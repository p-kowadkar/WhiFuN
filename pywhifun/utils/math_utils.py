"""
Mathematical utility functions for PyWhiFuN

This module contains mathematical functions used throughout the toolbox,
including correlation analysis, statistical transformations, and other
mathematical operations.
"""

import numpy as np
from scipy import stats
from scipy.stats import pearsonr
from typing import Union, Tuple, Optional
import warnings


def fisher_z(r: Union[float, np.ndarray]) -> Union[float, np.ndarray]:
    """
    Apply Fisher's r-to-z transformation to correlation coefficients.
    
    The Fisher transformation (often called Fisher's Z-transformation) is used
    to transform the sampling distribution of the Pearson correlation coefficient
    (r) from a non-normal (skewed) distribution to a distribution that is
    approximately normal. This makes the transformed variable Z more suitable
    for statistical inference, such as calculating confidence intervals or
    performing hypothesis tests on correlation coefficients.
    
    The formula for the transformation is:
        Z = 0.5 * ln((1+r)/(1-r))
    
    Parameters
    ----------
    r : float or np.ndarray
        The Pearson correlation coefficient(s) (or any value between -1 and 1).
        Can be a scalar, vector, or matrix.
        
    Returns
    -------
    Z : float or np.ndarray
        The Fisher's Z-transformed value(s). The output has the same shape as r.
        
    Notes
    -----
    The input r must be in the range (-1, 1). Values of r = -1 or r = 1
    will result in Z = -Inf or Z = Inf, respectively.
    
    Examples
    --------
    >>> z = fisher_z(0.5)
    >>> print(f"Fisher Z for r=0.5: {z:.3f}")
    
    >>> r_values = np.array([0.1, 0.5, 0.8])
    >>> z_values = fisher_z(r_values)
    >>> print(f"Fisher Z values: {z_values}")
    """
    r = np.asarray(r)
    
    # Check for values at the boundaries
    if np.any(np.abs(r) >= 1.0):
        warnings.warn("Correlation values at or beyond [-1, 1] will produce infinite Z values")
    
    # Apply Fisher transformation
    z = 0.5 * (np.log(1 + r) - np.log(1 - r))
    
    return z if r.ndim > 0 else float(z)


def inverse_fisher_z(z: Union[float, np.ndarray]) -> Union[float, np.ndarray]:
    """
    Apply inverse Fisher's z-to-r transformation.
    
    Parameters
    ----------
    z : float or np.ndarray
        Fisher's Z-transformed values.
        
    Returns
    -------
    r : float or np.ndarray
        Correlation coefficients.
    """
    z = np.asarray(z)
    r = np.tanh(z)
    return r if z.ndim > 0 else float(r)


def functional_connectivity(ts1: np.ndarray, 
                          ts2: Optional[np.ndarray] = None,
                          method: str = 'pearson') -> Union[float, np.ndarray]:
    """
    Calculate functional connectivity between time series.
    
    Parameters
    ----------
    ts1 : np.ndarray
        First time series or matrix of time series (time x regions).
    ts2 : np.ndarray, optional
        Second time series. If None, calculates connectivity matrix for ts1.
    method : str, default 'pearson'
        Correlation method ('pearson', 'spearman', 'kendall').
        
    Returns
    -------
    connectivity : float or np.ndarray
        Correlation coefficient(s).
    """
    if ts2 is None:
        # Calculate connectivity matrix
        if ts1.ndim == 1:
            raise ValueError("For connectivity matrix, ts1 must be 2D (time x regions)")
        return np.corrcoef(ts1.T)
    else:
        # Calculate correlation between two time series
        if method == 'pearson':
            corr, _ = pearsonr(ts1.flatten(), ts2.flatten())
        elif method == 'spearman':
            corr, _ = stats.spearmanr(ts1.flatten(), ts2.flatten())
        elif method == 'kendall':
            corr, _ = stats.kendalltau(ts1.flatten(), ts2.flatten())
        else:
            raise ValueError(f"Unknown correlation method: {method}")
        
        return corr


def partial_correlation(data: np.ndarray, 
                       x_idx: int, 
                       y_idx: int, 
                       control_idx: Union[int, list]) -> float:
    """
    Calculate partial correlation between two variables controlling for others.
    
    Parameters
    ----------
    data : np.ndarray
        Data matrix (observations x variables).
    x_idx : int
        Index of first variable.
    y_idx : int
        Index of second variable.
    control_idx : int or list
        Index(es) of control variable(s).
        
    Returns
    -------
    partial_corr : float
        Partial correlation coefficient.
    """
    if isinstance(control_idx, int):
        control_idx = [control_idx]
    
    # Extract variables
    x = data[:, x_idx]
    y = data[:, y_idx]
    controls = data[:, control_idx]
    
    # Regress out control variables
    from sklearn.linear_model import LinearRegression
    
    reg_x = LinearRegression().fit(controls, x)
    reg_y = LinearRegression().fit(controls, y)
    
    x_residual = x - reg_x.predict(controls)
    y_residual = y - reg_y.predict(controls)
    
    # Calculate correlation of residuals
    partial_corr, _ = pearsonr(x_residual, y_residual)
    
    return partial_corr


