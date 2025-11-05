"""
Preprocessing module for PyWhiFuN

This module contains all preprocessing functions for fMRI data,
including motion correction, segmentation, coregistration, 
normalization, filtering, and smoothing.
"""

from .core import WhiFuNPreprocessor
from .motion import realignment, calculate_fd, motion_qc
from .segmentation import segment_anatomical, skull_strip
from .coregistration import coregister_func_to_anat
from .normalization import normalize_to_mni
from .filtering import temporal_filter
from .smoothing import smooth_images, smooth_wm_gm_separately
from .nuisance import nuisance_regression, extract_csf_signal
from .utils import discard_initial_volumes, gunzip_files

__all__ = [
    'WhiFuNPreprocessor',
    'realignment',
    'calculate_fd', 
    'motion_qc',
    'segment_anatomical',
    'skull_strip',
    'coregister_func_to_anat',
    'normalize_to_mni',
    'temporal_filter',
    'smooth_images',
    'smooth_wm_gm_separately',
    'nuisance_regression',
    'extract_csf_signal',
    'discard_initial_volumes',
    'gunzip_files'
]