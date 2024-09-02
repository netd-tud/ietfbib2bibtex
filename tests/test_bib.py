#!/usr/bin/env python3

# Copyright (C) 2022 Freie Universität Berlin
#
# This file is subject to the terms and conditions of the GNU Lesser
# General Public License v2.1. See the file LICENSE in the top level
# directory for more detail

# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=missing-module-docstring
# pylint: disable=redefined-outer-name

import pytest

import ietfbib2bibtex.config
import ietfbib2bibtex.sources

from .test_sources import mock_config  # noqa: F401 pylint: disable=unused-import

__author__ = "Martine S. Lenders"
__copyright__ = "Copyright 2022 Freie Universität Berlin"
__license__ = "LGPL v2.1"
__email__ = "m.lenders@fu-berlin.de"


@pytest.mark.parametrize(
    "mock_config, exp_exc",
    [
        pytest.param(
            {"bibs": [{"name": "test", "rfc_index": {"remote": "http://example.org"}}]},
            None,
            id="with rfc_index config",
        ),
        pytest.param(
            {
                "bibpath": "/test/bibs",
                "bibs": [
                    {
                        "name": "test",
                        "bibxml_ids": {"remote": "foobar::test", "local": "test"},
                    }
                ],
            },
            None,
            id="with bibxml_ids config",
        ),
        pytest.param({"bibs": [{"name": "test"}]}, ValueError, id="no source config"),
    ],
    indirect=["mock_config"],
)
def test_bib_init(mock_config, exp_exc):  # noqa: F811
    if exp_exc is None:
        bib = ietfbib2bibtex.bib.Bib(mock_config.bibs[0], mock_config.bibpath)
        assert isinstance(bib.source, ietfbib2bibtex.sources.Source)
    else:
        with pytest.raises(exp_exc):
            ietfbib2bibtex.bib.Bib(mock_config.bibs[0], mock_config.bibpath)


def mock_generator(sequence):
    yield from sequence


@pytest.mark.parametrize(
    "mock_config",
    [
        pytest.param(
            {"bibs": [{"name": "test", "rfc_index": {"remote": "http://example.org"}}]},
            id="with rfc_index config",
        ),
    ],
    indirect=True,
)
def test_bib_iterate(mocker, mock_config):  # noqa: F811
    rfc_iterate = mocker.patch.object(
        ietfbib2bibtex.sources.RFCIndexSource, "iterate_entries"
    )
    rfc_iterate.return_value = mock_generator([0, 1, 2, 3])
    ids_iterate = mocker.patch.object(
        ietfbib2bibtex.sources.BibXMLIDsSource,
        "iterate_entries",
    )
    ids_iterate.return_value = mock_generator([4, 5, 6, 7])
    bib = ietfbib2bibtex.bib.Bib(mock_config.bibs[0], mock_config.bibpath)
    assert isinstance(bib.source, ietfbib2bibtex.sources.RFCIndexSource)
    assert [0, 1, 2, 3] == list(bib.iterate())
    ids_iterate.assert_not_called()


@pytest.mark.parametrize(
    "mock_config",
    [
        pytest.param(
            {"bibs": [{"name": "test", "rfc_index": {"remote": "http://example.org"}}]},
            id="with rfc_index config",
        ),
    ],
    indirect=True,
)
def test_bib_create_bibtex(mocker, mock_config):  # noqa: F811
    rfc_iterate = mocker.patch.object(
        ietfbib2bibtex.sources.RFCIndexSource, "iterate_entries"
    )
    rfc_iterate.return_value = mock_generator(
        [("zero", 0), ("one", 1), ("two", 2), ("three", 3)]
    )
    to_file = mocker.patch("pybtex.database.BibliographyData.to_file")
    bib = ietfbib2bibtex.bib.Bib(mock_config.bibs[0], mock_config.bibpath)
    bib.create_bibtex()
    assert isinstance(bib.source, ietfbib2bibtex.sources.RFCIndexSource)
    to_file.assert_called_once_with("./test.bib", "bibtex")


@pytest.mark.parametrize(
    "mock_config",
    [
        pytest.param(
            {
                "bibpath": "/opt/foobar/",
                "bibs": [
                    {"name": "test", "rfc_index": {"remote": "http://example.org"}},
                    {
                        "name": "test2",
                        "bibxml_ids": {"remote": "foo::bar", "local": "test"},
                    },
                ],
            },
            id="with rfc_index config",
        ),
    ],
    indirect=True,
)
def test_bib_create_all_bibtexs(mocker, mock_config):  # noqa: F811
    rfc_iterate = mocker.patch.object(
        ietfbib2bibtex.sources.RFCIndexSource, "iterate_entries"
    )
    rfc_iterate.return_value = mock_generator(
        [("zero", 0), ("one", 1), ("two", 2), ("three", 3)]
    )
    ids_iterate = mocker.patch.object(
        ietfbib2bibtex.sources.BibXMLIDsSource,
        "iterate_entries",
    )
    ids_iterate.return_value = mock_generator(
        [("four", 4), ("five", 5), ("six", 6), ("seven", 7)]
    )
    to_file = mocker.patch("pybtex.database.BibliographyData.to_file")
    ietfbib2bibtex.bib.Bib.create_all_bibtexs(mock_config)
    to_file.assert_has_calls(
        [
            mocker.call("/opt/foobar/test.bib", "bibtex"),
            mocker.call("/opt/foobar/test2.bib", "bibtex"),
        ],
    )
