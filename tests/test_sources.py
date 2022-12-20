#!/usr/bin/env python3

# Copyright (C) 2022 Freie Universität Berlin
#
# This file is subject to the terms and conditions of the GNU Lesser
# General Public License v2.1. See the file LICENSE in the top level
# directory for more details.

import datetime
import logging
import re
import os

import pytest

import ietfbib2bibtex.config
import ietfbib2bibtex.sources

# pylint: disable=redefined-outer-name

__author__ = "Martine S. Lenders"
__copyright__ = "Copyright 2022 Freie Universität Berlin"
__license__ = "LGPL v2.1"
__email__ = "m.lenders@fu-berlin.de"

MODULE_PATH = os.path.dirname(os.path.realpath(__file__))


@pytest.fixture
def mock_config(request):
    return ietfbib2bibtex.config.Config(**request.param)


def test_source_init():
    with pytest.raises(TypeError):
        # pylint: disable=abstract-class-instantiated
        ietfbib2bibtex.sources.Source()


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
def test_rfcindexsource_init_remote(mock_config):
    source = ietfbib2bibtex.sources.RFCIndexSource(mock_config.bibs[0].rfc_index)
    assert source.remote == "http://example.org"


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
def test_rfcindexsource_iterate_entries(mocker, mock_config):
    mocker.patch(
        "urllib.request.urlopen",
        mocker.mock_open(
            read_data="""<?xml version="1.0" encoding="UTF-8"?>
<rfc-index xmlns="http://www.rfc-editor.org/rfc-index"
           xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
           xsi:schemaLocation="http://www.rfc-editor.org/rfc-index
                               http://www.rfc-editor.org/rfc-index.xsd">
  <rfc-entry>
    <doc-id>RFC0781</doc-id>
    <title>Specification of the Internet Protocol (IP) timestamp option</title>
    <author>
        <name>Z. Su</name>
    </author>
    <date>
        <month>May</month>
        <year>1981</year>
    </date>
    <format>
        <file-format>ASCII</file-format>
        <file-format>HTML</file-format>
    </format>
    <page-count>1</page-count>
    <current-status>UNKNOWN</current-status>
    <publication-status>UNKNOWN</publication-status>
    <stream>Legacy</stream>
    <doi>10.17487/RFC0781</doi>
  </rfc-entry>
  <rfc-entry>
    <doc-id>RFC9325</doc-id>
    <title>Recommendations for Secure Use of TLS and DTLS</title>
    <author>
      <name>Y. Sheffer</name>
    </author>
    <author>
      <name>P. Saint-Andre</name>
    </author>
    <author>
      <name>T. Fossati</name>
    </author>
    <date>
      <month>November</month>
      <year>2022</year>
    </date>
    <format>
      <file-format>HTML</file-format>
      <file-format>TEXT</file-format>
      <file-format>PDF</file-format>
      <file-format>XML</file-format>
    </format>
    <page-count>34</page-count>
    <draft>draft-ietf-uta-rfc7525bis-11</draft>
    <obsoletes>
      <doc-id>RFC7525</doc-id>
    </obsoletes>
    <updates>
      <doc-id>RFC5288</doc-id>
      <doc-id>RFC6066</doc-id>
    </updates>
    <is-also>
      <doc-id>BCP0195</doc-id>
    </is-also>
    <current-status>BEST CURRENT PRACTICE</current-status>
    <publication-status>BEST CURRENT PRACTICE</publication-status>
    <stream>IETF</stream>
    <area>art</area>
    <doi>10.17487/RFC9325</doi>
  </rfc-entry>
  <rfc-entry>
    <doc-id>BCP0195</doc-id>
  </rfc-entry>
</rfc-index>"""
        ),
    )
    source = ietfbib2bibtex.sources.RFCIndexSource(mock_config.bibs[0].rfc_index)
    entries = list(source.iterate_entries())
    assert len(entries) == 2

    assert entries[0][0] == "RFC-781"
    assert entries[0][1].type == "techreport"
    assert entries[0][1].fields["title"] == (
        "{Specification of the Internet Protocol (IP) timestamp option}"
    )
    assert entries[0][1].fields["institution"] == "IETF"
    assert entries[0][1].fields["type"] == "RFC"
    assert entries[0][1].fields["number"] == "781"
    assert entries[0][1].fields["month"] == "May"
    assert entries[0][1].fields["year"] == "1981"

    assert len(entries[0][1].persons["author"]) == 1
    assert entries[0][1].persons["author"][0].first_names == ["Z."]
    assert not entries[0][1].persons["author"][0].middle_names
    assert entries[0][1].persons["author"][0].last_names == ["Su"]

    assert entries[1][0] == "RFC-9325"
    assert entries[1][1].type == "techreport"
    assert entries[1][1].fields["title"] == (
        "{Recommendations for Secure Use of TLS and DTLS}"
    )
    assert entries[1][1].fields["institution"] == "IETF"
    assert entries[1][1].fields["type"] == "RFC"
    assert entries[1][1].fields["number"] == "9325"
    assert entries[1][1].fields["month"] == "November"
    assert entries[1][1].fields["year"] == "2022"

    assert len(entries[1][1].persons["author"]) == 3
    assert entries[1][1].persons["author"][0].first_names == ["Y."]
    assert not entries[1][1].persons["author"][0].middle_names
    assert entries[1][1].persons["author"][0].last_names == ["Sheffer"]
    assert entries[1][1].persons["author"][1].first_names == ["P."]
    assert not entries[1][1].persons["author"][1].middle_names
    assert entries[1][1].persons["author"][1].last_names == ["Saint-Andre"]
    assert entries[1][1].persons["author"][2].first_names == ["T."]
    assert not entries[1][1].persons["author"][2].middle_names
    assert entries[1][1].persons["author"][2].last_names == ["Fossati"]


