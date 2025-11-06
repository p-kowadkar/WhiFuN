"""
Validation utilities for PyWhiFuN
"""

import os
import numpy as np
from pathlib import Path
from typing import Any, Dict, List, Union


def check_data(data: Any) -> bool:
    """
    Basic data validation.
    
    Parameters
    ----------
    data : Any
        Data to validate.
        
    Returns
    -------
    bool
        True if data is valid.
    """
    if data is None:
        return False
    
    if isinstance(data, np.ndarray):
        return not np.any(np.isnan(data))
    
    return True


def validate_parameters(params: Dict[str, Any]) -> bool:
    """
    Validate preprocessing parameters.
    
    Parameters
    ----------
    params : dict
        Parameters to validate.
        
    Returns
    -------
    bool
        True if parameters are valid.
    """
    # Basic validation - can be expanded
    return isinstance(params, dict)


def validate_file_path(file_path: Union[str, Path]) -> bool:
    """
    Validate that a file path exists.
    
    Parameters
    ----------
    file_path : str or Path
        File path to validate.
        
    Returns
    -------
    bool
        True if file exists.
    """
    return Path(file_path).exists()