def veccorr(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    """
    Vectorized correlation calculation between columns of two matrices.
    
    Equivalent to MATLAB's veccorr function.
    
    Parameters
    ----------
    x : np.ndarray
        First matrix (observations x variables).
    y : np.ndarray
        Second matrix (observations x variables).
        
    Returns
    -------
    correlations : np.ndarray
        Vector of correlations between corresponding columns.
    """
    if x.shape != y.shape:
        raise ValueError("Input matrices must have the same shape")
    
    # Center the data
    x_centered = x - np.mean(x, axis=0)
    y_centered = y - np.mean(y, axis=0)
    
    # Calculate correlations
    numerator = np.sum(x_centered * y_centered, axis=0)
    denominator = np.sqrt(np.sum(x_centered**2, axis=0) * np.sum(y_centered**2, axis=0))
    
    # Avoid division by zero
    correlations = np.divide(numerator, denominator, 
                           out=np.zeros_like(numerator), 
                           where=denominator!=0)
    
    return correlations


def corrvec(matrix: np.ndarray) -> np.ndarray:
    """
    Convert correlation matrix to vector form (upper triangle).
    
    Equivalent to MATLAB's corrvec function.
    
    Parameters
    ----------
    matrix : np.ndarray
        Square correlation matrix.
        
    Returns
    -------
    vector : np.ndarray
        Upper triangle of matrix as vector.
    """
    if matrix.ndim != 2 or matrix.shape[0] != matrix.shape[1]:
        raise ValueError("Input must be a square matrix")
    
    # Get upper triangle indices (excluding diagonal)
    triu_indices = np.triu_indices(matrix.shape[0], k=1)
    
    return matrix[triu_indices]


def fd_calc(motion_params: np.ndarray, radius: float = 50.0) -> np.ndarray:
    """
    Calculate framewise displacement from motion parameters.
    
    Parameters
    ----------
    motion_params : np.ndarray
        Motion parameters (timepoints x 6) - 3 translations + 3 rotations.
    radius : float, default 50.0
        Radius for converting rotations to displacements (mm).
        
    Returns
    -------
    fd : np.ndarray
        Framewise displacement values.
    """
    if motion_params.shape[1] != 6:
        raise ValueError("Motion parameters must have 6 columns (3 trans + 3 rot)")
    
    # Calculate derivatives
    motion_diff = np.diff(motion_params, axis=0)
    
    # Convert rotations to mm (multiply by radius)
    motion_diff[:, 3:] *= radius
    
    # Calculate framewise displacement
    fd = np.sum(np.abs(motion_diff), axis=1)
    
    # Prepend zero for first timepoint
    fd = np.concatenate([[0], fd])
    
    return fd


def dice_coefficient(mask1: np.ndarray, mask2: np.ndarray) -> float:
    """
    Calculate Dice coefficient between two binary masks.
    
    Parameters
    ----------
    mask1, mask2 : np.ndarray
        Binary masks.
        
    Returns
    -------
    dice : float
        Dice coefficient (0-1).
    """
    mask1 = mask1.astype(bool)
    mask2 = mask2.astype(bool)
    
    intersection = np.sum(mask1 & mask2)
    total = np.sum(mask1) + np.sum(mask2)
    
    if total == 0:
        return 1.0  # Both masks are empty
    
    return 2.0 * intersection / total


def identification_rate(fc_matrices: np.ndarray, 
                       target_matrix: np.ndarray) -> float:
    """
    Calculate identification rate for functional connectivity fingerprinting.
    
    Parameters
    ----------
    fc_matrices : np.ndarray
        Stack of FC matrices (subjects x regions x regions).
    target_matrix : np.ndarray
        Target FC matrix to identify.
        
    Returns
    -------
    id_rate : float
        Identification rate (0-1).
    """
    n_subjects = fc_matrices.shape[0]
    
    # Calculate correlations with target
    correlations = np.zeros(n_subjects)
    target_vec = corrvec(target_matrix)
    
    for i in range(n_subjects):
        fc_vec = corrvec(fc_matrices[i])
        correlations[i] = np.corrcoef(target_vec, fc_vec)[0, 1]
    
    # Check if target has highest correlation with itself
    max_idx = np.argmax(correlations)
    
    return 1.0 if max_idx == 0 else 0.0