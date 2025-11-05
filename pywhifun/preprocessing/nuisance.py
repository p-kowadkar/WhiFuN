"""
Nuisance regression functions
"""

import numpy as np
from typing import List


def nuisance_regression(input_path: str, output_path: str, regressors: List[np.ndarray]) -> str:
    """
    Perform nuisance regression on functional data.
    
    Parameters
    ----------
    input_path : str
        Path to input functional image.
    output_path : str
        Path for output regressed image.
    regressors : list of np.ndarray
        List of regressor arrays.
        
    Returns
    -------
    str
        Path to regressed image.
    """
    # Placeholder implementation
    import shutil
    shutil.copy2(input_path, output_path)
    return output_path


def extract_csf_signal(input_path: str, csf_mask: str, threshold: float = 0.95, 
                      use_pca: bool = False, n_components: int = 5) -> np.ndarray:
    """
    Extract CSF signal for nuisance regression.
    
    Parameters
    ----------
    input_path : str
        Path to functional image.
    csf_mask : str
        Path to CSF mask.
    threshold : float
        Threshold for CSF mask.
    use_pca : bool
        Whether to use PCA for dimensionality reduction.
    n_components : int
        Number of PCA components.
        
    Returns
    -------
    np.ndarray
        CSF signal time series.
    """
    # Placeholder implementation
    return np.random.randn(100, n_components if use_pca else 1)