#!/usr/bin/env python3

# Copyright (C) 2022 Freie Universität Berlin
#
# This file is subject to the terms and conditions of the GNU Lesser
# General Public License v2.1. See the file LICENSE in the top level
# directory for more details.

# pylint: disable=missing-function-docstring
# pylint: disable=missing-module-docstring

import logging

import pytest

import ietfbib2bibtex.config

__author__ = "Martine S. Lenders"
__copyright__ = "Copyright 2022 Freie Universität Berlin"
__license__ = "LGPL v2.1"
__email__ = "m.lenders@fu-berlin.de"


def test_source():
    source = ietfbib2bibtex.config.Source(remote="test")
    assert source.remote == "test"


def test_rfc_index_source():
    with pytest.raises(ValueError):
        ietfbib2bibtex.config.RFCIndexSource(remote="foobar://example.org")
    source = ietfbib2bibtex.config.RFCIndexSource(remote="http://example.org")
    assert source.remote == "http://example.org"
    source = ietfbib2bibtex.config.RFCIndexSource(remote="https://example.org")
    assert source.remote == "https://example.org"


def test_bibxml_ids_source():
    source = ietfbib2bibtex.config.BibXMLIDsSource(remote="foobar::test", local="test")
    assert source.remote == "foobar::test"
    assert source.local == "test"


def test_bib():
    with pytest.raises(ValueError):
        ietfbib2bibtex.config.Bib(
            name="test",
            rfc_index=ietfbib2bibtex.config.RFCIndexSource(remote="http://example.org"),
            bibxml_ids=ietfbib2bibtex.config.BibXMLIDsSource(
                remote="foobar::test", local="test"
            ),
        )
    bib = ietfbib2bibtex.config.Bib(
        name="test",
        rfc_index=ietfbib2bibtex.config.RFCIndexSource(remote="http://example.org"),
    )
    assert bib.name == "test"
    assert bib.rfc_index.remote == "http://example.org"
    assert bib.bibxml_ids is None
    bib = ietfbib2bibtex.config.Bib(
        name="test2",
        bibxml_ids=ietfbib2bibtex.config.BibXMLIDsSource(
            remote="foobar::test", local="test"
        ),
    )
    assert bib.name == "test2"
    assert bib.bibxml_ids.remote == "foobar::test"
    assert bib.bibxml_ids.local == "test"
    assert bib.rfc_index is None


def test_config_default_does_not_exist(mocker, caplog):
    mocker.patch.object(ietfbib2bibtex.config, "open", side_effect=FileNotFoundError)
    with caplog.at_level(logging.WARNING):
        conf = ietfbib2bibtex.config.Config.from_file()
    assert conf.bibpath is None
    assert len(conf.bibs) == 0
    assert len(caplog.text) > 0


def test_config_default(mocker, caplog):
    mocker.patch.object(
        ietfbib2bibtex.config,
        "open",
        mocker.mock_open(
            read_data="""bibpath: /opt/foobar
bibs:
- name: test
  rfc_index:
    remote: https://example.org
"""
        ),
    )
    with caplog.at_level(logging.WARNING):
        conf = ietfbib2bibtex.config.Config.from_file()
    assert conf.bibpath == "/opt/foobar"
    assert len(conf.bibs) == 1
    assert len(caplog.text) == 0
    assert conf.bibs[0].name == "test"
    assert conf.bibs[0].rfc_index.remote == "https://example.org"


def test_config_with_filename(mocker, caplog):
    mocker.patch.object(
        ietfbib2bibtex.config,
        "open",
        mocker.mock_open(
            read_data="""bibs:
- name: test
  rfc_index:
    remote: https://example.org
- name: test2
  bibxml_ids:
    remote: foobar::test/
    local: test/
"""
        ),
    )
    with caplog.at_level(logging.WARNING):
        conf = ietfbib2bibtex.config.Config.from_file("test.yaml")
    assert conf.bibpath is None
    assert len(conf.bibs) == 2
    assert len(caplog.text) == 0
    assert conf.bibs[0].name == "test"
    assert conf.bibs[0].rfc_index.remote == "https://example.org"
    assert conf.bibs[1].name == "test2"
    assert conf.bibs[1].bibxml_ids.remote == "foobar::test/"
    assert conf.bibs[1].bibxml_ids.local == "test/"
