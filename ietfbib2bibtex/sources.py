#!/usr/bin/env python3

# Copyright (C) 2022 Freie Universität Berlin
#
# This file is subject to the terms and conditions of the GNU Lesser
# General Public License v2.1. See the file LICENSE in the top level
# directory for more detail

"""Bibliography sources"""

import abc
import glob
import logging
import os
import re
import subprocess
import urllib.request

import lxml.etree
import pybtex.database

from . import config

__author__ = "Martine S. Lenders"
__copyright__ = "Copyright 2022 Freie Universität Berlin"
__license__ = "LGPL v2.1"
__email__ = "m.lenders@fu-berlin.de"


class Source(abc.ABC):
    """Base class for a bibliography source."""

    @property
    @abc.abstractmethod
    def remote(self):
        """The remote resource of the bibliography source."""
        raise NotImplementedError()  # pragma: no cover

    @abc.abstractmethod
    def iterate_entries(self):
        """Iterate over all valid entries of the bibliography source."""
        raise NotImplementedError()  # pragma: no cover


class RFCIndexSource(Source):
    """rfc-index.xml source."""

    def __init__(self, rfc_index_config: config.RFCIndexSource):
        self._config = rfc_index_config

    @property
    def remote(self):
        return self._config.remote

    def iterate_entries(self):
        with urllib.request.urlopen(self.remote) as remote:
            tree = lxml.etree.parse(remote)
            root = tree.getroot()

            for element in root.iter("{http://www.rfc-editor.org/rfc-index}rfc-entry"):
                doc_id = element.find(
                    "{http://www.rfc-editor.org/rfc-index}doc-id"
                ).text
                if not re.match(r"RFC\d+", doc_id):
                    # erroneous tagging
                    continue
                title = element.find("{http://www.rfc-editor.org/rfc-index}title").text
                yield re.sub(
                    r"(RFC)0*([1-9][0-9]*)", r"\1-\2", doc_id
                ), pybtex.database.Entry(
                    "techreport",
                    {
                        "title": f"{{{title}}}",
                        "institution": "IETF",
                        "type": "RFC",
                        "number": re.sub(r"RFC0*([1-9][0-9]*)", r"\1", doc_id),
                        "month": (
                            element.find("{http://www.rfc-editor.org/rfc-index}date")
                            .find("{http://www.rfc-editor.org/rfc-index}month")
                            .text
                        ),
                        "year": (
                            element.find("{http://www.rfc-editor.org/rfc-index}date")
                            .find("{http://www.rfc-editor.org/rfc-index}year")
                            .text
                        ),
                    },
                    persons={
                        "author": [
                            pybtex.database.Person(
                                e.find("{http://www.rfc-editor.org/rfc-index}name").text
                            )
                            for e in element.findall(
                                "{http://www.rfc-editor.org/rfc-index}author"
                            )
                        ],
                    },
                )


class BibXMLIDsSource(Source):
    """rsync://rsync.ietf.org/bibxml-ids/ source."""

    def __init__(self, bibxml_ids_source_config: config.BibXMLIDsSource):
        self._config = bibxml_ids_source_config

    @property
    def remote(self):
        return self._config.remote

    @property
    def local(self):
        """The directory for the bibliography source."""
        return self._config.local

    def iterate_entries(self):
        subprocess.check_call(["rsync", "-avcizxL", self.remote, self.local])
        last_unversioned = None
        last_entry = None
        for xml_filename in sorted(glob.iglob(os.path.join(self.local, "*[0-9].xml"))):
            with open(
                xml_filename, encoding="utf-8", errors="xmlcharrefreplace"
            ) as xml:
                try:
                    tree = lxml.etree.parse(xml)
                except lxml.etree.XMLSyntaxError as exc:
                    logging.error("%s, ignoring %s", exc, xml_filename)
                    continue
                root = tree.getroot()
                front = root.find("front")
                series_info = root.find("seriesInfo")
                number = re.sub(r".*-(\d{2})$", r"\1", series_info.get("value"))
                unversioned = re.sub(r"(.*)-\d{2}$", r"\1", series_info.get("value"))
                try:
                    entry = pybtex.database.Entry(
                        "techreport",
                        {
                            "title": f"{{{front.find('title').text}}}",
                            "institution": "IETF",
                            "type": series_info.get("name")
                            + (
                                " -- work in progress"
                                if series_info.get("name") == "Internet-Draft"
                                else ""
                            ),
                            "number": number,
                            "month": front.find("date").get("month"),
                            "year": front.find("date").get("year"),
                        },
                        persons={
                            "author": [
                                pybtex.database.Person(e.get("fullname"))
                                for e in front.findall("author")
                            ],
                        },
                    )
                except pybtex.database.InvalidNameString as exc:
                    logging.error(
                        "%s in author fullname, ignoring %s", exc, xml_filename
                    )
                    continue
                if last_unversioned != unversioned and last_entry is not None:
                    yield last_unversioned, last_entry
                yield series_info.get("value"), entry
                last_unversioned = unversioned
                last_entry = entry
        if last_unversioned is not None and last_entry is not None:
            yield last_unversioned, last_entry
