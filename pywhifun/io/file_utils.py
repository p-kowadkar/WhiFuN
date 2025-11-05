"""
File utility functions for PyWhiFuN
"""

import os
from pathlib import Path
from typing import Union


def complete_filepath(filepath: Union[str, Path]) -> str:
    """
    Complete and normalize a file path.
    
    Parameters
    ----------
    filepath : str or Path
        Input file path.
        
    Returns
    -------
    str
        Completed file path.
    """
    return str(Path(filepath).resolve())


def check_file_exists(filepath: Union[str, Path]) -> bool:
    """
    Check if a file exists.
    
    Parameters
    ----------
    filepath : str or Path
        File path to check.
        
    Returns
    -------
    bool
        True if file exists, False otherwise.
    """
    return Path(filepath).exists()


def create_directories(dirpath: Union[str, Path]) -> None:
    """
    Create directories if they don't exist.
    
    Parameters
    ----------
    dirpath : str or Path
        Directory path to create.
    """
    Path(dirpath).mkdir(parents=True, exist_ok=True)