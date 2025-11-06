"""
Functional Connectivity Analysis Functions

Converted from MATLAB WhiFuN functional connectivity functions.
"""

import numpy as np
from scipy.stats import pearsonr
from scipy.spatial.distance import pdist, squareform
from ..utils.math_utils import fisher_z, corrvec
import warnings


def functional_connectivity(reg_ts, z_transform=False, window_size=None, stride=1, nonlinear=False):
    """
    Calculate Functional Connectivity (FC) from averaged ROI time series.
    
    Computes static or dynamic functional connectivity matrices (Pearson
    correlation or Non-linear Xi correlation) and returns the unique
    upper-triangle elements as a vector.
    
    Parameters
    ----------
    reg_ts : ndarray
        Time series of the ROIs. Shape: (T, ROI, Subjects)
        T = time points, ROI = number of ROIs, Subjects = number of subjects
    z_transform : bool, optional
        Apply Fisher Z-transformation to Pearson correlation results (default: False)
    window_size : int, optional
        Window size for Dynamic Functional Connectivity (DFC).
        If None, uses full time series for static FC (default: None)
    stride : int, optional
        Stride (step size) for sliding window in DFC (default: 1)
    nonlinear : bool, optional
        Use Non-linear Xi correlation instead of Pearson correlation (default: False)
        
    Returns
    -------
    vec : ndarray
        The vectorized upper-triangle of the FC matrices.
        - Static FC: (ROI*(ROI-1)/2, N_Subjects)
        - Dynamic FC: (ROI*(ROI-1)/2, N_Windows, N_Subjects)
    nan_subjects : list
        Subject indices with NaN values in FC matrices
        
    Notes
    -----
    Converted from MATLAB functional_connectivity.m
    """
    nan_subjects = []
    T, ROI, n_subjects = reg_ts.shape
    
    if window_size is None:
        window_size = T
        
    # Initialize correlation matrix
    cor = np.zeros((ROI, ROI))
    
    # Print processing message
    transform_msg = "With Fisher Z transform" if z_transform else ""
    fc_type = "Static" if window_size == T else "Dynamic"
    print(f"Creating {fc_type} map {transform_msg}")
    
    if not nonlinear:
        # Pearson correlation approach
        vec_list = []
        
        for s in range(n_subjects):
            subject_vecs = []
            
            # Sliding window approach
            for i1 in range(0, T - window_size + 1, stride):
                # Extract window data
                window_data = reg_ts[i1:i1 + window_size, :, s]
                
                # Calculate correlation matrix
                cor = np.corrcoef(window_data.T)
                
                # Check for NaN values
                if np.any(np.isnan(cor)):
                    print(f"NaN detected in subject {s+1}")
                    if s not in nan_subjects:
                        nan_subjects.append(s)
                
                # Apply Fisher Z-transformation if requested
                if z_transform:
                    cor = fisher_z(cor)
                
                # Extract upper triangle vector
                vec_window = corrvec(cor)
                subject_vecs.append(vec_window)
            
            vec_list.append(np.array(subject_vecs).T)
        
        # Convert to numpy array
        vec = np.array(vec_list)
        if window_size == T:
            # Static FC: squeeze out window dimension
            vec = vec.squeeze(axis=1).T
        else:
            # Dynamic FC: (features, windows, subjects)
            vec = np.transpose(vec, (1, 2, 0))
            
    else:
        # Non-linear correlation approach (placeholder - requires xicor implementation)
        warnings.warn("Non-linear correlation not yet implemented. Using Pearson correlation.")
        return functional_connectivity(reg_ts, z_transform, window_size, stride, nonlinear=False)
    
    return vec, nan_subjects


