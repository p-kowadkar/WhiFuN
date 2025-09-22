import numpy as np
import pytest
from pywhifun.core.stats import fisher_z

def test_fisher_z_scalar():
    """Tests the Fisher Z-transform on a single scalar value."""
    r = 0.5
    expected_z = 0.5493061443340549
    # Using np.isclose for scalar comparison is robust for floats
    assert np.isclose(fisher_z(r), expected_z)

def test_fisher_z_array():
    """Tests the Fisher Z-transform on a numpy array."""
    r = np.array([0, 0.25, 0.5, 0.75])
    expected_z = np.array([0.0, 0.25541281, 0.54930614, 0.97295507])
    # Using np.testing.assert_allclose for array comparison
    np.testing.assert_allclose(fisher_z(r), expected_z)

def test_fisher_z_zero():
    """Tests the Fisher Z-transform for an input of 0."""
    assert fisher_z(0) == 0.0

def test_fisher_z_boundaries():
    """
    Tests the Fisher Z-transform at the boundaries r=1 and r=-1,
    where the result should be infinity.
    """
    assert fisher_z(1) == np.inf
    assert fisher_z(-1) == -np.inf

def test_fisher_z_invalid_input():
    """
    Tests that np.arctanh issues a RuntimeWarning for inputs outside [-1, 1],
    which is the expected behavior.
    """
    with pytest.warns(RuntimeWarning):
        fisher_z(1.1)
    with pytest.warns(RuntimeWarning):
        fisher_z(-1.1)
