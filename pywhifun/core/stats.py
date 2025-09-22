import numpy as np
from numpy.typing import ArrayLike
from typing import Union

def fisher_z(r: ArrayLike) -> Union[np.ndarray, float]:
    """
    Performs the Fisher Z-transform on a correlation coefficient or array of coefficients.

    This function is a direct equivalent of the MATLAB `fisherZ` function.
    The Fisher Z-transform is used to stabilize the variance of correlation
    coefficients. The formula is Z = 0.5 * log((1+r)/(1-r)), which is
    equivalent to the inverse hyperbolic tangent (arctanh).

    Args:
        r: A scalar or numpy array of correlation coefficients.
           Values must be in the range [-1, 1].

    Returns:
        The transformed Z-score(s). Returns a float if the input is a scalar,
        or a numpy array if the input is an array.
    """
    return np.arctanh(r)
