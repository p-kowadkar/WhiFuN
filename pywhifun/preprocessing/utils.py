"""
Preprocessing utility functions
"""

import os
import gzip
import shutil
import nibabel as nib
from pathlib import Path
from typing import Union


def discard_initial_volumes(input_path: str, output_path: str, n_volumes: int) -> str:
    """
    Discard initial volumes from 4D functional image.
    
    Parameters
    ----------
    input_path : str
        Path to input 4D image.
    output_path : str
        Path for output image.
    n_volumes : int
        Number of initial volumes to discard.
        
    Returns
    -------
    str
        Path to output image.
    """
    if n_volumes == 0:
        # Just copy the file
        shutil.copy2(input_path, output_path)
        return output_path
    
    # Load image
    img = nib.load(input_path)
    data = img.get_fdata()
    
    if data.ndim != 4:
        raise ValueError("Input must be a 4D functional image")
    
    # Discard initial volumes
    data_trimmed = data[:, :, :, n_volumes:]
    
    # Create new image
    trimmed_img = nib.Nifti1Image(data_trimmed, img.affine, img.header)
    
    # Save
    nib.save(trimmed_img, output_path)
    
    return output_path


def gunzip_files(file_path: str, file_type: str = 'functional') -> str:
    """
    Unzip .gz files if needed.
    
    Parameters
    ----------
    file_path : str
        Path to potentially gzipped file.
    file_type : str
        Type of file ('functional' or 'anatomical').
        
    Returns
    -------
    str
        Path to unzipped file.
    """
    if not file_path.endswith('.gz'):
        return file_path
    
    output_path = file_path[:-3]  # Remove .gz extension
    
    if os.path.exists(output_path):
        return output_path
    
    # Unzip file
    with gzip.open(file_path, 'rb') as f_in:
        with open(output_path, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)
    
    return output_path