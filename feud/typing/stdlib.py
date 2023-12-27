# Copyright (c) 2023-2025 Feud Developers.
# Distributed under the terms of the MIT License (see the LICENSE file).
# SPDX-License-Identifier: MIT
# This source code is part of the Feud project (https://feud.wiki).

"""Officially supported types from the below standard library packages.

- ``collections``
- ``datetime``
- ``decimal``
- ``enum``
- ``pathlib``
- ``uuid``
"""

from __future__ import annotations

import collections
import datetime
import decimal
import enum
import pathlib
import uuid
from itertools import chain
from types import ModuleType

types: dict[ModuleType, list[str]] = {
    collections: ["deque"],
    datetime: ["date", "datetime", "time", "timedelta"],
    decimal: ["Decimal"],
    enum: ["Enum", "IntEnum", "StrEnum"],
    pathlib: ["Path"],
    uuid: ["UUID"],
}

globals().update(
    {
        attr: getattr(module, attr)
        for module, attrs in types.items()
        for attr in attrs
    }
)

__all__ = list(chain.from_iterable(types.values()))
