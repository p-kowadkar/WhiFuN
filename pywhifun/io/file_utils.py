"""
File utility functions for PyWhiFuN
"""

import os
import glob
import json
from pathlib import Path
from typing import Union, Dict, List, Optional


def complete_filepath(filepath: Union[str, Path]) -> str:
    """
    Complete and normalize a file path.
    
    Parameters
    ----------
    filepath : str or Path
        Input file path.
        
    Returns
    -------
    str
        Completed file path.
    """
    return str(Path(filepath).resolve())


def check_file_exists(filepath: Union[str, Path]) -> bool:
    """
    Check if a file exists.
    
    Parameters
    ----------
    filepath : str or Path
        File path to check.
        
    Returns
    -------
    bool
        True if file exists, False otherwise.
    """
    return Path(filepath).exists()


def create_directories(dirpath: Union[str, Path]) -> None:
    """
    Create directories if they don't exist.
    
    Parameters
    ----------
    dirpath : str or Path
        Directory path to create.
    """
    Path(dirpath).mkdir(parents=True, exist_ok=True)


def validate_data_structure(subject_folder: str, data_config: Dict) -> Dict:
    """
    Validate data structure and check for required files.
    
    Parameters
    ----------
    subject_folder : str
        Path to subject data folder
    data_config : dict
        Data structure configuration
        
    Returns
    -------
    results : dict
        Validation results with valid/invalid subjects and errors
    """
    results = {
        'valid_subjects': [],
        'invalid_subjects': [],
        'errors': []
    }
    
    subject_path = Path(subject_folder)
    if not subject_path.exists():
        results['errors'].append(f"Subject folder does not exist: {subject_folder}")
        return results
    
    # Get all subdirectories (potential subjects)
    subject_dirs = [d for d in subject_path.iterdir() if d.is_dir()]
    
    for subject_dir in subject_dirs:
        subject_name = subject_dir.name
        
        try:
            # Check if required files exist for this subject
            if data_config['is_bids']:
                # BIDS structure validation
                valid = validate_bids_subject(subject_dir)
            else:
                # Custom structure validation
                valid = validate_custom_subject(subject_dir, data_config)
            
            if valid:
                results['valid_subjects'].append(subject_name)
            else:
                results['invalid_subjects'].append(subject_name)
                
        except Exception as e:
            results['invalid_subjects'].append(subject_name)
            results['errors'].append(f"Error validating {subject_name}: {str(e)}")
    
    return results


def validate_bids_subject(subject_dir: Path) -> bool:
    """
    Validate BIDS subject structure.
    
    Parameters
    ----------
    subject_dir : Path
        Path to subject directory
        
    Returns
    -------
    valid : bool
        True if valid BIDS structure
    """
    # Check for required BIDS folders
    anat_dir = subject_dir / 'anat'
    func_dir = subject_dir / 'func'
    
    if not anat_dir.exists() or not func_dir.exists():
        return False
    
    # Check for T1w file
    t1w_files = list(anat_dir.glob('*T1w.nii*'))
    if not t1w_files:
        return False
    
    # Check for BOLD file
    bold_files = list(func_dir.glob('*bold.nii*'))
    if not bold_files:
        return False
    
    return True


def validate_custom_subject(subject_dir: Path, data_config: Dict) -> bool:
    """
    Validate custom subject structure.
    
    Parameters
    ----------
    subject_dir : Path
        Path to subject directory
    data_config : dict
        Data structure configuration
        
    Returns
    -------
    valid : bool
        True if valid custom structure
    """
    # Build paths based on configuration
    base_path = subject_dir
    
    if data_config['intermediate_folder']:
        base_path = base_path / data_config['intermediate_folder']
    
    # Check anatomical file
    anat_path = base_path / data_config['anat_folder_name']
    if not anat_path.exists():
        return False
    
    anat_pattern = data_config['anat_image_name'].replace('*', subject_dir.name)
    anat_files = list(anat_path.glob(anat_pattern))
    if not anat_files:
        # Try with wildcard
        anat_files = list(anat_path.glob(data_config['anat_image_name']))
        if not anat_files:
            return False
    
    # Check functional file
    func_path = base_path / data_config['func_folder_name']
    if not func_path.exists():
        return False
    
    func_pattern = data_config['func_image_name'].replace('*', subject_dir.name)
    func_files = list(func_path.glob(func_pattern))
    if not func_files:
        # Try with wildcard
        func_files = list(func_path.glob(data_config['func_image_name']))
        if not func_files:
            return False
    
    return True


def create_file_pattern(overwrite: bool, file_pattern: str) -> Optional[List]:
    """
    Create file pattern and check for existing files.
    
    Parameters
    ----------
    overwrite : bool
        Whether to overwrite existing files
    file_pattern : str
        File pattern to search for
        
    Returns
    -------
    files : list or None
        List of existing files or None if no files found
    """
    existing_files = glob.glob(file_pattern)
    
    if existing_files and not overwrite:
        return existing_files
    elif not existing_files:
        return None
    else:
        # Overwrite mode - return existing files for potential deletion
        return existing_files