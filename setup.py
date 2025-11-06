"""
Setup script for PyWhiFuN - Python White Matter Functional Networks Toolbox
"""

from setuptools import setup, find_packages
import os

# Read the README file
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="pywhifun",
    version="3.0.0",
    author="Pratik Jain (Original), OpenHands (Python Port)",
    author_email="pj44@njit.edu",
    description="Python White Matter Functional Networks Toolbox",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/p-kowadkar/WhiFuN",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Medical Science Apps.",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "gui": ["tkinter", "PyQt5", "matplotlib"],
        "dev": ["pytest", "black", "flake8", "mypy"],
        "docs": ["sphinx", "sphinx-rtd-theme"],
    },
    entry_points={
        "console_scripts": [
            "pywhifun=pywhifun.cli:main",
            "whifun-python=pywhifun.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "pywhifun": [
            "templates/*.nii",
            "atlases/*.nii",
            "atlases/*.nii.gz",
            "data/*",
        ],
    },
)