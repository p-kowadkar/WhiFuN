import pytest
from pywhifun.preprocessing.smoothing import spatial_smooth_stub

def test_spatial_smooth_stub():
    """
    Tests that the spatial smoothing stub is callable and returns a string.
    """
    result = spatial_smooth_stub("/path/func.nii", {})
    assert isinstance(result, str)
    assert result.endswith("_smoothed.nii")