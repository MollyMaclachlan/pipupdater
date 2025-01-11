"""
Copyright (C) 2024-2025  Molly M.B. Maclachlan

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""


import argparse

from .models import Logger

from argparse import Namespace
from importlib.resources import files
from os import makedirs
from os.path import exists
from platformdirs import user_config_dir
from tomllib import load, loads
from typing import Any


VERSION = "1.2.0-alpha"


def get_args() -> Namespace:
    """
    Uses an ArgumentParser to parse in command-line arguments and return the resultant Namespace.

    :returns: the Namespace produced by parsing arguments
    """
    parser: ArgumentParser = argparse.ArgumentParser(
        prog='pipupdater',
        description='A small command-line tool for automatically updating outdated pip packages.'
    )

    parser.add_argument("-d", "--debug", action="store_true", help="enable debug logging")
    parser.add_argument("-s", "--source", action="store", default=None,
                        help="provide a source file containing a list of outdated packages; if"
                        + " left blank, pipupdater will query pip for this list")
    parser.add_argument("-S", "--save-pip", action="store_true",
                        help="save pip output without printing it to console")
    parser.add_argument("-v", "--version", action="version", version=f"%(prog)s {VERSION}")

    return parser.parse_args()


def get_config(logger: Logger) -> dict[str, Any]:
    """Get user config options. If the pipupdater config file doesn't exist, try to create it using
    the default config options. If not possible, use default config options for this run and warn
    the user that no config file exists.

    :param logger: the logger
    :returns: as a dict, the config options
    """
    try:
        config_folder: str = f"{user_config_dir()}/pipupdater"

        if not exists(config_folder):
            makedirs(config_folder)

        if exists(f"{config_folder}/config.toml"):
            with open(f"{config_folder}/config.toml", "rb") as config_file:
                return load(config_file)
        else:
            with open(f"{config_folder}/config.toml", "w+") as config_file:
                default: str = files('pipupdater.data').joinpath('default_config.toml').read_text()
                config_file.write(default)
                return loads(default)
    except Exception as e:
        logger.new(
            "Could not find existing config file or make a new one. Using default settings.",
            "WARNING"
        )
        return loads(files('pipupdater.data').joinpath('default_config.toml').read_text())
