# Copyright (c) 2023-2025 Feud Developers.
# Distributed under the terms of the MIT License (see the LICENSE file).
# SPDX-License-Identifier: MIT
# This source code is part of the Feud project (https://feud.wiki).

"""Overrides for ``click``."""

try:
    from rich_click import *
except ImportError:
    from click import *

from feud.click.context import *
