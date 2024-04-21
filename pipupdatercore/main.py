"""
Copyright (C) 2024  Murdo B. Maclachlan

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


import subprocess
import sys
from smooth_logger import Logger


def print_results(failed: list[str], success: list[str], logger: Logger):
    """
    Outputs the results of the program.

    :param failed: the list of packages that couldn't be updated
    :param success: the list of packages that were successfully updated
    :param logger: the logger instance
    """
    if len(success) > 0:
        logger.new(
            "The following packages were updated (list does not include auto-installed dependencies): "
            + ', '.join(success),
            "INFO"
        )

    if len(failed) > 0:
        logger.new(f"Updates failed for the following packages: {', '.join(failed)}", "INFO")

    if len(success) == 0 and len(failed) == 0:
        logger.new("Nothing to do; did not find any out-of-date packages.", "INFO")


def str_starts_with(string: str, prefixes: list[str]):
    """
    Determines if a given string starts with any one of the given list of prefixes.

    :param string: the string to check for prefixes in
    :param prefixes: the list of prefixes
    :return: whether the string begins with any one of the prefixes
    """
    for prefix in prefixes:
        if string.startswith(prefix):
            return True
    return False


def update_package(package: str, logger: Logger):
    """
    Attempts to update a package with a given name, using subprocess.run() to execute a pip update
    command.

    :param package: the name of the package to update
    :param logger: the logger instance
    """
    try:
        subprocess.run(["pip", "install", "-U", package], capture_output=True)
        success.append(package)
    except Exception as e:
        logger.new(f"Failed to update package: {package} ({e})", "ERROR")
        failed.append(package)


def pipupdater(prefixes: list[str], logger: Logger):
    """
    The main function of pipupdater.

    :param prefixes: a list of prefixes for discarding unneeded lines
    :param logger: the logger instance
    """

    failed: list[str] = []
    success: list[str] = []

    logger.new("Parsing package list...", "INFO")

    for line in sys.stdin:

        # don't try to install debug/error output
        if str_starts_with(line, prefixes):
            # slice here removes new-line character
            logger.new(f"Skipping line: \"{line[:len(line)-1]}\"", "DEBUG") 
            continue
        
        # installation is attempted simply by trying to install whatever comes before the first space
        # in the line, if there are any spaces
        update_package(line.split(" ")[0])

    print_results(failed, success, logger)
