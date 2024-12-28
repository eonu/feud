# Copyright (c) 2023 Feud Developers.
# Distributed under the terms of the MIT License (see the LICENSE file).
# SPDX-License-Identifier: MIT
# This source code is part of the Feud project (https://feud.wiki).

"""Officially supported types from the ``typing`` package."""

from __future__ import annotations

import typing

types: list[str] = [
    "Annotated",
    "Any",
    "Deque",
    "FrozenSet",
    "List",
    "Literal",
    "NamedTuple",
    "Optional",
    "Pattern",
    "Set",
    "Text",
    "Tuple",
    "Union",
]

globals().update({attr: getattr(typing, attr) for attr in types})

__all__ = list(types)
