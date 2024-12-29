# Copyright (c) 2023 Feud Developers.
# Distributed under the terms of the MIT License (see the LICENSE file).
# SPDX-License-Identifier: MIT
# This source code is part of the Feud project (https://feud.wiki).

"""Overrides for ``click``."""

#: Whether ``rich_click`` is installed or not.
is_rich: bool

try:
    from rich_click import *

    is_rich = True
except (ImportError, ModuleNotFoundError):
    from click import *  # type: ignore[no-redef, assignment]

    is_rich = False

from feud.click.context import *  # noqa: E402
