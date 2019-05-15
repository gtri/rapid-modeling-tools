# -*- coding: utf-8 -*-

# Learn more: https://github.com/kennethreitz/setup.py

from setuptools import find_packages, setup

with open("README.md") as f:
    readme = f.read()

with open("LICENSE") as f:
    license = f.read()

setup(
    name="ricks-cafe-american",
    version="0.1.0",
    description="Sample package for Python-Guide.org",
    long_description=readme,
    author="Georgia Tech Research Corporation",
    author_email="support@gtri.gatech.edu",
    url="https://github.com/kennethreitz/samplemod",
    license=license,
    # move the good stuff into a dir called source then pull packages
    # from source
    packages=find_packages(exclude=("test_graph_analysis", "docs")),
    entry_points={
        "console_scripts": ["graph-analysis = graph_analysis.cli:main"]
    },
    install_requires=["pandas", "scipy", "networkx >=2.1", "xlrd >=0.9.0"],
    tests_require=["pytest", "unittest"],
)
