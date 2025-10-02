import pytest
import numpy as np
import os
import nibabel as nib
from numpy.testing import assert_allclose

# Imports from the original new test file
from pywhifun.preprocessing.motion import fd_check_stub

# Imports from the old, misplaced test file
from pywhifun.preprocessing.motion import calculate_fd, calculate_fd_sum, realign_image_stub

# --- Test for the new fd_check_stub ---

def test_fd_check_stub():
    """
    Tests that the fd_check_stub runs without error and returns the expected
    boolean value, logging a message.
    """
    # The stub doesn't actually use these inputs, so they can be simple.
    motion_params_path = "/fake/path/motion.par"
    subject = {"name": "sub-01"}
    params = {}

    # The stub is hardcoded to return False (subject passes)
    result = fd_check_stub(motion_params_path, subject, params)

    assert result is False, "fd_check_stub should return False"

# --- Tests from the old, preserved test_motion.py ---

def test_calculate_fd_basic():
    """Tests the FD calculation with a simple, known input."""
    # 4 timepoints, 6 parameters
    motion_params = np.array([
        [0, 0, 0, 0, 0, 0],
        [1, 1, 0, 0, 0, 0],
        [1, 2, 2, 0, 0, 0],
        [1, 2, 2, 3, 4, 0]
    ])

    expected_fd = np.array([np.sqrt(2), np.sqrt(5), 5.0])

    actual_fd = calculate_fd(motion_params)

    assert actual_fd.shape == (3,)
    assert_allclose(actual_fd, expected_fd)

def test_calculate_fd_invalid_input_shape():
    """Tests that a ValueError is raised for inputs with incorrect dimensions."""
    with pytest.raises(ValueError, match="must be a 2D array"):
        calculate_fd(np.array([1, 2, 3, 4, 5, 6]))

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

def test_calculate_fd_sum_basic():
    """Tests the sum-based FD calculation with a simple, known input."""
    motion_params = np.array([
        [0, 0, 0, 0, 0, 0],
        [1, -1, 0.5, 0.01, -0.01, 0],
        [2, -1, 0.5, 0.01, -0.01, 0.02]
    ])

    expected_fd = np.array([0.5, 2.0])

    actual_fd = calculate_fd_sum(motion_params)

    assert actual_fd.shape == (2,)
    assert_allclose(actual_fd, expected_fd)

def test_calculate_fd_sum_invalid_input():
    """Tests that a ValueError is raised for inputs with incorrect dimensions."""
    with pytest.raises(ValueError, match="shape \\(n_timepoints, 6\\)"):
        calculate_fd_sum(np.zeros((10, 5)))

def test_realign_image_stub(tmp_path):
    """Tests that the realignment stub correctly creates dummy output files."""
    nifti_path = tmp_path / "func.nii.gz"
    data = np.zeros((10, 10, 10, 5))
    img = nib.Nifti1Image(data, np.eye(4))
    nib.save(img, nifti_path)

    prefix = 'r'
    realigned_path, motion_path = realign_image_stub(str(nifti_path), output_prefix=prefix)

    assert os.path.exists(realigned_path)
    assert os.path.exists(motion_path)

    loaded_realigned = nib.load(realigned_path)
    assert_allclose(loaded_realigned.get_fdata(), data)

    motion_params = np.loadtxt(motion_path)
    assert motion_params.shape == (5, 6)
    assert np.all(motion_params == 0)