@pytest.mark.parametrize(
    "mock_config",
    [
        pytest.param(
            {
                "bibs": [
                    {
                        "name": "test",
                        "bibxml_ids": {"remote": "foobar::test", "local": "test"},
                    }
                ]
            },
            id="with bibxml_ids config",
        ),
    ],
    indirect=True,
)
def test_bibxml_ids_init_remote_local(mock_config):
    source = ietfbib2bibtex.sources.BibXMLIDsSource(mock_config.bibs[0].bibxml_ids)
    assert source.remote == "foobar::test"
    assert source.local == "test"


@pytest.mark.parametrize(
    "mock_config",
    [
        pytest.param(
            {
                "bibs": [
                    {
                        "name": "test",
                        "bibxml_ids": {
                            "remote": "foobar::test",
                            "local": os.path.join(MODULE_PATH, "test_ids"),
                        },
                    }
                ]
            },
            id="with bibxml_ids config",
        ),
    ],
    indirect=True,
)
def test_bibxml_ids_iterate_entries(mocker, mock_config, caplog):
    # pylint: disable=too-many-statements
    check_call = mocker.patch("subprocess.check_call")
    source = ietfbib2bibtex.sources.BibXMLIDsSource(mock_config.bibs[0].bibxml_ids)
    with caplog.at_level(logging.ERROR):
        entries = list(source.iterate_entries())
    check_call.assert_called_once_with(
        ["rsync", "-avcizxL", "foobar::test", os.path.join(MODULE_PATH, "test_ids")]
    )
    assert len(entries) == 5
    assert "draft-ietf-idn-amc-ace-v-00" in caplog.text
    assert "draft-yangcan-cloud-intelligence-web-platform-00" in caplog.text

    for i in range(3):
        if i < 2:
            assert entries[i][0] == f"draft-ietf-core-dns-over-coap-{i:02d}"
            assert entries[i][1].fields["number"] == f"{i:02d}"
        else:
            assert entries[i][0] == "draft-ietf-core-dns-over-coap"
            assert entries[i][1].fields["number"] == "01"
        assert entries[i][1].type == "techreport"
        assert entries[i][1].fields["title"] == "{DNS over CoAP (DoC)}"
        assert entries[i][1].fields["institution"] == "IETF"
        assert entries[i][1].fields["type"] == "Internet-Draft -- work in progress"
        assert entries[i][1].fields["month"] in [
            datetime.datetime(2022, m, 1).strftime("%B") for m in range(1, 13)
        ]
        assert re.match(r"\d{4}", entries[i][1].fields["year"])

        assert len(entries[i][1].persons["author"]) == 5
        assert entries[i][1].persons["author"][0].first_names == ["Martine"]
        assert entries[i][1].persons["author"][0].middle_names == ["Sophie"]
        assert entries[i][1].persons["author"][0].last_names == ["Lenders"]
        assert entries[i][1].persons["author"][1].first_names == ["Christian"]
        assert not entries[i][1].persons["author"][1].middle_names
        assert entries[i][1].persons["author"][1].last_names == ["Amsüss"]
        assert entries[i][1].persons["author"][2].first_names == ["Cenk"]
        assert not entries[i][1].persons["author"][2].middle_names
        assert entries[i][1].persons["author"][2].last_names == ["Gündoğan"]
        assert entries[i][1].persons["author"][3].first_names == ["Thomas"]
        assert entries[i][1].persons["author"][3].middle_names == ["C."]
        assert entries[i][1].persons["author"][3].last_names == ["Schmidt"]
        assert entries[i][1].persons["author"][4].first_names == ["Matthias"]
        assert not entries[i][1].persons["author"][4].middle_names
        assert entries[i][1].persons["author"][4].last_names == ["Wählisch"]

    for i in range(3, 5):
        if i < 4:
            assert entries[i][0] == f"draft-lenders-dns-cns-{i - 3:02d}"
            assert entries[i][1].fields["number"] == f"{i - 3:02d}"
        else:
            assert entries[i][0] == "draft-lenders-dns-cns"
            assert entries[i][1].fields["number"] == "00"
        assert entries[i][1].type == "techreport"
        assert (
            entries[i][1].fields["title"]
            == "{Guidance on DNS Message Composition in Constrained Networks}"
        )
        assert entries[i][1].fields["institution"] == "IETF"
        assert entries[i][1].fields["type"] == "Internet-Draft -- work in progress"
        assert entries[i][1].fields["month"] in [
            datetime.datetime(2022, m, 1).strftime("%B") for m in range(1, 13)
        ]
        assert re.match(r"\d{4}", entries[i][1].fields["year"])

        assert len(entries[i][1].persons["author"]) == 3
        assert entries[i][1].persons["author"][0].first_names == ["Martine"]
        assert entries[i][1].persons["author"][0].middle_names == ["Sophie"]
        assert entries[i][1].persons["author"][0].last_names == ["Lenders"]
        assert entries[i][1].persons["author"][1].first_names == ["Thomas"]
        assert entries[i][1].persons["author"][1].middle_names == ["C."]
        assert entries[i][1].persons["author"][1].last_names == ["Schmidt"]
        assert entries[i][1].persons["author"][2].first_names == ["Matthias"]
        assert not entries[i][1].persons["author"][2].middle_names
        assert entries[i][1].persons["author"][2].last_names == ["Wählisch"]


@pytest.mark.parametrize(
    "mock_config",
    [
        pytest.param(
            {
                "bibs": [
                    {
                        "name": "test",
                        "bibxml_ids": {
                            "remote": "foobar::test",
                            "local": os.path.join(MODULE_PATH, "test_ids"),
                        },
                    }
                ]
            },
            id="with bibxml_ids config",
        ),
    ],
    indirect=True,
)
def test_bibxml_ids_iterate_entries_no_entry(mocker, mock_config):
    check_call = mocker.patch("subprocess.check_call")
    iglob = mocker.patch("glob.iglob")
    iglob.return_value = []
    source = ietfbib2bibtex.sources.BibXMLIDsSource(mock_config.bibs[0].bibxml_ids)
    entries = list(source.iterate_entries())
    assert len(entries) == 0
    check_call.assert_called_once_with(
        ["rsync", "-avcizxL", "foobar::test", os.path.join(MODULE_PATH, "test_ids")]
    )
    iglob.assert_called_once_with(os.path.join(MODULE_PATH, "test_ids", "*[0-9].xml"))
