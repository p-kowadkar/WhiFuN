"""
Core preprocessing pipeline for PyWhiFuN

This module contains the main preprocessing class that orchestrates
the complete fMRI preprocessing pipeline, equivalent to whifun_preproc.m
"""

import os
import logging
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass, field
import numpy as np
from pathlib import Path

from ..io.nifti_io import nifti_read, nifti_write
from ..utils.validation import validate_parameters
from .motion import realignment, calculate_fd, motion_qc
from .segmentation import segment_anatomical, skull_strip
from .coregistration import coregister_func_to_anat
from .normalization import normalize_to_mni
from .filtering import temporal_filter
from .smoothing import smooth_images, smooth_wm_gm_separately
from .nuisance import nuisance_regression, extract_csf_signal
from .utils import discard_initial_volumes, gunzip_files


@dataclass
class SubjectData:
    """
    Data structure for subject information, equivalent to MATLAB Subj_list_1 struct.
    """
    name: str
    func_folder: str
    func_name: str
    anat_folder: str
    anat_name: str
    error: bool = False
    motion_ex: bool = False
    
    # Preprocessing paths (will be populated during processing)
    current_func_path: Optional[str] = None
    current_anat_path: Optional[str] = None
    motion_params_path: Optional[str] = None
    
    # Segmentation outputs
    gm_native_path: Optional[str] = None
    wm_native_path: Optional[str] = None
    csf_native_path: Optional[str] = None
    gm_mni_path: Optional[str] = None
    wm_mni_path: Optional[str] = None
    csf_mni_path: Optional[str] = None
    deformation_field_path: Optional[str] = None
    
    # Quality control metrics
    fd_stats: Dict[str, float] = field(default_factory=dict)
    
    def __post_init__(self):
        """Initialize paths"""
        if self.current_func_path is None:
            self.current_func_path = os.path.join(self.func_folder, self.func_name)
        if self.current_anat_path is None:
            self.current_anat_path = os.path.join(self.anat_folder, self.anat_name)


@dataclass
class PreprocessingParameters:
    """
    Parameters for preprocessing pipeline, equivalent to MATLAB inputParser results.
    """
    # General
    over_write: bool = False
    
    # Volume discarding
    cut_pre: str = 'c_'
    n_vol_dis: int = 0
    
    # Realignment
    realign_pre: str = 'r'
    
    # Framewise displacement thresholds
    max_fd: float = 0.5
    mean_fd: float = 0.2
    greater_than_20: float = 0.2
    
    # Skull stripping
    skull_pre: str = 'b'
    
    # CSF regression
    reg_csf: bool = False
    csf_thres: str = '0.95'
    pca_for_temp_reg: bool = False
    n_pca: int = 5
    
    # Nuisance regression
    reg_pre: str = 'REG_'
    motion_reg: bool = False
    
    # Filtering
    filter_check: bool = False
    f_pre: str = 'f'
    filter_lp: str = '0.01'
    filter_hp: str = '0.15'
    
    # Smoothing
    smooth_: bool = False
    smooth_pre: str = 's'
    wm_gm_separate: bool = True
    smooth_fwhm: float = 4.0
    
    # Normalization
    dartel_: bool = False
    norm_pre: str = 'w'
    vox: Union[float, List[float]] = 3.0
    
    def __post_init__(self):
        """Validate parameters after initialization"""
        if isinstance(self.vox, (int, float)):
            self.vox = [self.vox, self.vox, self.vox]


