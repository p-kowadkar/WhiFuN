import numpy as np
import pytest
from numpy.testing import assert_allclose
from pywhifun.utils.array_utils import matrix_to_vector

def test_matrix_to_vector_2d():
    """Tests vectorizing a single 2D matrix."""
    matrix = np.array([
        [1, 2, 3],
        [4, 5, 6],
        [7, 8, 9]
    ])
    # Upper triangle (k=1) is [2, 3, 6]
    expected = np.array([[2], [3], [6]])
    actual = matrix_to_vector(matrix)
    assert actual.shape == (3, 1)
    assert_allclose(actual, expected)

def test_matrix_to_vector_3d():
    """Tests vectorizing a stack of 3D matrices."""
    matrix = np.zeros((3, 3, 2))
    matrix[:, :, 0] = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
    matrix[:, :, 1] = np.array([[10, 20, 30], [40, 50, 60], [70, 80, 90]])

    # Expected shape is (3 connections, 2 subjects)
    expected = np.array([
        [2, 20],
        [3, 30],
        [6, 60]
    ])
    actual = matrix_to_vector(matrix)
    assert actual.shape == (3, 2)
    assert_allclose(actual, expected)

def test_matrix_to_vector_invalid_shape():
    """Tests that a ValueError is raised for non-square or invalid ndim inputs."""
    with pytest.raises(ValueError, match="Input matrix must be square"):
        matrix_to_vector(np.zeros((3, 4)))

    with pytest.raises(ValueError, match="Input must be a 2D or 3D array"):
        matrix_to_vector(np.zeros(3)) # 1D

    with pytest.raises(ValueError, match="Input must be a 2D or 3D array"):
        matrix_to_vector(np.zeros((2, 2, 2, 2))) # 4D

def test_matrix_to_vector_edge_case_1x1():
    """Tests behavior with a 1x1 matrix."""
    matrix = np.array([[5]])
    actual = matrix_to_vector(matrix)
    # Expected shape is (0 connections, 1 subject)
    assert actual.shape == (0, 1)

def test_matrix_to_vector_3d_edge_case_1x1():
    """Tests behavior with a stack of 1x1 matrices."""
    matrix = np.zeros((1, 1, 5))
    actual = matrix_to_vector(matrix)
    # Expected shape is (0 connections, 5 subjects)
    assert actual.shape == (0, 5)
