import pytest
from pywhifun.preprocessing.normalization import normalize_image_stub

def test_normalize_image_stub():
    """
    Tests that the normalization stub is callable and returns a string.
    """
    result = normalize_image_stub("/path/func.nii", "/path/anat.nii", {})
    assert isinstance(result, str)
    assert result.endswith("_normalized.nii")