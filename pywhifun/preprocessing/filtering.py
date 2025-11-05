"""
Temporal filtering functions
"""


def temporal_filter(input_path: str, output_path: str, low_pass: float = 0.01, high_pass: float = 0.15) -> str:
    """
    Apply temporal filtering to functional data.
    
    Parameters
    ----------
    input_path : str
        Path to input functional image.
    output_path : str
        Path for output filtered image.
    low_pass : float
        Low-pass filter cutoff frequency.
    high_pass : float
        High-pass filter cutoff frequency.
        
    Returns
    -------
    str
        Path to filtered image.
    """
    # Placeholder implementation
    import shutil
    shutil.copy2(input_path, output_path)
    return output_path