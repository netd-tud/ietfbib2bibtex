#!/usr/bin/env python3

# Copyright (C) 2022 Freie Universität Berlin
#
# This file is subject to the terms and conditions of the GNU Lesser
# General Public License v2.1. See the file LICENSE in the top level
# directory for more detail

import logging
import os

import pybtex.database

from . import config
from . import sources

__author__ = "Martine S. Lenders"
__copyright__ = "Copyright 2022 Freie Universität Berlin"
__license__ = "LGPL v2.1"
__email__ = "m.lenders@fu-berlin.de"


class Bib:
    def __init__(self, bib_config: config.Bib, bib_path=None):
        self.path = "./" if bib_path is None else bib_path
        self.name = bib_config.name
        if bib_config.rfc_index is not None:
            self.source = sources.RFCIndexSource(bib_config.rfc_index)
        elif bib_config.bibxml_ids is not None:
            self.source = sources.BibXMLIDsSource(bib_config.bibxml_ids)
        else:
            raise ValueError(f"No source configured in {bib_config}")

    def iterate(self):
        return self.source.iterate_entries()

    def create_bibtex(self):
        logging.info("Checking out %s", self.name)
        data = pybtex.database.BibliographyData()
        for entry in self.iterate():
            data.entries[entry[0]] = entry[1]
        logging.debug(
            "Storing %s to %s.bib", self.name, os.path.join(self.path, self.name)
        )
        data.to_file(f"{os.path.join(self.path, self.name)}.bib", "bibtex")

    @classmethod
    def create_all_bibtexs(cls, the_config: config.Config):
        for bib_config in the_config.bibs:
            bib = cls(bib_config, bib_path=the_config.bibpath)
            bib.create_bibtex()
