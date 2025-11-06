"""
Motion Quality Control Functions

Converted from MATLAB WhiFuN motion QC functions.
"""

import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from pathlib import Path
import nibabel as nib
from ..io.nifti_io import nifti_read
from ..preprocessing.motion import calculate_fd
from ..utils.validation import validate_file_path


def motion_quality_control(output_folder, realigned_func_path, subject_name, 
                          max_fd_threshold, mean_fd_threshold, fd_20_threshold,
                          overwrite=False, motion_params=None):
    """
    Generate a quality control figure for head motion.
    
    Creates a comprehensive quality control report for head motion for a single
    subject. The report consists of four plots combined into a single figure.
    
    Parameters
    ----------
    output_folder : str
        Path to the quality control directory for saving the figure
    realigned_func_path : str
        Full path to the realigned functional file
    subject_name : str
        Subject's name for labeling
    max_fd_threshold : float
        Maximum FD threshold
    mean_fd_threshold : float
        Mean FD threshold  
    fd_20_threshold : float
        FD threshold for percentage of excluded volumes
    overwrite : bool, optional
        Force overwriting existing files (default: False)
    motion_params : ndarray, optional
        Motion parameters matrix to use instead of loading from file
        
    Returns
    -------
    qc_metrics : dict
        Dictionary containing motion QC metrics
        
    Notes
    -----
    Converted from MATLAB whifun_qc_head_motion.m
    """
    # Create output directory
    os.makedirs(output_folder, exist_ok=True)
    
    # Check if QC file already exists
    qc_filename = f"{subject_name}_motion_qc.png"
    qc_filepath = os.path.join(output_folder, qc_filename)
    
    if os.path.exists(qc_filepath) and not overwrite:
        print(f"Motion QC file already exists: {qc_filename}")
        return None
    
    print(f"Generating motion QC for subject: {subject_name}")
    
    # Load functional data
    if not os.path.exists(realigned_func_path):
        raise FileNotFoundError(f"Realigned functional file not found: {realigned_func_path}")
    
    func_data, func_affine, func_header = nifti_read(realigned_func_path)
    
    # Get data dimensions
    if func_data.ndim == 4:
        nx, ny, nz, nt = func_data.shape
    else:
        raise ValueError("Functional data must be 4D (x, y, z, time)")
    
    print(f"Functional data shape: {func_data.shape}")
    
    # Calculate global mean signal
    global_mean = calculate_global_mean(func_data)
    
    # Calculate pairwise variance
    pairwise_variance = calculate_pairwise_variance(func_data)
    
    # Load or use provided motion parameters
    if motion_params is None:
        # Try to find motion parameter file
        motion_file = find_motion_parameter_file(realigned_func_path)
        if motion_file:
            motion_params = np.loadtxt(motion_file)
        else:
            print("Warning: Motion parameter file not found. Creating dummy data.")
            motion_params = np.zeros((nt, 6))  # 6 motion parameters
    
    # Calculate framewise displacement
    if motion_params.shape[0] > 0:
        fd_values = calculate_fd(motion_params)
    else:
        fd_values = np.zeros(nt)
    
    # Calculate QC metrics
    qc_metrics = calculate_motion_qc_metrics(
        global_mean, pairwise_variance, fd_values, motion_params,
        max_fd_threshold, mean_fd_threshold, fd_20_threshold
    )
    
    # Create QC figure
    create_motion_qc_figure(
        global_mean, pairwise_variance, motion_params, fd_values,
        qc_metrics, subject_name, qc_filepath,
        max_fd_threshold, mean_fd_threshold, fd_20_threshold
    )
    
    print(f"Motion QC figure saved: {qc_filename}")
    
    return qc_metrics


