from setuptools import setup, find_packages

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name="pywhifun",
    version="0.1.0",
    packages=find_packages(),
    author="Jules",
    description="A Python conversion of the WhiFuN neuroimaging toolbox.",
    install_requires=requirements,
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
)
