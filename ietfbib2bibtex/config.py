#!/usr/bin/env python3

# Copyright (C) 2022 Freie Universität Berlin
#
# This file is subject to the terms and conditions of the GNU Lesser
# General Public License v2.1. See the file LICENSE in the top level
# directory for more details.

import logging
import os
import typing

import appdirs
import pydantic
import yaml

__author__ = "Martine S. Lenders"
__copyright__ = "Copyright 2022 Freie Universität Berlin"
__license__ = "LGPL v2.1"
__email__ = "m.lenders@fu-berlin.de"

DEFAULT_CONFIG_FILE = os.path.join(
    appdirs.user_config_dir(), "ietfbib2bibtex", "config.yaml"
)


class Source(pydantic.BaseModel):
    remote: str


class RFCIndexSource(Source):
    @pydantic.validator("remote", always=True)
    def http_uri_remote(cls, value):  # pylint: disable=no-self-argument
        if not value.startswith("http:") and not value.startswith("https:"):
            raise ValueError("'remote' is not a HTTP URL")
        return value


class BibXMLIDsSource(Source):
    local: str


class Bib(pydantic.BaseModel):
    name: str
    rfc_index: typing.Optional[RFCIndexSource] = None
    bibxml_ids: typing.Optional[BibXMLIDsSource] = None

    @pydantic.validator("bibxml_ids", always=True)
    def mutually_exclusive(cls, value, values):  # pylint: disable=no-self-argument
        if values["rfc_index"] is not None and value:
            raise ValueError("'rfc_index' and 'bibxml_ids' are mutually exclusive.")
        return value


class Config(pydantic.BaseSettings):
    bibpath: typing.Optional[str] = None
    bibs: typing.List[Bib] = []

    @classmethod
    def from_file(cls, config_file: typing.Optional[str] = None):
        if config_file is None:
            try:
                with open(
                    DEFAULT_CONFIG_FILE,
                    encoding="utf-8",
                ) as file:
                    config_dict = yaml.load(file, Loader=yaml.Loader)
            except FileNotFoundError as exc:
                logging.warning("%s", exc)
                config_dict = {}
        else:
            with open(config_file, encoding="utf-8") as file:
                config_dict = yaml.load(file, Loader=yaml.Loader)
        return cls(**config_dict)
