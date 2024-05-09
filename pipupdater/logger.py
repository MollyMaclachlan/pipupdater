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


import smooth_logger

from os import makedirs
from os.path import isdir
from smooth_logger.enums import Categories


class Logger(smooth_logger.Logger):
    """
    Extends the base smooth_logger.Logger class with some useful methods for formatting and
    printing the final output.
    """
    def __init__(self,
                 program_name: str,
                 config_path: str = None,
                 debug: int = Categories.DISABLED,
                 error: int = Categories.MAXIMUM,
                 fatal: int = Categories.MAXIMUM,
                 info: int = Categories.PRINT,
                 warning: int = Categories.MAXIMUM):
        super().__init__(
            program_name,
            config_path,
            debug,
            error,
            fatal,
            warning,
        )
        self.save_path = self.__define_pip_save_path()

    def format_results(self, package_list: list[str]) -> str:
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

    def __define_pip_save_path(self) -> str:
        """
        Determines the location for the pip log folder and creates it if it does not exist.

        Returns None if an error arises while attempting to create the folder; this results in
        saving pip logs being disabled for that instance of pipupdater.

        :return: the location of the pip log folder
        """
        save_path: str = self._output_path.removesuffix("logs") + "pip_logs"
        if not isdir(save_path):
            self.new(f"Making pip log folder: {save_path}", "INFO")
            try:
                makedirs(save_path, exist_ok=True)
            except Exception as e:
                self.new(
                    "Could not make pip log folder; saving pip output will be disabled for this"
                    + f" instance. Error was: {e}",
                    "ERROR"
                )
                return None
        return save_path

    def print_results(self, failed: list[str], success: list[str]) -> None:
        """
        Outputs the results of the program.

        :param failed: the list of packages that couldn't be updated
        :param success: the list of packages that were successfully updated
        :param logger: the logger instance
        """
        if len(success) > 0:
            self.new(
                "The following packages were updated (list does not include auto-installed "
                + f"dependencies):\n{self.format_results(success)}",
                "INFO"
            )
        if len(failed) > 0:
            self.new(
                f"Updates failed for the following packages:\n{self.format_results(failed)}",
                "INFO"
            )
        if len(success) == 0 and len(failed) == 0:
            self.new("Nothing to do; did not find any out-of-date packages.", "INFO")

    def save_pip_output(self, output: str) -> None:
        """
        Saves a given output string to the pip log file. Should be used only for saving the output
        of pip command subprocesses.

        :param output: the output to save
        """
        if self.save_path and self._scopes["DEBUG"] == Categories.MAXIMUM:
            with open(f"{self.save_path}/pip_log-{self._get_time(date_only=True)}.txt",
                      "at+") as save_file:
                save_file.write(output)
