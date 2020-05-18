# -*- coding: utf-8 -*-
"""
Copyright (C) 2018 by the Georgia Tech Research Institute (GTRI)
This software may be modified and distributed under the terms of
the BSD 3-Clause license. See the LICENSE file for details.
"""

# Learn more: https://github.com/kennethreitz/setup.py

import re
from pathlib import Path

from setuptools import find_packages, setup

NAME = "model_processing"
HERE = Path(__file__).parent
SRC = HERE / "src" / NAME
VERSION_RE = r""".*__version__ = (['"])(\d+\.\d+\.\d+.*)\1.*"""

setup(
    # TODO: non-cute name
    name=NAME,
    version=re.findall(VERSION_RE, (SRC / "_version.py").read_text())[0][1],
    # TODO: better description
    description="Sample package for Python-Guide.org",
    long_description=(HERE / "README.md").read_text(),
    long_description_content_type="text/markdown",
    author="Georgia Tech Research Corporation",
    author_email="ingrid-nerdman@gtri.gatech.edu",
    # TODO: better url
    url="https://github.com/kennethreitz/samplemod",
    license="BSD-3-Clause",
    package_dir={"": "src"},
    packages=find_packages("src"),
    entry_points={
        "console_scripts": ["model-processing = model_processing.cli:main"]
    },
    classifiers=[
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
    ],
    install_requires=["pandas", "scipy", "networkx >=2.3", "xlrd >=0.9.0"],
    tests_require=[
        "pytest-cov",
        "pytest-flake8",
        "pytest-isort",
        "pytest-black",
    ],
    zip_safe=False,
)
