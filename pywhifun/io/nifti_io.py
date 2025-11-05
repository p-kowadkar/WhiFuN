"""
NIfTI file I/O utilities for PyWhiFuN

This module provides functions for reading and writing NIfTI files with proper
scaling factor handling, equivalent to the MATLAB whifun_niftiread function.
"""

import numpy as np
import nibabel as nib
from typing import Tuple, Union, Optional
import os


def nifti_read(image_path: str) -> Tuple[np.ndarray, nib.Nifti1Header]:
    """
    Read a NIfTI file and apply scaling factors.
    
    This function reads a NIfTI file, correctly applying the stored scaling 
    and offset values from the file's header. This is crucial for ensuring 
    that voxel intensity values are interpreted correctly, as many NIfTI files 
    store data as integers to save space and require a scaling factor to be 
    applied for the correct floating-point representation.
    
    The function applies the formula: y = AdditiveOffset + x * MultiplicativeScaling,
    where x is the raw data and y is the corrected data.
    
    Parameters
    ----------
    image_path : str
        The full path to the NIfTI file to be read.
        
    Returns
    -------
    volume : np.ndarray
        A numeric array containing the corrected voxel data.
    info : nibabel.Nifti1Header
        Header information of the NIfTI file.
        
    Raises
    ------
    FileNotFoundError
        If the specified file does not exist.
    ValueError
        If the file is not a valid NIfTI file.
        
    Examples
    --------
    >>> volume, header = nifti_read('/path/to/image.nii')
    >>> print(f"Image shape: {volume.shape}")
    >>> print(f"Voxel size: {header.get_zooms()}")
    """
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"File not found: {image_path}")
    
    try:
        # Load the NIfTI image
        img = nib.load(image_path)
        
        # Get the data and header
        volume = img.get_fdata(dtype=np.float64)
        header = img.header
        
        # Apply scaling if present (nibabel usually handles this automatically,
        # but we'll be explicit to match MATLAB behavior)
        scl_slope = header.get('scl_slope', 1.0)
        scl_inter = header.get('scl_inter', 0.0)
        
        if scl_slope != 0:
            volume = scl_inter + volume * scl_slope
        else:
            # If slope is 0, set it to 1 (as in MATLAB version)
            header['scl_slope'] = 1.0
            
        return volume, header
        
    except Exception as e:
        raise ValueError(f"Error reading NIfTI file {image_path}: {str(e)}")


def nifti_write(volume: np.ndarray, 
                output_path: str, 
                reference_header: Optional[nib.Nifti1Header] = None,
                affine: Optional[np.ndarray] = None) -> None:
    """
    Write a volume to a NIfTI file.
    
    Parameters
    ----------
    volume : np.ndarray
        The volume data to write.
    output_path : str
        Path where the NIfTI file will be saved.
    reference_header : nibabel.Nifti1Header, optional
        Reference header to use for the output file.
    affine : np.ndarray, optional
        Affine transformation matrix. If None and reference_header is provided,
        uses the affine from the reference header.
        
    Raises
    ------
    ValueError
        If neither reference_header nor affine is provided.
    """
    if reference_header is not None:
        # Use reference header's affine if no affine provided
        if affine is None:
            # Create a new image object from the reference
            ref_img = nib.Nifti1Image(np.zeros(reference_header.get_data_shape()[:3]), 
                                    None, reference_header)
            affine = ref_img.affine
        
        # Create new image with reference header
        new_header = reference_header.copy()
        new_header.set_data_shape(volume.shape)
        img = nib.Nifti1Image(volume, affine, new_header)
        
    elif affine is not None:
        # Create image with provided affine
        img = nib.Nifti1Image(volume, affine)
        
    else:
        raise ValueError("Either reference_header or affine must be provided")
    
    # Save the image
    nib.save(img, output_path)


def nifti_info(image_path: str) -> nib.Nifti1Header:
    """
    Get header information from a NIfTI file without loading the data.
    
    Parameters
    ----------
    image_path : str
        Path to the NIfTI file.
        
    Returns
    -------
    header : nibabel.Nifti1Header
        Header information of the NIfTI file.
    """
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"File not found: {image_path}")
    
    img = nib.load(image_path)
    return img.header


def get_nifti_shape(image_path: str) -> Tuple[int, ...]:
    """
    Get the shape of a NIfTI file without loading the data.
    
    Parameters
    ----------
    image_path : str
        Path to the NIfTI file.
        
    Returns
    -------
    shape : tuple
        Shape of the image data.
    """
    header = nifti_info(image_path)
    return header.get_data_shape()


def get_nifti_affine(image_path: str) -> np.ndarray:
    """
    Get the affine transformation matrix from a NIfTI file.
    
    Parameters
    ----------
    image_path : str
        Path to the NIfTI file.
        
    Returns
    -------
    affine : np.ndarray
        4x4 affine transformation matrix.
    """
    img = nib.load(image_path)
    return img.affine