import numpy as np
from numpy.typing import ArrayLike

def calculate_fd(motion_params: ArrayLike) -> np.ndarray:
    """
    Calculates Framewise Displacement (FD).

    This function replicates the specific FD calculation from `fd_calc.m`
    in the WhiFuN toolbox, which is the Euclidean norm (L2 norm) of the
    temporal difference of the motion parameters.

    Note: This is a simplified FD calculation and may differ from other
    implementations (e.g., Power et al., 2012) which apply a
    transformation to rotational parameters before calculating displacement.

    Args:
        motion_params: A 2D numpy array of shape (n_timepoints, n_params)
                       containing the motion parameters (e.g., 3 translations
                       and 3 rotations).

    Returns:
        A 1D numpy array of shape (n_timepoints - 1,) containing the
        Framewise Displacement for each time point.

    Raises:
        ValueError: If the input array is not 2D or has fewer than 2 timepoints.
    """
    motion_params = np.asarray(motion_params)

    if motion_params.ndim != 2 or motion_params.shape[0] < 2:
        raise ValueError("motion_params must be a 2D array with at least 2 timepoints.")

    # Calculate temporal difference (row-wise)
    diff_matrix = np.diff(motion_params, axis=0)

    # Calculate the L2 norm of each row of the difference matrix
    fd = np.linalg.norm(diff_matrix, axis=1)

    return fd
