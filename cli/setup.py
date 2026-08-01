#!/usr/bin/env python3
"""
NFM-X CLI Setup
===============

Setup script for installing NFM-X CLI.

Urdu: NFM-X CLI انسٹال ڧرنے لئے سئ؟ اپ کلیےں
"""

from setuptools import setup, find_packages
import os

# Package metadata
PACKAGE_NAME = "nfm-x-cli"
VERSION = "0.1.0"
DESCRIPTION = "NFM-X: Non-Forgettable Evolutionary AI Memory - Command Line Interface"
AUTHOR = "Abdulraheem Nohari"
AUTHOR_EMAIL = "abdulraheemnohari@gmail.com"
URL = "https://github.com/abdulraheemnohari/NFM-X"
LICENSE = "MIT"

# Read requirements from parent directory
requirements = [
    "argparse",
    "requests",
    "pydantic",
    "httpx",
]

setup(
    name=PACKAGE_NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=open("README.md").read() if os.path.exists("README.md") else DESCRIPTION,
    long_description_content_type="text/markdown",
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    url=URL,
    license=LICENSE,
    
    # Package configuration
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=requirements,
    
    # Additional classifiers
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Utilities",
    ],
    
    # Entry points for CLI
    entry_points={
        "console_scripts": [
            "nfm-x=nfm.cli.main:main",
        ],
    },
    
    # Include non-Python files
    include_package_data=True,
    package_data={
        "": ["*.md", "*.json", "*.yaml", "*.yml"],
    },
)