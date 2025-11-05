"""
Spatial normalization functions
"""

from typing import List, Union


def normalize_to_mni(input_path: str, output_path: str, deformation_field: str, 
                     voxel_size: Union[float, List[float]] = 3.0) -> str:
    """
    Normalize image to MNI space.
    
    Parameters
    ----------
    input_path : str
        Path to input image.
    output_path : str
        Path for output normalized image.
    deformation_field : str
        Path to deformation field.
    voxel_size : float or list
        Target voxel size.
        
    Returns
    -------
    str
        Path to normalized image.
    """
    # Placeholder implementation
    import shutil
    shutil.copy2(input_path, output_path)
    return output_path