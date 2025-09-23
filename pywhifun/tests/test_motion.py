import numpy as np
import pytest
from numpy.testing import assert_allclose
from pywhifun.preprocessing.motion import calculate_fd

def test_calculate_fd_basic():
    """Tests the FD calculation with a simple, known input."""
    # 4 timepoints, 6 parameters
    motion_params = np.array([
        [0, 0, 0, 0, 0, 0],
        [1, 1, 0, 0, 0, 0],  # Diff = [1, 1, 0, 0, 0, 0] -> FD = sqrt(1^2 + 1^2) = sqrt(2)
        [1, 2, 2, 0, 0, 0],  # Diff = [0, 1, 2, 0, 0, 0] -> FD = sqrt(1^2 + 2^2) = sqrt(5)
        [1, 2, 2, 3, 4, 0]   # Diff = [0, 0, 0, 3, 4, 0] -> FD = sqrt(3^2 + 4^2) = sqrt(25) = 5
    ])

    expected_fd = np.array([np.sqrt(2), np.sqrt(5), 5.0])

    actual_fd = calculate_fd(motion_params)

    assert actual_fd.shape == (3,)
    assert_allclose(actual_fd, expected_fd)

def test_calculate_fd_invalid_input_shape():
    """Tests that a ValueError is raised for inputs with incorrect dimensions."""
    # Test with a 1D array
    with pytest.raises(ValueError, match="must be a 2D array"):
        calculate_fd(np.array([1, 2, 3, 4, 5, 6]))

    # Test with only one timepoint
    with pytest.raises(ValueError, match="at least 2 timepoints"):
        calculate_fd(np.array([[1, 2, 3, 4, 5, 6]]))

def test_calculate_fd_no_motion():
    """Tests that FD is zero when there is no motion."""
    motion_params = np.array([
        [0.5, 1.2, -0.8, 0, 0, 0],
        [0.5, 1.2, -0.8, 0, 0, 0],
        [0.5, 1.2, -0.8, 0, 0, 0]
    ])

    expected_fd = np.array([0.0, 0.0])
    actual_fd = calculate_fd(motion_params)
    assert_allclose(actual_fd, expected_fd)


# --- Tests for calculate_fd_sum ---

from pywhifun.preprocessing.motion import calculate_fd_sum

def test_calculate_fd_sum_basic():
    """Tests the sum-based FD calculation with a simple, known input."""
    motion_params = np.array([
        [0, 0, 0, 0, 0, 0],
        [1, -1, 0.5, 0.01, -0.01, 0],
        [2, -1, 0.5, 0.01, -0.01, 0.02]
    ])

    # Expected FD:
    # t1: (1-0) + (-1-0) + (0.5-0) = 0.5. Rot diff is 0. FD = 0.5
    # t2: (2-1) + (-1-(-1)) + (0.5-0.5) = 1. Rot diff is 0.02. Scaled rot diff = 1. FD = 1+1=2.0
    expected_fd = np.array([0.5, 2.0])

    actual_fd = calculate_fd_sum(motion_params)

    assert actual_fd.shape == (2,)
    assert_allclose(actual_fd, expected_fd)

def test_calculate_fd_sum_invalid_input():
    """Tests that a ValueError is raised for inputs with incorrect dimensions."""
    with pytest.raises(ValueError, match="shape \\(n_timepoints, 6\\)"):
        calculate_fd_sum(np.zeros((10, 5))) # wrong number of columns
