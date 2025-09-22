import os
import pytest
from pywhifun.utils.path_utils import complete_filepath

@pytest.fixture
def temp_dir_structure(tmp_path):
    """
    Creates a temporary directory structure for testing file path resolution.

    Structure:
    tmp_path/
    └── sub-01/
        ├── anat/
        │   └── t1w.nii.gz
        └── func/
            ├── bold_run-1.nii.gz
            └── bold_run-2.nii.gz
    """
    sub_dir = tmp_path / "sub-01"
    sub_dir.mkdir()
    (sub_dir / "anat").mkdir()
    (sub_dir / "func").mkdir()

    # Create some files
    (sub_dir / "anat" / "t1w.nii.gz").touch()
    (sub_dir / "func" / "bold_run-1.nii.gz").touch()
    (sub_dir / "func" / "bold_run-2.nii.gz").touch()

    return str(tmp_path) # Return path as string for os.path.join

def test_complete_filepath_single_file(temp_dir_structure):
    """Tests resolving a path that matches a single file."""
    # Pattern that should match only 't1w.nii.gz'
    resolved_path = complete_filepath(temp_dir_structure, "sub-01", "anat", "*.nii.gz")

    expected_path = os.path.join(temp_dir_structure, "sub-01", "anat", "t1w.nii.gz")

    assert resolved_path == expected_path

def test_complete_filepath_multiple_files(temp_dir_structure):
    """Tests resolving a path that matches multiple files, returning the directory."""
    # Pattern that should match both 'bold_run-1.nii.gz' and 'bold_run-2.nii.gz'
    resolved_path = complete_filepath(temp_dir_structure, "sub-01", "func", "bold*.nii.gz")

    # Should return the parent directory
    expected_path = os.path.join(temp_dir_structure, "sub-01", "func")

    assert resolved_path == expected_path

def test_complete_filepath_no_match(temp_dir_structure):
    """Tests resolving a path that has no matches."""
    # Pattern that won't match anything
    resolved_path = complete_filepath(temp_dir_structure, "sub-01", "dwi", "*.nii.gz")

    assert resolved_path == ""

def test_complete_filepath_no_args():
    """Tests calling the function with no arguments."""
    assert complete_filepath() == ""

def test_complete_filepath_no_wildcard(temp_dir_structure):
    """Tests resolving a path with no wildcard that points to a single file."""
    resolved_path = complete_filepath(temp_dir_structure, "sub-01", "anat", "t1w.nii.gz")

    expected_path = os.path.join(temp_dir_structure, "sub-01", "anat", "t1w.nii.gz")

    assert resolved_path == expected_path