def calculate_global_mean(func_data):
    """
    Calculate scaled global signal mean over time.
    
    Parameters
    ----------
    func_data : ndarray
        4D functional data (x, y, z, time)
        
    Returns
    -------
    global_mean : ndarray
        Global mean signal over time
    """
    # Calculate mean across all voxels for each timepoint
    global_mean = np.mean(func_data.reshape(-1, func_data.shape[-1]), axis=0)
    
    # Scale to percentage signal change
    baseline_mean = np.mean(global_mean)
    global_mean_scaled = ((global_mean - baseline_mean) / baseline_mean) * 100
    
    return global_mean_scaled


def calculate_pairwise_variance(func_data):
    """
    Calculate pairwise variance between consecutive time points.
    
    Parameters
    ----------
    func_data : ndarray
        4D functional data (x, y, z, time)
        
    Returns
    -------
    pairwise_variance : ndarray
        Pairwise variance over time
    """
    nt = func_data.shape[-1]
    pairwise_variance = np.zeros(nt - 1)
    
    # Reshape data for easier computation
    data_2d = func_data.reshape(-1, nt)
    
    for t in range(nt - 1):
        # Calculate variance between consecutive timepoints
        diff = data_2d[:, t + 1] - data_2d[:, t]
        pairwise_variance[t] = np.var(diff)
    
    return pairwise_variance


def find_motion_parameter_file(func_path):
    """
    Find motion parameter file associated with functional data.
    
    Parameters
    ----------
    func_path : str
        Path to functional data file
        
    Returns
    -------
    motion_file : str or None
        Path to motion parameter file if found
    """
    func_dir = os.path.dirname(func_path)
    func_basename = os.path.splitext(os.path.basename(func_path))[0]
    
    # Common motion parameter file patterns
    patterns = [
        f"rp_{func_basename}.txt",
        f"{func_basename}_motion.txt",
        f"{func_basename}.par",
        "motion_parameters.txt",
        "realignment_parameters.txt"
    ]
    
    for pattern in patterns:
        motion_file = os.path.join(func_dir, pattern)
        if os.path.exists(motion_file):
            return motion_file
    
    return None


def calculate_motion_qc_metrics(global_mean, pairwise_variance, fd_values, motion_params,
                               max_fd_threshold, mean_fd_threshold, fd_20_threshold):
    """
    Calculate motion quality control metrics.
    
    Parameters
    ----------
    global_mean : ndarray
        Global mean signal
    pairwise_variance : ndarray
        Pairwise variance values
    fd_values : ndarray
        Framewise displacement values
    motion_params : ndarray
        Motion parameters
    max_fd_threshold : float
        Maximum FD threshold
    mean_fd_threshold : float
        Mean FD threshold
    fd_20_threshold : float
        FD threshold for percentage calculation
        
    Returns
    -------
    metrics : dict
        Dictionary of QC metrics
    """
    metrics = {}
    
    # Global mean metrics
    metrics['global_mean_range'] = np.ptp(global_mean)  # peak-to-peak
    metrics['global_mean_std'] = np.std(global_mean)
    
    # Pairwise variance metrics
    pv_mean = np.mean(pairwise_variance)
    pv_std = np.std(pairwise_variance)
    metrics['pairwise_variance_mean'] = pv_mean
    metrics['pairwise_variance_std'] = pv_std
    metrics['pairwise_variance_outliers'] = np.sum(pairwise_variance > (pv_mean + 3 * pv_std))
    
    # Motion parameter metrics
    if motion_params.shape[0] > 0:
        # Translation parameters (typically first 3 columns)
        translations = motion_params[:, :3]
        rotations = motion_params[:, 3:6]
        
        metrics['max_translation'] = np.max(np.abs(translations))
        metrics['max_rotation'] = np.max(np.abs(rotations))
        metrics['mean_translation'] = np.mean(np.abs(translations))
        metrics['mean_rotation'] = np.mean(np.abs(rotations))
    
    # Framewise displacement metrics
    if len(fd_values) > 0:
        metrics['max_fd'] = np.max(fd_values)
        metrics['mean_fd'] = np.mean(fd_values)
        metrics['fd_above_threshold'] = np.sum(fd_values > fd_20_threshold)
        metrics['fd_percentage_above_threshold'] = (metrics['fd_above_threshold'] / len(fd_values)) * 100
        
        # QC flags
        metrics['max_fd_pass'] = metrics['max_fd'] <= max_fd_threshold
        metrics['mean_fd_pass'] = metrics['mean_fd'] <= mean_fd_threshold
        metrics['fd_percentage_pass'] = metrics['fd_percentage_above_threshold'] <= 20.0  # 20% threshold
    
    return metrics


