#!/usr/bin/env python3

import os
from setuptools import setup, find_packages

PACKAGE = "ietfbib2bibtex"
LICENSE = "MIT"
URL = "https://github.com/TBD/ietfbib2bibtex"


def get_requirements():
    with open("requirements.txt", encoding="utf-8") as req_file:
        for line in req_file:
            yield line.strip()


def get_version(package):
    """Extract package version without importing file
    Importing cause issues with coverage,
        (modules can be removed from sys.modules to prevent this)
    Importing __init__.py triggers importing rest and then requests too

    Inspired from pep8 setup.py
    """
    with open(os.path.join(package, "__init__.py"), encoding="utf-8") as init_fd:
        for line in init_fd:
            if line.startswith("__version__"):
                return eval(line.split("=")[-1])  # pylint:disable=eval-used
    return None


setup(
    name=PACKAGE,
    version=get_version(PACKAGE),
    description=(
        "ietfbib2bibtex - "
        "A tool to generate bibtex bibliographies from IETF bibliographies"
    ),
    long_description=open("README.rst").read(),
    long_description_content_type="text/x-rst",
    author="Martine S. Lenders",
    author_email="m.lenders@fu-berlin.de",
    url=URL,
    license=LICENSE,
    download_url=URL,
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Intended Audience :: End Users/Desktop",
        "Intended Audience :: Science/Research",
        "Environment :: Console",
        "Topic :: Utilities",
    ],
    install_requires=list(get_requirements()),
    entry_points={
        "console_scripts": [
            "ietfbib2bibtex = ietfbib2bibtex.cli:main",
        ],
    },
    python_requires=">=3.7",
)
