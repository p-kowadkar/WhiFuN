import numpy as np
from numpy.typing import ArrayLike
from typing import Union, Tuple
from statsmodels.stats.multitest import fdrcorrection


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


def fdr_bh(pvals: ArrayLike, q: float = 0.05, method: str = 'pdep') -> Tuple[np.ndarray, float, np.ndarray]:
    """
    Performs the Benjamini-Hochberg FDR correction on a set of p-values.

    This function is a wrapper around `statsmodels.stats.multitest.fdrcorrection`
    and is designed to be a close analog to the MATLAB `fdr_bh.m` script.

    Args:
        pvals: A scalar or numpy array of p-values.
        q: The desired false discovery rate (alpha). Defaults to 0.05.
        method: The correction method to use.
            'pdep': for independent or positively dependent tests (Benjamini-Hochberg).
            'dep': for tests with any dependency structure (Benjamini-Yekutieli).
            Defaults to 'pdep'.

    Returns:
        A tuple containing:
        - h: A boolean array of the same shape as pvals, where True indicates
          a significant p-value.
        - crit_p: The critical p-value. All original p-values less than or
          equal to this value are considered significant.
        - adj_p: An array of the FDR-corrected p-values, with the same shape
          as pvals.
    """
    pvals = np.asarray(pvals)
    original_shape = pvals.shape
    pvals_flat = pvals.flatten()

    if method == 'pdep':
        statsmodels_method = 'indep'
    elif method == 'dep':
        statsmodels_method = 'negcorr'
    else:
        raise ValueError("Method must be either 'pdep' or 'dep'.")

    rejected, pvals_corrected = fdrcorrection(pvals_flat, alpha=q, method=statsmodels_method)

    # Reshape results back to the original shape
    h = rejected.reshape(original_shape)
    adj_p = pvals_corrected.reshape(original_shape)

    # Calculate the critical p-value from the uncorrected p-values
    pvals_significant = pvals_flat[rejected]
    crit_p = np.max(pvals_significant) if pvals_significant.size > 0 else 0.0

    return h, crit_p, adj_p


def calculate_idiff(vec1: ArrayLike, vec2: ArrayLike) -> Tuple[float, np.ndarray, float, float]:
    """
    Calculates the "identification differential" (idiff) score.

    This score measures how uniquely identifiable subjects are based on their
    functional connectivity (FC) patterns across two sessions. It is the
    difference between the average self-similarity and the average
    cross-subject similarity.

    This function replicates the primary (non-PCA) logic of `idiff.m`.

    Args:
        vec1 (ArrayLike): An array of shape (n_features, n_subjects) containing
                          the vectorized FC for each subject in session 1.
        vec2 (ArrayLike): An array of shape (n_features, n_subjects) containing
                          the vectorized FC for each subject in session 2.

    Returns:
        A tuple containing:
        - idiff_score (float): The final identifiability score.
        - corr_matrix (np.ndarray): The subject-by-subject correlation matrix.
        - iself (float): The mean self-correlation across sessions.
        - iothers (float): The mean cross-subject correlation.
    """
    vec1 = np.asarray(vec1)
    vec2 = np.asarray(vec2)

    if vec1.shape != vec2.shape:
        raise ValueError("Input vectors vec1 and vec2 must have the same shape.")

    # Correlate each column of vec1 with each column of vec2
    # This is not a simple matrix multiplication. We need to do it column by column.
    n_subjects = vec1.shape[1]
    corr_matrix = np.zeros((n_subjects, n_subjects))
    for i in range(n_subjects):
        for j in range(n_subjects):
            # Correlation between subject i from session 1 and subject j from session 2
            corr_matrix[i, j] = np.corrcoef(vec1[:, i], vec2[:, j])[0, 1]

    # Calculate Iself: mean of the diagonal of the absolute correlation matrix
    iself = np.mean(np.abs(np.diag(corr_matrix)))

    # Calculate Iothers: mean of the off-diagonal elements
    # Create a copy to avoid modifying the original, fill diagonal with NaN
    temp_matrix = np.abs(corr_matrix.copy())
    np.fill_diagonal(temp_matrix, np.nan)
    iothers = np.nanmean(temp_matrix)

    # Calculate idiff score
    idiff_score = (iself - iothers) * 100

    return idiff_score, corr_matrix, iself, iothers
