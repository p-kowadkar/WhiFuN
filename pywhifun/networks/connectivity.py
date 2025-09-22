import numpy as np
from numpy.typing import ArrayLike

from pywhifun.core.stats import fisher_z
from pywhifun.utils.array_utils import matrix_to_vector

def calculate_static_fc(regional_timeseries: ArrayLike, fisher_z_transform: bool = False) -> np.ndarray:
    """
    Calculates static functional connectivity for a group of subjects.

    This function computes the Pearson correlation between regional time series
    for each subject, optionally applies a Fisher Z-transform, and then
    vectorizes the upper triangle of the resulting connectivity matrices.

    This replicates the default (static, linear) behavior of the MATLAB
    `functional_connectivity.m` script.

    Args:
        regional_timeseries: A 3D numpy array of shape
                             (n_timepoints, n_rois, n_subjects)
                             containing the time series for each region of
                             interest for each subject.
        fisher_z_transform: If True, applies the Fisher Z-transform to the
                            correlation matrices. Defaults to False.

    Returns:
        A 2D numpy array of shape (n_connections, n_subjects) where each
        column is the vectorized upper triangle of a subject's
        connectivity matrix.

    Raises:
        ValueError: If the input array is not 3D.
    """
    regional_timeseries = np.asarray(regional_timeseries)
    if regional_timeseries.ndim != 3:
        raise ValueError("Input regional_timeseries must be a 3D array.")

    n_timepoints, n_rois, n_subjects = regional_timeseries.shape

    # Initialize an array to hold all the connectivity matrices
    fc_matrices = np.zeros((n_rois, n_rois, n_subjects))

    for i in range(n_subjects):
        # Get the timeseries for the current subject (n_timepoints x n_rois)
        subject_ts = regional_timeseries[:, :, i]

        # numpy.corrcoef expects rows to be variables, so we use rowvar=False
        # to treat columns as variables.
        # The result is an (n_rois x n_rois) correlation matrix.
        corr_matrix = np.corrcoef(subject_ts, rowvar=False)

        # Handle case of single ROI, where corrcoef returns a scalar
        if n_rois == 1:
            corr_matrix = np.array([[1.0]])

        if fisher_z_transform:
            # To avoid warnings/inf on the diagonal (self-correlation is always 1),
            # we can set it to 0 before the transform and then set it back.
            np.fill_diagonal(corr_matrix, 0)
            corr_matrix = fisher_z(corr_matrix)
            # After transform, the diagonal is 0. This is desired as self-
            # connections are usually excluded from graph analysis.
            np.fill_diagonal(corr_matrix, 0)

        fc_matrices[:, :, i] = corr_matrix

    # Vectorize the upper triangle of all matrices at once
    fc_vectors = matrix_to_vector(fc_matrices)

    return fc_vectors
