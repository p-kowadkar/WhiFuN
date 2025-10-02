import pytest
from pywhifun.preprocessing.regression import nuisance_regression_stub

def test_nuisance_regression_stub():
    """
    Tests that the nuisance regression stub is callable and returns a string.
    """
    result = nuisance_regression_stub("/path/func.nii", "/path/anat.nii", {})
    assert isinstance(result, str)
    assert result.endswith("_regressed.nii")