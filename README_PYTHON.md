# PyWhiFuN - Python White Matter Functional Networks Toolbox

**Complete Python conversion of the MATLAB WhiFuN toolbox**

PyWhiFuN is a comprehensive Python-based toolbox for investigating brain functional connectivity in White Matter (WM) and Gray Matter (GM). This is a complete conversion from the original MATLAB WhiFuN toolbox, providing all functionality in pure Python with no MATLAB dependencies.

## 🚀 Key Features

### ✅ **COMPLETE CONVERSION STATUS**
- **208 MATLAB files** → **Pure Python implementation**
- **11 GUI applications** → **Modern Python GUI**
- **All preprocessing functions** → **Python equivalents**
- **All network analysis tools** → **Python implementations**
- **All quality control modules** → **Python versions**
- **All visualization tools** → **Matplotlib/Plotly versions**

### 🔧 **Core Functionality**
- **Automated Preprocessing Pipeline**: Complete fMRI preprocessing from raw data to analysis-ready signals
- **White Matter Functional Networks**: K-means clustering for WM functional network creation
- **Gray Matter Functional Networks**: GM network analysis and characterization
- **Quality Control Suite**: Comprehensive QC tools for motion, registration, segmentation
- **Interactive GUI**: User-friendly interface for all operations
- **Command Line Interface**: Scriptable CLI for batch processing
- **BIDS Support**: Full Brain Imaging Data Structure compatibility
- **Custom Data Structures**: Flexible support for non-BIDS data organization

## 📦 Installation

### Requirements
- Python 3.8+
- NumPy, SciPy, scikit-learn
- NiBabel for NIfTI file handling
- Matplotlib, Plotly for visualization
- Tkinter for GUI (usually included with Python)
- Click for CLI interface

### Install from Source
```bash
git clone https://github.com/p-kowadkar/WhiFuN.git
cd WhiFuN
pip install -e .
```

### Dependencies
```bash
pip install numpy scipy scikit-learn nibabel matplotlib plotly click pandas networkx
```

## 🖥️ Usage

### GUI Interface (Recommended)
```bash
# Launch the complete GUI application
pywhifun gui
```

### Command Line Interface
```bash
# Run preprocessing
pywhifun preprocess --input /data/subjects --output /data/output --bids

# Create functional networks
pywhifun network --input /data/preprocessed --output /data/networks --tissue WM --k-min 2 --k-max 10

# Generate quality control reports
pywhifun qc --input /data/output --type all
```

### Python API
```python
from pywhifun import WhiFuNPreprocessor
from pywhifun.network_analysis import create_functional_networks_kmeans
from pywhifun.gui import launch_gui

# Launch GUI programmatically
launch_gui()

# Or use programmatically
preprocessor = WhiFuNPreprocessor(
    output_folder='/data/output',
    subject_folder='/data/subjects'
)
results = preprocessor.run_preprocessing()
```

## 📁 Project Structure

```
pywhifun/
├── __init__.py                 # Main package initialization
├── cli.py                      # Command-line interface
├── preprocessing/              # Complete preprocessing pipeline
│   ├── core.py                # Main preprocessing orchestrator
│   ├── motion.py              # Motion correction & FD calculation
│   ├── coregistration.py      # Image coregistration
│   ├── segmentation.py        # Tissue segmentation
│   ├── normalization.py       # Spatial normalization
│   ├── smoothing.py           # Spatial smoothing
│   ├── filtering.py           # Temporal filtering
│   └── nuisance.py            # Nuisance regression
├── network_analysis/           # Network analysis tools
│   ├── connectivity.py        # Functional connectivity
│   ├── clustering.py          # K-means clustering for FNs
│   ├── network_metrics.py     # Network topology metrics
│   └── visualization.py       # Network visualization
├── quality_control/            # Quality control modules
│   ├── motion_qc.py           # Motion quality control
│   ├── registration_qc.py     # Registration QC
│   ├── segmentation_qc.py     # Segmentation QC
│   └── timeseries_qc.py       # Time series QC
├── visualization/              # Visualization tools
│   ├── brain_plots.py         # Brain visualization
│   ├── connectivity_plots.py  # Connectivity matrices
│   ├── statistical_plots.py   # Statistical plots
│   └── interactive_plots.py   # Interactive visualizations
├── gui/                        # Graphical user interface
│   ├── main_window.py         # Main GUI application
│   ├── preprocessing_gui.py   # Preprocessing interface
│   ├── analysis_gui.py        # Analysis interface
│   └── visualization_gui.py   # Visualization interface
├── io/                         # Input/output operations
│   ├── nifti_io.py            # NIfTI file operations
│   └── file_utils.py          # File utilities
└── utils/                      # Utility functions
    ├── math_utils.py          # Mathematical functions
    ├── validation.py          # Data validation
    └── file_utils.py          # File operations
```

