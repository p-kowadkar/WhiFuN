import numpy as np
import pytest
from numpy.testing import assert_allclose
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


# --- Tests for fdr_bh ---

from pywhifun.core.stats import fdr_bh
from statsmodels.stats.multitest import fdrcorrection

def test_fdr_bh_basic():
    """Tests the fdr_bh wrapper against the statsmodels ground truth."""
    pvals = np.array([0.001, 0.02, 0.04, 0.1, 0.5, 0.6])
    q = 0.05

    # Get ground truth from statsmodels
    expected_h, expected_adj_p = fdrcorrection(pvals, alpha=q, method='indep')

    # Run our wrapper
    h, crit_p, adj_p = fdr_bh(pvals, q=q, method='pdep')

    # Compare h and adj_p to ground truth
    assert_allclose(h, expected_h)
    assert_allclose(adj_p, expected_adj_p)

    # Test our crit_p calculation separately
    expected_crit_p = np.max(pvals[expected_h]) if np.any(expected_h) else 0.0
    assert np.isclose(crit_p, expected_crit_p)

def test_fdr_bh_dependent():
    """Tests the fdr_bh wrapper with the 'dep' method against statsmodels."""
    pvals = np.array([0.01, 0.02, 0.03, 0.4, 0.5])
    q = 0.05

    # Get ground truth from statsmodels
    expected_h, expected_adj_p = fdrcorrection(pvals, alpha=q, method='negcorr')

    # Run our wrapper
    h, crit_p, adj_p = fdr_bh(pvals, q=q, method='dep')

    assert_allclose(h, expected_h)
    assert_allclose(adj_p, expected_adj_p)

    # Test our crit_p calculation separately
    expected_crit_p = np.max(pvals[expected_h]) if np.any(expected_h) else 0.0
    assert np.isclose(crit_p, expected_crit_p)

def test_fdr_bh_no_significant():
    """Tests the fdr_bh wrapper when no p-values are significant."""
    pvals = np.array([0.1, 0.2, 0.3, 0.4, 0.5])
    h, crit_p, adj_p = fdr_bh(pvals, q=0.05)

    assert not np.any(h)
    assert crit_p == 0.0

def test_fdr_bh_matrix_input():
    """Tests that the wrapper handles multi-dimensional arrays correctly."""
    pvals = np.array([[0.01, 0.6], [0.03, 0.4]])
    q = 0.05

    # Get ground truth for the flattened array
    expected_h_flat, _ = fdrcorrection(pvals.flatten(), alpha=q, method='indep')
    expected_h = expected_h_flat.reshape(pvals.shape)

    # Run our wrapper
    h, crit_p, adj_p = fdr_bh(pvals, q=q)

    assert h.shape == pvals.shape
    assert adj_p.shape == pvals.shape
    assert_allclose(h, expected_h)

def test_fdr_bh_invalid_method():
    """Tests that an invalid method string raises a ValueError."""
    pvals = np.array([0.01, 0.05])
    with pytest.raises(ValueError, match="Method must be either 'pdep' or 'dep'"):
        fdr_bh(pvals, method='invalid_method')
