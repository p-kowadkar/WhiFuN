"""
Image coregistration functions
"""


def coregister_func_to_anat(func_path: str, anat_path: str, output_path: str, qc_path: str) -> str:
    """
    Coregister functional image to anatomical image.
    
    Parameters
    ----------
    func_path : str
        Path to functional image.
    anat_path : str
        Path to anatomical image.
    output_path : str
        Path for output coregistered image.
    qc_path : str
        Path for quality control outputs.
        
    Returns
    -------
    str
        Path to coregistered functional image.
    """
    # Placeholder implementation
    import shutil
    shutil.copy2(func_path, output_path)
    return output_path