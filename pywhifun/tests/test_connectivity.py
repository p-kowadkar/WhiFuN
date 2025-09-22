import numpy as np
import pytest
from numpy.testing import assert_allclose
from pywhifun.networks.connectivity import calculate_static_fc
from pywhifun.core.stats import fisher_z

@pytest.fixture
def sample_timeseries():
    """
    Creates a sample regional timeseries array for testing.
    Shape: (10 timepoints, 3 ROIs, 2 subjects)
    """
    ts = np.zeros((10, 3, 2))
    rng = np.random.default_rng(0)

    # Subject 1: ROI 0 and 1 are highly correlated
    roi0 = rng.standard_normal(10)
    roi1 = roi0 * 0.9 + rng.standard_normal(10) * 0.1 # Strong positive correlation
    roi2 = rng.standard_normal(10) # Independent
    ts[:, :, 0] = np.vstack([roi0, roi1, roi2]).T

    # Subject 2: ROI 1 and 2 are anti-correlated
    roi3 = rng.standard_normal(10) # Independent
    roi4 = rng.standard_normal(10)
    roi5 = -roi4 * 0.9 + rng.standard_normal(10) * 0.1 # Strong negative correlation
    ts[:, :, 1] = np.vstack([roi3, roi4, roi5]).T

    return ts

def test_calculate_static_fc_basic(sample_timeseries):
    """Tests the basic static FC calculation for shape and expected correlations."""
    fc_vectors = calculate_static_fc(sample_timeseries)

    # Expected shape: 3 ROIs -> 3 connections (0-1, 0-2, 1-2), 2 subjects
    assert fc_vectors.shape == (3, 2)

    # Check subject 1: corr(roi0, roi1) should be high and positive
    # This corresponds to the first element of the vectorized matrix
    assert fc_vectors[0, 0] > 0.8

    # Check subject 2: corr(roi4, roi5) should be high and negative
    # This corresponds to the last element (corr between ROI 1 and 2)
    assert fc_vectors[2, 1] < -0.8

def test_calculate_static_fc_fisher_z(sample_timeseries):
    """Tests that the Fisher Z-transform option is applied correctly."""
    fc_vectors_no_z = calculate_static_fc(sample_timeseries, fisher_z_transform=False)
    fc_vectors_with_z = calculate_static_fc(sample_timeseries, fisher_z_transform=True)

    # The transformed values should be different from the original
    assert not np.allclose(fc_vectors_no_z, fc_vectors_with_z)

    # Manually transform the first subject's vector and compare
    # Note: we need to reconstruct the matrix to handle the diagonal correctly
    # before comparing, but for a simple check, we can transform the vector.
    # The underlying function handles the diagonal properly.
    expected_z_vec = fisher_z(fc_vectors_no_z[:, 0])
    assert_allclose(fc_vectors_with_z[:, 0], expected_z_vec)

def test_calculate_static_fc_invalid_input():
    """Tests that a ValueError is raised for invalid input shape."""
    with pytest.raises(ValueError, match="must be a 3D array"):
        calculate_static_fc(np.zeros((10, 3))) # 2D input

def test_calculate_static_fc_single_roi():
    """Tests behavior with only one ROI, which should result in no connections."""
    ts = np.random.default_rng(1).standard_normal((20, 1, 5)) # 5 subjects
    fc_vectors = calculate_static_fc(ts)

    # There are no connections with only one ROI
    assert fc_vectors.shape == (0, 5)
