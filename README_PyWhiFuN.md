# PyWhiFuN: Python White Matter Functional Networks Toolbox

PyWhiFuN is a comprehensive Python toolbox for investigating brain functional connectivity in White Matter (WM) and Gray Matter (GM). This is a Python port of the original MATLAB WhiFuN toolbox.

## Overview

WhiFuN (White Matter Functional Networks) is designed to map functional networks in both white matter and gray matter using resting-state fMRI data. The toolbox provides a complete preprocessing pipeline, network analysis tools, and quality control measures.

## Key Features

- **Complete Preprocessing Pipeline**: Motion correction, segmentation, coregistration, normalization, filtering, and smoothing
- **White Matter Network Analysis**: Specialized tools for analyzing functional connectivity in white matter
- **K-means Clustering**: Advanced clustering algorithms for network identification
- **Quality Control**: Comprehensive QC measures including framewise displacement, motion assessment, and visual inspection tools
- **Cross-platform**: Works on Linux, macOS, and Windows
- **Modern Python**: Built with modern Python libraries (NumPy, SciPy, nibabel, nilearn)

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Install from source

```bash
git clone https://github.com/p-kowadkar/WhiFuN.git
cd WhiFuN
git checkout PyWhiFuN-v3
pip install -e .
```

### Dependencies

The toolbox requires several neuroimaging and scientific computing packages:

- `numpy`, `scipy`, `pandas` - Core scientific computing
- `nibabel`, `nilearn` - Neuroimaging data handling
- `scikit-learn` - Machine learning algorithms
- `matplotlib`, `seaborn` - Visualization
- `nipype` - Neuroimaging pipeline framework (optional, for SPM/FSL integration)

## Quick Start

### Command Line Interface

PyWhiFuN provides a command-line interface for common operations:

```bash
# Calculate framewise displacement
pywhifun calculate-framewise-displacement motion_params.txt

# Perform motion quality control
pywhifun motion-quality-control motion_params.txt --max-fd 0.5

# Get NIfTI file information
pywhifun nifti-info-cmd brain.nii.gz

# Apply Fisher Z transformation
pywhifun fisher-transform 0.3 0.5 0.7

# Create subject configuration template
pywhifun create-subject-config
```

### Python API

```python
import numpy as np
from pywhifun.utils.math_utils import fisher_z, calculate_fd
from pywhifun.preprocessing.motion import motion_qc
from pywhifun.io.nifti_io import nifti_read

# Fisher Z transformation
correlations = np.array([0.3, 0.5, 0.7])
z_values = fisher_z(correlations)

# Calculate framewise displacement
fd = calculate_fd('motion_params.txt')

# Motion quality control
qc_stats = motion_qc('motion_params.txt', max_fd=0.5, mean_fd=0.2)

# Read NIfTI files with proper scaling
volume, header = nifti_read('brain.nii.gz')
```

### Preprocessing Pipeline

```python
from pywhifun.preprocessing.core import WhiFuNPreprocessor, SubjectData

# Define subject data
subject = SubjectData(
    name='subject_001',
    func_folder='/path/to/func',
    func_name='func.nii.gz',
    anat_folder='/path/to/anat',
    anat_name='anat.nii.gz'
)

# Initialize preprocessor
preprocessor = WhiFuNPreprocessor(
    quality_control_path='/path/to/qc',
    smooth_=True,
    smooth_fwhm=4.0,
    filter_check=True,
    normalize=True
)

# Run preprocessing
result = preprocessor.preprocess_subject(subject)
```

## Testing

Run the test suite to verify installation:

```bash
python test_pywhifun.py
```

This will test core functionality including:
- Fisher Z transformation
- Framewise displacement calculation
- Motion quality control
- Correlation functions

## Project Structure

```
pywhifun/
├── __init__.py              # Main package initialization
├── cli.py                   # Command-line interface
├── preprocessing/           # Preprocessing modules
│   ├── core.py             # Main preprocessing pipeline
│   ├── motion.py           # Motion correction and QC
│   ├── segmentation.py     # Anatomical segmentation
│   ├── coregistration.py   # Image coregistration
│   ├── normalization.py    # Spatial normalization
│   ├── filtering.py        # Temporal filtering
│   ├── smoothing.py        # Spatial smoothing
│   └── nuisance.py         # Nuisance regression
├── network_analysis/        # Network analysis tools
├── quality_control/         # Quality control measures
├── visualization/           # Plotting and visualization
├── io/                     # Input/output utilities
│   └── nifti_io.py         # NIfTI file handling
├── utils/                  # Utility functions
│   └── math_utils.py       # Mathematical functions
└── gui/                    # Graphical user interface
```

## Conversion Status

This Python port is currently in development. The following components have been converted:

### ✅ Completed
- Core I/O functions (NIfTI reading/writing with proper scaling)
- Mathematical utilities (Fisher Z, correlation functions, FD calculation)
- Basic preprocessing pipeline structure
- Motion correction and quality control
- Command-line interface
- Project structure and packaging

### 🚧 In Progress
- Complete preprocessing pipeline implementation
- Network analysis functions
- Quality control visualizations
- GUI interface

### 📋 Planned
- Advanced network clustering algorithms
- Statistical analysis tools
- Comprehensive test suite
- Documentation and tutorials

## Original MATLAB Version

This Python toolbox is based on the original MATLAB WhiFuN toolbox:

**Citation:**
Pratik Jain, Andrew M. Michael, Pan Wang, Xin Di, Bharat Biswal; 
WhiFuN: A toolbox to map the white matter functional networks of the human brain. 
Imaging Neuroscience 2025; doi: https://doi.org/10.1162/IMAG.a.3

## Contributing

Contributions are welcome! Please see the original repository for contribution guidelines.

## License

This project maintains the same license as the original WhiFuN toolbox.

## Contact

- Original Author: Pratik Jain (pj44@njit.edu)
- Python Port: OpenHands AI Assistant

## Acknowledgments

- Original WhiFuN development team
- Neuroimaging community for open-source tools
- Python scientific computing ecosystem