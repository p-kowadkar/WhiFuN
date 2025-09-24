import pytest
from pywhifun.preprocessing.registration import coregister_image_stub

def test_coregister_image_stub():
    """
    Tests that the coregistration stub runs without error and returns True,
    as expected for a placeholder function.
    """
    success = coregister_image_stub(
        reference_path="/path/to/anat.nii",
        source_path="/path/to/func.nii",
        other_paths=["/path/to/func.nii,1", "/path/to/func.nii,2"]
    )
    assert success is True