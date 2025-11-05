"""
Spatial smoothing functions
"""


def smooth_images(input_path: str, output_path: str, fwhm: float = 4.0) -> str:
    """
    Apply spatial smoothing to functional data.
    
    Parameters
    ----------
    input_path : str
        Path to input functional image.
    output_path : str
        Path for output smoothed image.
    fwhm : float
        Full-width at half-maximum of smoothing kernel.
        
    Returns
    -------
    str
        Path to smoothed image.
    """
    # Placeholder implementation
    import shutil
    shutil.copy2(input_path, output_path)
    return output_path


def smooth_wm_gm_separately(input_path: str, output_path: str, wm_mask: str, gm_mask: str, fwhm: float = 4.0) -> str:
    """
    Apply spatial smoothing separately to WM and GM.
    
    Parameters
    ----------
    input_path : str
        Path to input functional image.
    output_path : str
        Path for output smoothed image.
    wm_mask : str
        Path to white matter mask.
    gm_mask : str
        Path to gray matter mask.
    fwhm : float
        Full-width at half-maximum of smoothing kernel.
        
    Returns
    -------
    str
        Path to smoothed image.
    """
    # Placeholder implementation
    import shutil
    shutil.copy2(input_path, output_path)
    return output_path