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
import copy
import difflib
import tomlkit
import sys

from .models import Logger

from argparse import Namespace
from importlib.resources import files
from os import makedirs
from os.path import exists
from platformdirs import user_config_dir
from tomlkit import TOMLDocument
from typing import Any, List, Mapping


__version__ = "1.2.0-alpha"


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
    parser.add_argument("-v", "--version", action="version", version=f"%(prog)s {__version__}")

    return parser.parse_args()


def get_config(logger: Logger) -> dict[str, Any]:
    """
    Get user config options. If the pipupdater config file doesn't exist, try to create it using
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
            with open(f"{config_folder}/config.toml", "r") as config_file:
                return import_new_config(tomlkit.load(config_file), config_folder, logger)
        else:
            with open(f"{config_folder}/config.toml", "w+") as config_file:
                default: str = files('pipupdater.data').joinpath('default_config.toml').read_text()
                config_file.write(default)
                return tomlkit.loads(default).unwrap()
    except Exception as e:
        logger.new(
            "Could not find existing config file or make a new one. Using default settings.",
            "WARNING"
        )
        return tomlkit.loads(
            files('pipupdater.data').joinpath('default_config.toml').read_text()
        ).unwrap()


def import_new_config(
        existing: TOMLDocument,
        config_folder: str,
        logger: Logger) -> dict[str, Any]:
    """
    Compares the default_config.toml file with the user's existing configuration file (if one
    exists). Any keys missing from the user's file will be imported from the default and written
    to the existing file.

    New keys within tables and new items within lists are imported, while preserving any the
    user has added. See the deep_update() docstring for more detailed explanations of the exact
    functionality of how new keys are imported.

    :param existing: the existing config options
    :param config_folder: the path to pipupdater's config folder
    :param logger: the logger
    :returns: the modified config options
    """
    modified: bool = False
    original: TOMLDocument = copy.deepcopy(existing)
    default: TOMLDocument = tomlkit.loads(
        files('pipupdater.data').joinpath('default_config.toml').read_text()
    )

    if (default.as_string() != existing.as_string()):
        existing = deep_update(default, existing)

    if (original.as_string() != existing.as_string()):
        logger.new(
            "New configuration options were detected in the default config file. Adding them to"
            + " existing config.",
            "INFO"
        )
        with open(f"{config_folder}/config.toml", "w+") as config_file:
            tomlkit.dump(existing, config_file)
    
    return existing


def deep_update(source: Any, target: Any) -> Any:
    """
    Performs a "deep update" on a TOMLDocument. The standard tomlkit .update() method overwrites
    existing keys with the new versions, losing any configurations the user had entered. This
    instead performs a merge, delving into tables and lists and preserving user settings for
    existing keys.

    This method does not support importing new comments in the following scenarios:
    - Comments in top level whitespace, detached from any key.
    - Comments attached to new keys added to existing tables.

    This is because tomlkit refuses to import comments in those scenarios, for whatever reason.
    Comments attached to keys in new tables *will* be imported, however comments direclty preceeding
    the table itself will not be. I might look into writing a TOML parser that's actually functional
    if I have the time.

    This method is based on the algorithm written by contributor frostming on the tomlkit GitHub
    repository (https://github.com/python-poetry/tomlkit/issues/255#issuecomment-1407551898). My
    version is a disgusting bastardisation with a slightly different functionality.

    :param source: the document from which new values are sourced
    :param target: the document being updated
    :returns: the updated document
    """
    for key, value in source.items():
        if isinstance(value, Mapping) and value:
            if target.get(key) is not None:
                deep_update(value, target.get(key))
            else:
                target[key] = source[key]
        elif isinstance(value, tomlkit.items.Array):
            target[key] = deep_update_array(value, target.get(key))
        else:
            if hasattr(target, 'keys'):
                if key not in target.keys():
                    target[key] = source[key]
            else:
                target[key] = source[key]
    return target


def deep_update_array(
        source: tomlkit.items.Array,
        target: tomlkit.items.Array) -> tomlkit.items.Array:
    """
    Performs a merge on two tomlkit Arrays. This method assumes the Array is multiline and adds
    each new item from the source array to the original as a new line appended with a comma.

    :param source: the array from which new items are sourced
    :param target: the array being updated
    :returns: the merged array
    """
    for item in source:
        if item not in target:
            target.add_line(item, add_comma=True)
    return target
