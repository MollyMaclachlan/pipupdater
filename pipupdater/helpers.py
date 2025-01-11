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
