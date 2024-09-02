#!/usr/bin/env python3

# Copyright (C) 2022-23 Freie Universität Berlin
# Copyright (C) 2023 HAW Hamburg
#
# This file is subject to the terms and conditions of the GNU Lesser
# General Public License v2.1. See the file LICENSE in the top level
# directory for more details.

"""Configuration"""

import logging
import os
import typing

import platformdirs
import pydantic
import pydantic_settings
import yaml

__author__ = "Martine S. Lenders"
__copyright__ = "Copyright 2022 Freie Universität Berlin"
__license__ = "LGPL v2.1"
__email__ = "m.lenders@fu-berlin.de"

DEFAULT_CONFIG_FILE = os.path.join(
    platformdirs.user_config_dir(), "ietfbib2bibtex", "config.yaml"
)


class Source(pydantic.BaseModel):
    """Base bibliography source configuration validation model."""

    remote: str


class RFCIndexSource(Source):
    """rfc-index.xml source configuration validation model."""

    @pydantic.validator("remote", always=True)
    def _http_uri_remote(cls, value):  # pylint: disable=no-self-argument
        if not value.startswith("http:") and not value.startswith("https:"):
            raise ValueError("'remote' is not a HTTP URL")
        return value


class BibXMLIDsSource(Source):
    """rsync://rsync.ietf.org/bibxml-ids/ source configuration validation model."""

    local: str


class Bib(pydantic.BaseModel):
    """Bibliography configuration validation model."""

    name: str
    rfc_index: typing.Optional[RFCIndexSource] = None
    bibxml_ids: typing.Optional[BibXMLIDsSource] = None

    @pydantic.validator("bibxml_ids", always=True)
    def _mutually_exclusive(cls, value, values):  # pylint: disable=no-self-argument
        if values["rfc_index"] is not None and value:
            raise ValueError("'rfc_index' and 'bibxml_ids' are mutually exclusive.")
        return value


class Config(pydantic_settings.BaseSettings):
    """Base settings validation model."""

    bibpath: typing.Optional[str] = None
    bibs: typing.List[Bib] = []

    @classmethod
    def from_file(cls, config_file: typing.Optional[str] = None):
        """Read configuration from file.

        :param config_file: Name of the configuration file.

        :returns: :py:class:`Config` object generated from file.
        """
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
