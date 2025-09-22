import numpy as np
from numpy.typing import ArrayLike

def matrix_to_vector(matrix: ArrayLike) -> np.ndarray:
    """
    Converts the upper-triangular portion of a matrix or a stack of matrices
    into column vectors.

    This function is a Python equivalent of the `corrvec.m` utility in WhiFuN.
    It takes an (N, N) or (N, N, M) array and returns an array of shape
    (L, M), where L is the number of upper-triangular elements and M is the
    number of matrices.

    Args:
        matrix: A 2D (N, N) or 3D (N, N, M) numpy array.

    Returns:
        A 2D numpy array of shape (L, M) containing the vectorized
        upper-triangular elements of each matrix. If the input was 2D,
        the output shape is (L, 1).

    Raises:
        ValueError: If the input array is not 2D or 3D, or if the first
                    two dimensions are not equal.
    """
    matrix = np.asarray(matrix)

    if matrix.ndim < 2 or matrix.ndim > 3:
        raise ValueError("Input must be a 2D or 3D array.")

    if matrix.shape[0] != matrix.shape[1]:
        raise ValueError("Input matrix must be square (N, N) or a stack of square matrices (N, N, M).")

    n = matrix.shape[0]
    if n < 2:
        # Handle edge case of 0x0 or 1x1 matrix
        if matrix.ndim == 2:
            return np.array([[]]).reshape(0, 1)
        else:
            return np.array([[]]).reshape(0, matrix.shape[2])

    # Get indices of the upper triangle, excluding the diagonal (k=1)
    iu = np.triu_indices(n, k=1)

    # If the matrix is 2D, treat it as a 3D stack of one matrix for consistent handling
    if matrix.ndim == 2:
        matrix = matrix[..., np.newaxis]

    # Indexing with the upper-triangle indices extracts the values.
    # The result is of shape (L, M) where L is number of elements and M is number of matrices.
    vectorized_matrices = matrix[iu[0], iu[1], :]

    return vectorized_matrices