def create_motion_qc_figure(global_mean, pairwise_variance, motion_params, fd_values,
                           qc_metrics, subject_name, output_path,
                           max_fd_threshold, mean_fd_threshold, fd_20_threshold):
    """
    Create comprehensive motion QC figure with four subplots.
    
    Parameters
    ----------
    global_mean : ndarray
        Global mean signal
    pairwise_variance : ndarray
        Pairwise variance values
    motion_params : ndarray
        Motion parameters
    fd_values : ndarray
        Framewise displacement values
    qc_metrics : dict
        QC metrics
    subject_name : str
        Subject name for title
    output_path : str
        Output file path
    max_fd_threshold : float
        Maximum FD threshold
    mean_fd_threshold : float
        Mean FD threshold
    fd_20_threshold : float
        FD threshold for percentage calculation
    """
    # Create figure with subplots
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    fig.suptitle(f'Motion Quality Control - {subject_name}', fontsize=16, fontweight='bold')
    
    # Time vectors
    time_points = np.arange(len(global_mean))
    pv_time_points = np.arange(len(pairwise_variance))
    fd_time_points = np.arange(len(fd_values))
    
    # Subplot 1: Global Mean Signal
    ax1 = axes[0, 0]
    ax1.plot(time_points, global_mean, 'b-', linewidth=1)
    ax1.set_title('Global Mean Signal (% Change)')
    ax1.set_xlabel('Time Points')
    ax1.set_ylabel('% Signal Change')
    ax1.grid(True, alpha=0.3)
    ax1.text(0.02, 0.98, f'Range: {qc_metrics.get("global_mean_range", 0):.2f}%\n'
                          f'Std: {qc_metrics.get("global_mean_std", 0):.2f}%',
             transform=ax1.transAxes, verticalalignment='top',
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    # Subplot 2: Pairwise Variance
    ax2 = axes[0, 1]
    ax2.plot(pv_time_points, pairwise_variance, 'g-', linewidth=1)
    
    # Add 3-sigma line
    pv_mean = qc_metrics.get('pairwise_variance_mean', 0)
    pv_std = qc_metrics.get('pairwise_variance_std', 0)
    threshold_line = pv_mean + 3 * pv_std
    ax2.axhline(y=threshold_line, color='r', linestyle='--', linewidth=2, 
                label=f'3σ threshold: {threshold_line:.2e}')
    
    ax2.set_title('Pairwise Variance')
    ax2.set_xlabel('Time Points')
    ax2.set_ylabel('Variance')
    ax2.grid(True, alpha=0.3)
    ax2.legend()
    ax2.text(0.02, 0.98, f'Outliers: {qc_metrics.get("pairwise_variance_outliers", 0)}',
             transform=ax2.transAxes, verticalalignment='top',
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    # Subplot 3: Rigid Body Motion Parameters
    ax3 = axes[1, 0]
    if motion_params.shape[0] > 0:
        motion_time = np.arange(motion_params.shape[0])
        
        # Plot translations (first 3 columns)
        for i in range(3):
            ax3.plot(motion_time, motion_params[:, i], 
                    label=f'Trans {["X", "Y", "Z"][i]}', linewidth=1)
        
        # Plot rotations (last 3 columns) - convert to degrees if in radians
        for i in range(3, 6):
            rotation_data = motion_params[:, i]
            # Assume radians if values are small
            if np.max(np.abs(rotation_data)) < np.pi:
                rotation_data = np.degrees(rotation_data)
            ax3.plot(motion_time, rotation_data, '--',
                    label=f'Rot {["X", "Y", "Z"][i-3]}', linewidth=1)
    
    ax3.set_title('Rigid Body Motion Parameters')
    ax3.set_xlabel('Time Points')
    ax3.set_ylabel('Translation (mm) / Rotation (deg)')
    ax3.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    ax3.grid(True, alpha=0.3)
    
    # Subplot 4: Framewise Displacement
    ax4 = axes[1, 1]
    if len(fd_values) > 0:
        ax4.plot(fd_time_points, fd_values, 'r-', linewidth=1)
        
        # Add threshold lines
        ax4.axhline(y=max_fd_threshold, color='orange', linestyle='-', linewidth=2,
                   label=f'Max FD threshold: {max_fd_threshold}')
        ax4.axhline(y=mean_fd_threshold, color='purple', linestyle='-', linewidth=2,
                   label=f'Mean FD threshold: {mean_fd_threshold}')
        ax4.axhline(y=fd_20_threshold, color='red', linestyle='--', linewidth=2,
                   label=f'20% threshold: {fd_20_threshold}')
    
    ax4.set_title('Framewise Displacement')
    ax4.set_xlabel('Time Points')
    ax4.set_ylabel('FD (mm)')
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    
    # Add FD metrics text
    if 'max_fd' in qc_metrics:
        fd_text = (f'Max FD: {qc_metrics["max_fd"]:.3f} mm\n'
                  f'Mean FD: {qc_metrics["mean_fd"]:.3f} mm\n'
                  f'Above {fd_20_threshold}: {qc_metrics["fd_percentage_above_threshold"]:.1f}%')
        ax4.text(0.02, 0.98, fd_text, transform=ax4.transAxes, verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    # Adjust layout and save
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()


def batch_motion_qc(subject_list, output_folder, **kwargs):
    """
    Run motion QC for multiple subjects.
    
    Parameters
    ----------
    subject_list : list
        List of subject dictionaries with required fields
    output_folder : str
        Output directory for QC reports
    **kwargs : dict
        Additional parameters for motion_quality_control
        
    Returns
    -------
    batch_results : dict
        Results for all subjects
    """
    batch_results = {}
    
    for i, subject in enumerate(subject_list):
        print(f"\nProcessing subject {i+1}/{len(subject_list)}: {subject['name']}")
        
        try:
            qc_metrics = motion_quality_control(
                output_folder=output_folder,
                realigned_func_path=subject['realigned_func'],
                subject_name=subject['name'],
                **kwargs
            )
            
            batch_results[subject['name']] = qc_metrics
            
        except Exception as e:
            print(f"Error processing subject {subject['name']}: {str(e)}")
            batch_results[subject['name']] = {'error': str(e)}
    
    return batch_results


def create_motion_qc_summary(batch_results, output_folder):
    """
    Create summary report for batch motion QC results.
    
    Parameters
    ----------
    batch_results : dict
        Results from batch_motion_qc
    output_folder : str
        Output directory
    """
    import pandas as pd
    
    # Extract metrics for all subjects
    summary_data = []
    
    for subject_name, metrics in batch_results.items():
        if 'error' not in metrics:
            row = {'subject': subject_name}
            row.update(metrics)
            summary_data.append(row)
    
    if summary_data:
        # Create DataFrame
        df = pd.DataFrame(summary_data)
        
        # Save to CSV
        summary_file = os.path.join(output_folder, 'motion_qc_summary.csv')
        df.to_csv(summary_file, index=False)
        
        # Create summary statistics
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        summary_stats = df[numeric_cols].describe()
        
        stats_file = os.path.join(output_folder, 'motion_qc_statistics.csv')
        summary_stats.to_csv(stats_file)
        
        print(f"Motion QC summary saved: {summary_file}")
        print(f"Motion QC statistics saved: {stats_file}")
    
    else:
        print("No valid motion QC results to summarize")