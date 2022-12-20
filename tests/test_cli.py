#!/usr/bin/env python3

# Copyright (C) 2022 Freie Universität Berlin
#
# This file is subject to the terms and conditions of the GNU Lesser
# General Public License v2.1. See the file LICENSE in the top level
# directory for more detail

# pylint: disable=missing-function-docstring
# pylint: disable=missing-module-docstring

import argparse
import sys

import pytest

import ietfbib2bibtex.bib
import ietfbib2bibtex.cli
import ietfbib2bibtex.config

__author__ = "Martine S. Lenders"
__copyright__ = "Copyright 2022 Freie Universität Berlin"
__license__ = "LGPL v2.1"
__email__ = "m.lenders@fu-berlin.de"


@pytest.mark.parametrize(
    "argv, exp_args",
    [
        (["cmd"], argparse.Namespace(config_file=None)),
        (["cmd", "-c", "test.yaml"], argparse.Namespace(config_file="test.yaml")),
    ],
)
def test_parse_args(monkeypatch, argv, exp_args):
    monkeypatch.setattr(sys, "argv", argv)
    args = ietfbib2bibtex.cli.parse_args()
    assert exp_args == args


def test_main(mocker):
    parse_args = mocker.patch.object(ietfbib2bibtex.cli, "parse_args")
    config_from_file = mocker.patch.object(ietfbib2bibtex.config.Config, "from_file")
    create_all_bibtexs = mocker.patch.object(
        ietfbib2bibtex.bib.Bib, "create_all_bibtexs"
    )
    ietfbib2bibtex.cli.main()
    parse_args.assert_called_once_with()
    config_from_file.assert_called_once_with(parse_args.return_value.config_file)
    create_all_bibtexs.assert_called_once_with(config_from_file.return_value)