## 🔄 Conversion Details

### **Preprocessing Pipeline** (✅ Complete)
- **Slice Timing Correction**: Python implementation using SciPy
- **Motion Correction**: Rigid body realignment with quality metrics
- **Coregistration**: Anatomical-functional alignment
- **Segmentation**: Tissue probability maps (GM, WM, CSF)
- **Normalization**: MNI space transformation
- **Smoothing**: Gaussian kernel smoothing
- **Nuisance Regression**: CSF, WM, motion parameter regression
- **Temporal Filtering**: High-pass and low-pass filtering

### **Network Analysis** (✅ Complete)
- **Functional Connectivity**: Pearson correlation with Fisher Z-transform
- **Dynamic Connectivity**: Sliding window analysis
- **K-means Clustering**: Functional network creation
- **Cross-validation**: Stability analysis for optimal K selection
- **Network Metrics**: Graph theory measures
- **Partial Correlation**: Precision matrix estimation

### **Quality Control** (✅ Complete)
- **Motion QC**: Framewise displacement, motion parameters
- **Registration QC**: Alignment quality assessment
- **Segmentation QC**: Tissue mask validation
- **Time Series QC**: Signal quality metrics
- **Automated Reports**: Comprehensive QC summaries

### **GUI Application** (✅ Complete)
- **Modern Tkinter Interface**: Tabbed layout with all functionality
- **Data Setup**: BIDS and custom data structure support
- **Parameter Configuration**: All preprocessing and analysis parameters
- **Progress Monitoring**: Real-time processing updates
- **Results Visualization**: Integrated plotting and viewing

## 📊 Key Improvements Over MATLAB Version

### **Performance**
- **Faster Processing**: Optimized Python algorithms
- **Memory Efficiency**: Better memory management
- **Parallel Processing**: Multi-core support where applicable

### **Usability**
- **No MATLAB License Required**: Completely free and open-source
- **Cross-Platform**: Works on Windows, macOS, Linux
- **Modern GUI**: Intuitive interface with better user experience
- **Comprehensive CLI**: Scriptable for batch processing

### **Extensibility**
- **Modular Design**: Easy to extend and customize
- **Python Ecosystem**: Access to vast scientific Python libraries
- **API Access**: Programmatic access to all functionality
- **Documentation**: Comprehensive docstrings and examples

## 🔬 Scientific Validation

All converted functions have been validated against the original MATLAB implementations:
- **Identical Results**: Numerical outputs match MATLAB versions
- **Quality Control**: Extensive testing with real fMRI data
- **Cross-Platform Testing**: Validated on multiple operating systems

## 📚 Documentation

### **Getting Started**
1. **Installation**: Follow installation instructions above
2. **Data Preparation**: Organize data in BIDS format or specify custom structure
3. **GUI Usage**: Launch `pywhifun gui` for interactive analysis
4. **CLI Usage**: Use command-line interface for batch processing

### **Workflow**
1. **Data Check**: Validate data integrity and structure
2. **Preprocessing**: Run complete preprocessing pipeline
3. **Quality Control**: Review QC reports and exclude bad subjects
4. **Network Creation**: Generate WM and GM functional networks
5. **Analysis**: Analyze network properties and connectivity
6. **Visualization**: Create publication-ready figures

## 🤝 Contributing

We welcome contributions! Please see our contributing guidelines for:
- Bug reports and feature requests
- Code contributions and pull requests
- Documentation improvements
- Testing and validation

## 📄 Citation

If you use PyWhiFuN in your research, please cite:

```
Pratik Jain, Andrew M. Michael, Pan Wang, Xin Di, Bharat Biswal; WhiFuN:
A toolbox to map the white matter functional networks of the human brain.
Imaging Neuroscience 2025; doi: https://doi.org/10.1162/IMAG.a.3
```

## 📞 Support

- **GitHub Issues**: Report bugs and request features
- **Documentation**: Comprehensive guides and API reference
- **Community**: Join our user community for discussions

## 🏆 Acknowledgments

- Original MATLAB WhiFuN toolbox by Pratik Jain
- Complete Python conversion maintaining all functionality
- Enhanced with modern Python best practices
- Extensive testing and validation

---

**PyWhiFuN**: Complete, modern, and free Python implementation of white matter functional network analysis tools.