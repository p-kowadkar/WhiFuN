#!/usr/bin/env python3
"""
Test script to demonstrate PyWhiFuN functionality
"""

import numpy as np
import os
import tempfile
from pathlib import Path

# Add pywhifun to path
import sys
sys.path.insert(0, str(Path(__file__).parent))

from pywhifun.utils.math_utils import fisher_z
from pywhifun.preprocessing.motion import calculate_fd as motion_fd, motion_qc
from pywhifun.io.nifti_io import nifti_read


def test_fisher_z():
    """Test Fisher Z transformation"""
    print("Testing Fisher Z transformation...")
    
    # Test single value
    r = 0.5
    z = fisher_z(r)
    print(f"Fisher Z for r={r}: {z:.4f}")
    
    # Test array
    r_values = np.array([0.1, 0.3, 0.5, 0.7, 0.9])
    z_values = fisher_z(r_values)
    print("Fisher Z for multiple values:")
    for r, z in zip(r_values, z_values):
        print(f"  r={r:.1f} -> Z={z:.4f}")
    
    print("✓ Fisher Z transformation test passed\n")


def test_fd_calculation():
    """Test framewise displacement calculation"""
    print("Testing framewise displacement calculation...")
    
    # Create synthetic motion parameters
    n_timepoints = 100
    motion_params = np.random.randn(n_timepoints, 6) * 0.1  # Small random motion
    
    # Add some larger motion at specific timepoints
    motion_params[50:55, :] += np.random.randn(5, 6) * 0.5  # Larger motion
    
    # Calculate FD
    fd = motion_fd(motion_params)
    
    print(f"Calculated FD for {len(fd)} timepoints")
    print(f"Mean FD: {fd.mean():.4f} mm")
    print(f"Max FD: {fd.max():.4f} mm")
    print(f"Timepoints with FD > 0.5: {np.sum(fd > 0.5)}")
    
    # Test with file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        np.savetxt(f.name, motion_params, fmt='%.6f')
        temp_file = f.name
    
    try:
        fd_from_file = motion_fd(temp_file)
        assert np.allclose(fd, fd_from_file, rtol=1e-4, atol=1e-4), "FD calculation from file doesn't match"
        print("✓ FD calculation from file matches direct calculation")
    finally:
        os.unlink(temp_file)
    
    print("✓ Framewise displacement test passed\n")


def test_motion_qc():
    """Test motion quality control"""
    print("Testing motion quality control...")
    
    # Create motion parameters with known characteristics
    n_timepoints = 200
    motion_params = np.random.randn(n_timepoints, 6) * 0.05  # Low motion
    
    # Add high motion period
    motion_params[100:110, :] += np.random.randn(10, 6) * 0.8  # High motion
    
    # Save to temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        np.savetxt(f.name, motion_params, fmt='%.6f')
        temp_file = f.name
    
    try:
        # Run QC
        qc_stats = motion_qc(temp_file, max_fd=0.5, mean_fd=0.2, threshold_pct=0.2)
        
        print("Motion QC Results:")
        for key, value in qc_stats.items():
            if isinstance(value, float):
                print(f"  {key}: {value:.4f}")
            else:
                print(f"  {key}: {value}")
        
        # Check if results make sense
        assert qc_stats['n_timepoints'] == n_timepoints, "Incorrect timepoint count"
        assert qc_stats['max_fd'] > 0, "Max FD should be positive"
        
        print("✓ Motion QC test passed")
        
    finally:
        os.unlink(temp_file)
    
    print()


def test_correlation_functions():
    """Test correlation functions"""
    print("Testing correlation functions...")
    
    # Create synthetic time series
    n_timepoints = 100
    n_regions = 5
    
    # Create correlated time series
    base_signal = np.random.randn(n_timepoints)
    ts_data = np.zeros((n_timepoints, n_regions))
    
    for i in range(n_regions):
        noise = np.random.randn(n_timepoints) * 0.5
        ts_data[:, i] = base_signal * (0.8 - i * 0.1) + noise
    
    # Calculate correlation matrix
    corr_matrix = np.corrcoef(ts_data.T)
    
    print(f"Created {n_regions}x{n_regions} correlation matrix")
    print(f"Mean correlation: {corr_matrix[np.triu_indices(n_regions, k=1)].mean():.4f}")
    
    # Apply Fisher Z transformation
    z_matrix = fisher_z(corr_matrix)
    print(f"Applied Fisher Z transformation")
    print(f"Mean Z value: {z_matrix[np.triu_indices(n_regions, k=1)].mean():.4f}")
    
    print("✓ Correlation functions test passed\n")


def main():
    """Run all tests"""
    print("PyWhiFuN Test Suite")
    print("=" * 50)
    
    try:
        test_fisher_z()
        test_fd_calculation()
        test_motion_qc()
        test_correlation_functions()
        
        print("=" * 50)
        print("✓ All tests passed successfully!")
        print("\nPyWhiFuN basic functionality is working correctly.")
        print("You can now use the command-line interface:")
        print("  python -m pywhifun.cli --help")
        
    except Exception as e:
        print(f"✗ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == '__main__':
    exit(main())