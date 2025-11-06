"""
Command-line interface for PyWhiFuN
"""

import click
import os
import sys
from pathlib import Path
import json

from .preprocessing.core import WhiFuNPreprocessor, SubjectData, PreprocessingParameters
from .preprocessing.motion import calculate_fd, motion_qc
from .io.nifti_io import nifti_read, nifti_info
from .utils.math_utils import fisher_z


@click.group()
@click.version_option(version='3.0.0')
def main():
    """PyWhiFuN: Python White Matter Functional Networks Toolbox"""
    pass


@main.command()
@click.argument('motion_file', type=click.Path(exists=True))
@click.option('--radius', default=50.0, help='Brain radius for rotation conversion (mm)')
@click.option('--output', '-o', help='Output file for FD values')
def calculate_framewise_displacement(motion_file, radius, output):
    """Calculate framewise displacement from motion parameters."""
    try:
        fd = calculate_fd(motion_file, radius=radius)
        
        click.echo(f"Calculated FD for {len(fd)} timepoints")
        click.echo(f"Mean FD: {fd.mean():.4f} mm")
        click.echo(f"Max FD: {fd.max():.4f} mm")
        click.echo(f"Std FD: {fd.std():.4f} mm")
        
        if output:
            import numpy as np
            np.savetxt(output, fd, fmt='%.6f')
            click.echo(f"FD values saved to: {output}")
            
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)


@main.command()
@click.argument('motion_file', type=click.Path(exists=True))
@click.option('--max-fd', default=0.5, help='Maximum FD threshold')
@click.option('--mean-fd', default=0.2, help='Mean FD threshold')
@click.option('--threshold-pct', default=0.2, help='Percentage threshold for high motion volumes')
def motion_quality_control(motion_file, max_fd, mean_fd, threshold_pct):
    """Perform motion quality control checks."""
    try:
        qc_stats = motion_qc(motion_file, max_fd=max_fd, mean_fd=mean_fd, threshold_pct=threshold_pct)
        
        click.echo("Motion Quality Control Results:")
        click.echo("=" * 40)
        for key, value in qc_stats.items():
            if isinstance(value, float):
                click.echo(f"{key}: {value:.4f}")
            else:
                click.echo(f"{key}: {value}")
        
        # Check if subject passes QC
        passes_qc = (qc_stats['max_fd'] <= max_fd and 
                    qc_stats['mean_fd'] <= mean_fd and
                    qc_stats['pct_above_threshold'] <= threshold_pct * 100)
        
        click.echo("=" * 40)
        if passes_qc:
            click.echo("✓ Subject PASSES motion QC", color='green')
        else:
            click.echo("✗ Subject FAILS motion QC", color='red')
            
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)


@main.command()
@click.argument('nifti_file', type=click.Path(exists=True))
def nifti_info_cmd(nifti_file):
    """Display information about a NIfTI file."""
    try:
        header = nifti_info(nifti_file)
        
        click.echo(f"NIfTI File Information: {nifti_file}")
        click.echo("=" * 50)
        click.echo(f"Data shape: {header.get_data_shape()}")
        click.echo(f"Data type: {header.get_data_dtype()}")
        click.echo(f"Voxel size: {header.get_zooms()}")
        click.echo(f"Scaling slope: {header.get('scl_slope', 'N/A')}")
        click.echo(f"Scaling intercept: {header.get('scl_inter', 'N/A')}")
        
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)


@main.command()
@click.argument('correlation_values', nargs=-1, type=float)
def fisher_transform(correlation_values):
    """Apply Fisher's r-to-z transformation to correlation values."""
    if not correlation_values:
        click.echo("Please provide correlation values as arguments")
        sys.exit(1)
    
    try:
        import numpy as np
        r_values = np.array(correlation_values)
        z_values = fisher_z(r_values)
        
        click.echo("Fisher Z Transformation Results:")
        click.echo("=" * 40)
        for r, z in zip(r_values, z_values):
            click.echo(f"r = {r:.4f} -> Z = {z:.4f}")
            
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)


@main.command()
@click.argument('subject_config', type=click.Path(exists=True))
@click.argument('qc_path', type=click.Path())
@click.option('--overwrite', is_flag=True, help='Overwrite existing files')
@click.option('--n-vol-dis', default=0, help='Number of initial volumes to discard')
@click.option('--max-fd', default=0.5, help='Maximum FD threshold')
@click.option('--mean-fd', default=0.2, help='Mean FD threshold')
@click.option('--smooth', is_flag=True, help='Enable smoothing')
@click.option('--smooth-fwhm', default=4.0, help='FWHM for smoothing kernel')
@click.option('--filter', 'filter_check', is_flag=True, help='Enable temporal filtering')
@click.option('--normalize', is_flag=True, help='Enable normalization to MNI')
def preprocess(subject_config, qc_path, overwrite, n_vol_dis, max_fd, mean_fd, 
               smooth, smooth_fwhm, filter_check, normalize):
    """Run preprocessing pipeline for a subject."""
    try:
        # Load subject configuration
        with open(subject_config, 'r') as f:
            config = json.load(f)
        
        # Create subject data structure
        subject = SubjectData(
            name=config['name'],
            func_folder=config['func_folder'],
            func_name=config['func_name'],
            anat_folder=config['anat_folder'],
            anat_name=config['anat_name']
        )
        
        # Create preprocessing parameters
        params = PreprocessingParameters(
            over_write=overwrite,
            n_vol_dis=n_vol_dis,
            max_fd=max_fd,
            mean_fd=mean_fd,
            smooth_=smooth,
            smooth_fwhm=smooth_fwhm,
            filter_check=filter_check,
            dartel_=not normalize
        )
        
        # Initialize preprocessor
        preprocessor = WhiFuNPreprocessor(qc_path, **params.__dict__)
        
        # Run preprocessing
        click.echo(f"Starting preprocessing for subject: {subject.name}")
        result = preprocessor.preprocess_subject(subject)
        
        if result.error:
            click.echo(f"✗ Preprocessing failed for {subject.name}", color='red')
            sys.exit(1)
        elif result.motion_ex:
            click.echo(f"⚠ Subject {subject.name} excluded due to excessive motion", color='yellow')
        else:
            click.echo(f"✓ Preprocessing completed successfully for {subject.name}", color='green')
            click.echo(f"Final output: {result.current_func_path}")
            
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)


@main.command()
def gui():
    """Launch the PyWhiFuN GUI interface."""
    try:
        from .gui.main_window import launch_gui
        click.echo("Launching PyWhiFuN GUI...")
        launch_gui()
    except ImportError as e:
        click.echo(f"Error: GUI dependencies not available: {str(e)}", err=True)
        click.echo("Please install GUI dependencies: pip install tkinter", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Error launching GUI: {str(e)}", err=True)
        sys.exit(1)


@main.command()
def create_subject_config():
    """Create a template subject configuration file."""
    config = {
        "name": "subject_001",
        "func_folder": "/path/to/functional/data",
        "func_name": "func.nii.gz",
        "anat_folder": "/path/to/anatomical/data", 
        "anat_name": "anat.nii.gz"
    }
    
    output_file = "subject_config_template.json"
    with open(output_file, 'w') as f:
        json.dump(config, f, indent=2)
    
    click.echo(f"Template configuration saved to: {output_file}")
    click.echo("Edit this file with your subject's data paths.")


if __name__ == '__main__':
    main()