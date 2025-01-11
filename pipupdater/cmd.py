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


import shutil

from .cfg import get_args
from .cfg import get_config
from .models import Logger
from .models import Updater

from argparse import Namespace
from smooth_logger.enums import Categories
from typing import Any


def entry_point():
    """
    Entry point for the program. Creates the logger and prefixes array and starts the main function.
    """
    logger: Logger = Logger("pipupdater")

    args: Namespace = get_args()
    config: dict[str, Any] = get_config(logger)

    logger.edit_scope("DEBUG", Categories.MAXIMUM if args.debug else Categories.DISABLED)
    logger.add_scope("PIPOUTPUT", Categories.SAVE if args.save_pip else Categories.DISABLED)

    updater: Updater = Updater(args, logger, config["prefixes"])
    updater.update_all()