def partial_correlation(reg_ts, z_transform=False):
    """
    Calculate partial correlation matrix from time series.
    
    Parameters
    ----------
    reg_ts : ndarray
        Time series data. Shape: (T, ROI, Subjects)
    z_transform : bool, optional
        Apply Fisher Z-transformation (default: False)
        
    Returns
    -------
    partial_corr : ndarray
        Partial correlation matrices
    """
    from sklearn.covariance import GraphicalLassoCV
    
    T, ROI, n_subjects = reg_ts.shape
    partial_corr = np.zeros((ROI, ROI, n_subjects))
    
    for s in range(n_subjects):
        # Use GraphicalLasso for partial correlation estimation
        model = GraphicalLassoCV()
        model.fit(reg_ts[:, :, s])
        
        # Convert precision matrix to partial correlation
        precision = model.precision_
        partial_corr[:, :, s] = -precision / np.sqrt(np.outer(np.diag(precision), np.diag(precision)))
        np.fill_diagonal(partial_corr[:, :, s], 1.0)
        
        if z_transform:
            partial_corr[:, :, s] = fisher_z(partial_corr[:, :, s])
    
    return partial_corr


def dynamic_connectivity(reg_ts, window_size, stride=1, z_transform=False):
    """
    Calculate dynamic functional connectivity using sliding window approach.
    
    Parameters
    ----------
    reg_ts : ndarray
        Time series data. Shape: (T, ROI, Subjects)
    window_size : int
        Size of sliding window
    stride : int, optional
        Step size for sliding window (default: 1)
    z_transform : bool, optional
        Apply Fisher Z-transformation (default: False)
        
    Returns
    -------
    dfc : ndarray
        Dynamic functional connectivity matrices
    """
    return functional_connectivity(reg_ts, z_transform, window_size, stride)


def instantaneous_correlation(reg_ts, seed_region=None):
    """
    Calculate instantaneous correlation (seed-based connectivity).
    
    Parameters
    ----------
    reg_ts : ndarray
        Time series data. Shape: (T, ROI, Subjects)
    seed_region : int, optional
        Index of seed region. If None, calculates for all regions
        
    Returns
    -------
    instacorr : ndarray
        Instantaneous correlation maps
    """
    T, ROI, n_subjects = reg_ts.shape
    
    if seed_region is not None:
        # Single seed region
        instacorr = np.zeros((ROI, n_subjects))
        for s in range(n_subjects):
            seed_ts = reg_ts[:, seed_region, s]
            for roi in range(ROI):
                instacorr[roi, s] = np.corrcoef(seed_ts, reg_ts[:, roi, s])[0, 1]
    else:
        # All regions as seeds
        instacorr = np.zeros((ROI, ROI, n_subjects))
        for s in range(n_subjects):
            instacorr[:, :, s] = np.corrcoef(reg_ts[:, :, s].T)
    
    return instacorr


def connectivity_strength(connectivity_matrix):
    """
    Calculate connectivity strength for each node.
    
    Parameters
    ----------
    connectivity_matrix : ndarray
        Connectivity matrix
        
    Returns
    -------
    strength : ndarray
        Node strength values
    """
    # Remove diagonal (self-connections)
    conn_no_diag = connectivity_matrix.copy()
    np.fill_diagonal(conn_no_diag, 0)
    
    # Calculate strength as sum of absolute connections
    strength = np.sum(np.abs(conn_no_diag), axis=1)
    
    return strength


def connectivity_density(connectivity_matrix, threshold=0.0):
    """
    Calculate connectivity density (proportion of non-zero connections).
    
    Parameters
    ----------
    connectivity_matrix : ndarray
        Connectivity matrix
    threshold : float, optional
        Threshold for considering connections (default: 0.0)
        
    Returns
    -------
    density : float
        Connectivity density
    """
    # Remove diagonal
    conn_no_diag = connectivity_matrix.copy()
    np.fill_diagonal(conn_no_diag, 0)
    
    # Count connections above threshold
    n_connections = np.sum(np.abs(conn_no_diag) > threshold)
    n_possible = conn_no_diag.shape[0] * (conn_no_diag.shape[1] - 1)
    
    density = n_connections / n_possible
    
    return density