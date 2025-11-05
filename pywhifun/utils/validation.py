"""
Validation utilities for PyWhiFuN
"""

import numpy as np
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