class WhiFuNPreprocessor:
    """
    Main preprocessing class for PyWhiFuN.
    
    This class orchestrates a comprehensive fMRI preprocessing pipeline,
    equivalent to the MATLAB whifun_preproc function.
    """
    
    def __init__(self, quality_control_path: str, **kwargs):
        """
        Initialize the preprocessor.
        
        Parameters
        ----------
        quality_control_path : str
            Path where quality control outputs will be saved.
        **kwargs
            Additional parameters for preprocessing (see PreprocessingParameters).
        """
        self.qc_path = Path(quality_control_path)
        self.qc_path.mkdir(parents=True, exist_ok=True)
        
        # Create logs directory
        self.logs_path = self.qc_path / 'logs'
        self.logs_path.mkdir(exist_ok=True)
        
        # Initialize parameters
        self.params = PreprocessingParameters(**kwargs)
        
        # Setup logging
        self.logger = self._setup_logging()
        
    def _setup_logging(self) -> logging.Logger:
        """Setup logging for the preprocessing pipeline."""
        logger = logging.getLogger('pywhifun_preproc')
        logger.setLevel(logging.INFO)
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Create console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        return logger
        
    def preprocess_subject(self, subject: SubjectData) -> SubjectData:
        """
        Run the complete preprocessing pipeline for a single subject.
        
        Parameters
        ----------
        subject : SubjectData
            Subject data structure containing paths and information.
            
        Returns
        -------
        subject : SubjectData
            Updated subject data structure with processing results.
        """
        self.logger.info(f"Starting preprocessing for subject: {subject.name}")
        
        # Setup subject-specific logging
        log_file = self.logs_path / f"{subject.name}_log_info.txt"
        file_handler = logging.FileHandler(log_file, mode='a')
        file_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
        self.logger.addHandler(file_handler)
        
        try:
            # Step 1: Unzip files
            subject = self._step_unzip(subject)
            if subject.error:
                return subject
                
            # Step 2: Discard initial volumes
            subject = self._step_discard_volumes(subject)
            if subject.error:
                return subject
                
            # Step 3: Realignment (motion correction)
            subject = self._step_realignment(subject)
            if subject.error:
                return subject
                
            # Step 4: Framewise displacement QC
            subject = self._step_fd_qc(subject)
            if subject.motion_ex:
                return subject
                
            # Step 5: Segmentation
            subject = self._step_segmentation(subject)
            if subject.error:
                return subject
                
            # Step 6: Skull stripping
            subject = self._step_skull_strip(subject)
            if subject.error:
                return subject
                
            # Step 7: Coregistration
            subject = self._step_coregistration(subject)
            if subject.error:
                return subject
                
            # Step 8: Nuisance regression (optional)
            if self.params.reg_csf or self.params.motion_reg:
                subject = self._step_nuisance_regression(subject)
                if subject.error:
                    return subject
                    
            # Step 9: Filtering (optional)
            if self.params.filter_check:
                subject = self._step_filtering(subject)
                if subject.error:
                    return subject
                    
            # Step 10: Smoothing (optional)
            if self.params.smooth_:
                subject = self._step_smoothing(subject)
                if subject.error:
                    return subject
                    
            # Step 11: Normalization (optional, skip if DARTEL)
            if not self.params.dartel_:
                subject = self._step_normalization(subject)
                if subject.error:
                    return subject
                    
            self.logger.info(f"Preprocessing completed successfully for {subject.name}")
            
        except Exception as e:
            self.logger.error(f"Error during preprocessing of {subject.name}: {str(e)}")
            subject.error = True
            
        finally:
            # Remove file handler
            self.logger.removeHandler(file_handler)
            file_handler.close()
            
        return subject
        
    def _step_unzip(self, subject: SubjectData) -> SubjectData:
        """Step 1: Unzip functional and anatomical files."""
        self.logger.info("Step 1: Unzipping files")
        
        try:
            # Unzip functional data
            subject.current_func_path = gunzip_files(
                subject.current_func_path, 'functional'
            )
            
            # Unzip anatomical data  
            subject.current_anat_path = gunzip_files(
                subject.current_anat_path, 'anatomical'
            )
            
        except Exception as e:
            self.logger.error(f"Error in unzipping: {str(e)}")
            subject.error = True
            
        return subject
        
    def _step_discard_volumes(self, subject: SubjectData) -> SubjectData:
        """Step 2: Discard initial volumes."""
        if self.params.n_vol_dis == 0:
            return subject
            
        self.logger.info(f"Step 2: Discarding {self.params.n_vol_dis} initial volumes")
        
        try:
            input_path = subject.current_func_path
            output_path = self._get_output_path(input_path, self.params.cut_pre)
            
            if not self._should_process(output_path):
                subject.current_func_path = output_path
                return subject
                
            subject.current_func_path = discard_initial_volumes(
                input_path, output_path, self.params.n_vol_dis
            )
            
        except Exception as e:
            self.logger.error(f"Error in discarding volumes: {str(e)}")
            subject.error = True
            
        return subject
        
    def _step_realignment(self, subject: SubjectData) -> SubjectData:
        """Step 3: Realignment (motion correction)."""
        self.logger.info("Step 3: Realignment")
        
        try:
            input_path = subject.current_func_path
            output_path = self._get_output_path(input_path, self.params.realign_pre)
            
            if not self._should_process(output_path):
                subject.current_func_path = output_path
                # Find motion parameters file
                motion_file = output_path.replace('.nii', '_motion.txt')
                if os.path.exists(motion_file):
                    subject.motion_params_path = motion_file
                return subject
                
            subject.current_func_path, subject.motion_params_path = realignment(
                input_path, output_path, self.qc_path
            )
            
        except Exception as e:
            self.logger.error(f"Error in realignment: {str(e)}")
            subject.error = True
            
        return subject
        
    def _step_fd_qc(self, subject: SubjectData) -> SubjectData:
        """Step 4: Framewise displacement quality control."""
        self.logger.info("Step 4: Framewise displacement QC")
        
        try:
            if subject.motion_params_path is None:
                raise ValueError("Motion parameters not found")
                
            fd_stats = motion_qc(
                subject.motion_params_path,
                max_fd=self.params.max_fd,
                mean_fd=self.params.mean_fd,
                threshold_pct=self.params.greater_than_20
            )
            
            subject.fd_stats = fd_stats
            
            # Check if subject should be excluded
            if (fd_stats['max_fd'] > self.params.max_fd or 
                fd_stats['mean_fd'] > self.params.mean_fd or
                fd_stats['pct_above_threshold'] > self.params.greater_than_20):
                
                self.logger.warning(f"Subject {subject.name} excluded due to excessive motion")
                subject.motion_ex = True
                
        except Exception as e:
            self.logger.error(f"Error in FD QC: {str(e)}")
            subject.error = True
            
        return subject
        
    def _step_segmentation(self, subject: SubjectData) -> SubjectData:
        """Step 5: Anatomical segmentation."""
        self.logger.info("Step 5: Segmentation")
        
        try:
            input_path = subject.current_anat_path
            
            # Check if segmentation already exists
            gm_path = input_path.replace('.nii', '_seg_GM.nii')
            if not self._should_process(gm_path):
                # Load existing segmentation paths
                subject.gm_native_path = gm_path
                subject.wm_native_path = input_path.replace('.nii', '_seg_WM.nii')
                subject.csf_native_path = input_path.replace('.nii', '_seg_CSF.nii')
                subject.deformation_field_path = input_path.replace('.nii', '_deformation.nii')
                return subject
                
            seg_results = segment_anatomical(input_path, self.qc_path)
            
            subject.gm_native_path = seg_results['gm_native']
            subject.wm_native_path = seg_results['wm_native'] 
            subject.csf_native_path = seg_results['csf_native']
            subject.gm_mni_path = seg_results['gm_mni']
            subject.wm_mni_path = seg_results['wm_mni']
            subject.csf_mni_path = seg_results['csf_mni']
            subject.deformation_field_path = seg_results['deformation_field']
            
        except Exception as e:
            self.logger.error(f"Error in segmentation: {str(e)}")
            subject.error = True
            
        return subject
        
    def _step_skull_strip(self, subject: SubjectData) -> SubjectData:
        """Step 6: Skull stripping."""
        self.logger.info("Step 6: Skull stripping")
        
        try:
            input_path = subject.current_anat_path
            output_path = self._get_output_path(input_path, self.params.skull_pre)
            
            if not self._should_process(output_path):
                subject.current_anat_path = output_path
                return subject
                
            subject.current_anat_path = skull_strip(
                input_path, output_path,
                subject.gm_native_path,
                subject.wm_native_path,
                subject.csf_native_path
            )
            
        except Exception as e:
            self.logger.error(f"Error in skull stripping: {str(e)}")
            subject.error = True
            
        return subject
        
    def _step_coregistration(self, subject: SubjectData) -> SubjectData:
        """Step 7: Coregistration of functional to anatomical."""
        self.logger.info("Step 7: Coregistration")
        
        try:
            func_input = subject.current_func_path
            anat_input = subject.current_anat_path
            
            # Output path for coregistered functional
            output_path = self._get_output_path(func_input, 'coreg_')
            
            if not self._should_process(output_path):
                subject.current_func_path = output_path
                return subject
                
            subject.current_func_path = coregister_func_to_anat(
                func_input, anat_input, output_path, self.qc_path
            )
            
        except Exception as e:
            self.logger.error(f"Error in coregistration: {str(e)}")
            subject.error = True
            
        return subject
        
    def _step_nuisance_regression(self, subject: SubjectData) -> SubjectData:
        """Step 8: Nuisance regression."""
        self.logger.info("Step 8: Nuisance regression")
        
        try:
            input_path = subject.current_func_path
            output_path = self._get_output_path(input_path, self.params.reg_pre)
            
            if not self._should_process(output_path):
                subject.current_func_path = output_path
                return subject
                
            # Prepare regressors
            regressors = []
            
            if self.params.reg_csf and subject.csf_native_path:
                csf_signal = extract_csf_signal(
                    input_path, subject.csf_native_path,
                    threshold=float(self.params.csf_thres),
                    use_pca=self.params.pca_for_temp_reg,
                    n_components=self.params.n_pca
                )
                regressors.append(csf_signal)
                
            if self.params.motion_reg and subject.motion_params_path:
                motion_params = np.loadtxt(subject.motion_params_path)
                regressors.append(motion_params)
                
            if regressors:
                subject.current_func_path = nuisance_regression(
                    input_path, output_path, regressors
                )
            
        except Exception as e:
            self.logger.error(f"Error in nuisance regression: {str(e)}")
            subject.error = True
            
        return subject
        
    def _step_filtering(self, subject: SubjectData) -> SubjectData:
        """Step 9: Temporal filtering."""
        self.logger.info("Step 9: Temporal filtering")
        
        try:
            input_path = subject.current_func_path
            output_path = self._get_output_path(input_path, self.params.f_pre)
            
            if not self._should_process(output_path):
                subject.current_func_path = output_path
                return subject
                
            subject.current_func_path = temporal_filter(
                input_path, output_path,
                low_pass=float(self.params.filter_lp),
                high_pass=float(self.params.filter_hp)
            )
            
        except Exception as e:
            self.logger.error(f"Error in filtering: {str(e)}")
            subject.error = True
            
        return subject
        
    def _step_smoothing(self, subject: SubjectData) -> SubjectData:
        """Step 10: Spatial smoothing."""
        self.logger.info("Step 10: Smoothing")
        
        try:
            input_path = subject.current_func_path
            output_path = self._get_output_path(input_path, self.params.smooth_pre)
            
            if not self._should_process(output_path):
                subject.current_func_path = output_path
                return subject
                
            if self.params.wm_gm_separate:
                subject.current_func_path = smooth_wm_gm_separately(
                    input_path, output_path,
                    subject.wm_native_path, subject.gm_native_path,
                    fwhm=self.params.smooth_fwhm
                )
            else:
                subject.current_func_path = smooth_images(
                    input_path, output_path, fwhm=self.params.smooth_fwhm
                )
                
        except Exception as e:
            self.logger.error(f"Error in smoothing: {str(e)}")
            subject.error = True
            
        return subject
        
    def _step_normalization(self, subject: SubjectData) -> SubjectData:
        """Step 11: Normalization to MNI space."""
        self.logger.info("Step 11: Normalization")
        
        try:
            input_path = subject.current_func_path
            output_path = self._get_output_path(input_path, self.params.norm_pre)
            
            if not self._should_process(output_path):
                subject.current_func_path = output_path
                return subject
                
            if subject.deformation_field_path is None:
                raise ValueError("Deformation field not found")
                
            subject.current_func_path = normalize_to_mni(
                input_path, output_path,
                subject.deformation_field_path,
                voxel_size=self.params.vox
            )
            
        except Exception as e:
            self.logger.error(f"Error in normalization: {str(e)}")
            subject.error = True
            
        return subject
        
    def _get_output_path(self, input_path: str, prefix: str) -> str:
        """Generate output path with prefix."""
        path_obj = Path(input_path)
        return str(path_obj.parent / f"{prefix}{path_obj.name}")
        
    def _should_process(self, output_path: str) -> bool:
        """Check if processing should be done based on overwrite flag."""
        if self.params.over_write:
            return True
        return not os.path.exists(output_path)