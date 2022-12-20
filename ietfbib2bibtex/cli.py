#!/usr/bin/env python3

# Copyright (C) 2022 Freie Universität Berlin
#
# This file is subject to the terms and conditions of the GNU Lesser
# General Public License v2.1. See the file LICENSE in the top level
# directory for more details.

"""CLI definitions"""

import argparse

from ietfbib2bibtex.config import Config
from ietfbib2bibtex.bib import Bib

__author__ = "Martine S. Lenders"
__copyright__ = "Copyright 2022 Freie Universität Berlin"
__license__ = "LGPL v2.1"
__email__ = "m.lenders@fu-berlin.de"


def parse_args():
    """Parse arguments for main command."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-c",
        "--config-file",
        help="A YAML configuration file",
    )
    return parser.parse_args()


def main():
    """The main command: Take IETF bibliographies from configuration file (taken from
    CLI arguments if provided) and create bibtex format files from all of them."""
    args = parse_args()
    config = Config.from_file(args.config_file)
    Bib.create_all_bibtexs(config)
