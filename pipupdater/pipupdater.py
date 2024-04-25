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


def extract_package_details(line: str) -> list[str]:
    """
    Extracts the details of an outdated package from a given line. The details include the package
    name, its current version, and the latest version available to update to.

    :param line: the line to extract details from
    :return: the package name, the current version and the latest version
    """
    # filter out empty characters for strings that use multiple spaces for formatting purposes
    line_parts: list[str] = list(filter(lambda x: x != '', line.split(" ")))

    package: str = line_parts[0]
    current_version: str = None
    latest_version: str = None

    # handles default 'pip list --outdated' format
    if line_parts[1] == "(Current:":
        current_version = line_parts[2]
        latest_version = line_parts[4].removesuffix(")")
    # handles 'pip list --outdated format=columns' format
    else:
        current_version = line_parts[1]
        latest_version = line_parts[2]

    return [package, current_version, latest_version]


def format_results(package_list: list[str]) -> str:
    """
    Formats a given list of packages to display in the following manner:

        package_name (old_version -> new_version)
    
    :param package_list: the list of packages to format
    :return: the formatted list
    """
    results: str = ""

    for package in package_list:
        results += f"   {package[0]} ({package[1]} -> {package[2]})\n"
    
    return results.removesuffix("\n")


def print_results(failed: list[str], success: list[str], logger: Logger) -> None:
    """
    Outputs the results of the program.

    :param failed: the list of packages that couldn't be updated
    :param success: the list of packages that were successfully updated
    :param logger: the logger instance
    """
    if len(success) > 0:
        logger.new(
            "The following packages were updated (list does not include auto-installed dependencies):\n"
            + format_results(success),
            "INFO"
        )

    if len(failed) > 0:
        logger.new(f"Updates failed for the following packages:\n{format_results(failed)}", "INFO")

    if len(success) == 0 and len(failed) == 0:
        logger.new("Nothing to do; did not find any out-of-date packages.", "INFO")


def str_starts_with(string: str, prefixes: list[str]) -> bool:
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


def update_package(package_details: list[str],
                   failed: list[str],
                   success: list[str],
                   logger: Logger) -> None:
    """
    Attempts to update a package with a given name, using subprocess.run() to execute a pip update
    command.

    :param package: the name of the package to update
    :param logger: the logger instance
    """
    try:
        subprocess.run(["pip", "install", "-U", package_details[0]], capture_output=True)
        success.append(package_details)
    except Exception as e:
        logger.new(f"Failed to update package: {package_details[0]} ({e})", "ERROR")
        failed.append(package_details)


def pipupdater(prefixes: list[str], logger: Logger) -> None:
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
        
        package_details: list[str] = extract_package_details(line)

        # installation is attempted simply by trying to install whatever comes before the first space
        # in the line, if there are any spaces
        update_package(package_details, failed, success, logger)

    print_results(failed, success, logger)


def entry_point():
    """
    Entry point for the program. Creates the logger and prefixes array and starts the main function.
    """
    logger: Logger = Logger("pipupdater")
    prefixes: list[str] = ["DEPRECATION", "ERROR", "WARNING", "Package", "-------"]

    pipupdater(prefixes, logger)