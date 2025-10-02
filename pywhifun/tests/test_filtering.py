import pytest
from pywhifun.preprocessing.filtering import temporal_filter_stub

def test_temporal_filter_stub():
    """
    Tests that the temporal filtering stub is callable and returns a string.
    """
    result = temporal_filter_stub("/path/func.nii", {})
    assert isinstance(result, str)
    assert result.endswith("_filtered.nii")