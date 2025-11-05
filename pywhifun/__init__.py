"""
PyWhiFuN: Python White Matter Functional Networks Toolbox

A comprehensive Python toolbox for investigating brain functional connectivity
in White Matter (WM) and Gray Matter (GM). This is a Python port of the
original MATLAB WhiFuN toolbox.

Author: Converted from MATLAB WhiFuN by OpenHands
Original Author: Pratik Jain
Contact: pj44@njit.edu

Citation:
Pratik Jain, Andrew M. Michael, Pan Wang, Xin Di, Bharat Biswal; 
WhiFuN: A toolbox to map the white matter functional networks of the human brain. 
Imaging Neuroscience 2025; doi: https://doi.org/10.1162/IMAG.a.3
"""

__version__ = "3.0.0"
__author__ = "Pratik Jain (Original), OpenHands (Python Port)"
__email__ = "pj44@njit.edu"

# Import main modules
from . import preprocessing
from . import network_analysis
from . import quality_control
from . import visualization
from . import utils
from . import io

# Main functions
try:
    from .core import WhiFuNProcessor
except ImportError:
    WhiFuNProcessor = None
    
try:
    from .gui import WhiFuNGUI
except ImportError:
    WhiFuNGUI = None

__all__ = [
    'WhiFuNProcessor',
    'WhiFuNGUI',
    'preprocessing',
    'network_analysis', 
    'quality_control',
    'visualization',
    'utils',
    'io'
]