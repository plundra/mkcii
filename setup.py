#!/usr/bin/env python

from setuptools import setup

setup(
    name="mkcii",
    version="0.1-dev",
    py_modules=["mkcii", "easyiso"],
    entry_points={"console_scripts": ["mkcii = mkcii:main"]},
    install_requires=["pycdlib", "PyYAML"],
)
