import pytest
from pywhifun.visualization.qc import ts_check_stub

def test_ts_check_stub():
    """
    Tests that the time series QC stub is callable and returns True.
    """
    result = ts_check_stub("/path/func.nii", "/path/motion.txt", "sub-01")
    assert result is True