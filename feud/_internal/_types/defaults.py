# Copyright (c) 2023 Feud Developers.
# Distributed under the terms of the MIT License (see the LICENSE file).
# SPDX-License-Identifier: MIT
# This source code is part of the Feud project (https://feud.wiki).

import datetime
import enum
import typing as t


def convert_default(default: t.Any) -> t.Any:
    if isinstance(default, enum.Enum):
        return convert_default(default.value)
    if isinstance(default, datetime.datetime):
        # this would be caught by isinstance(default, datetime.date) otherwise
        return default
    if isinstance(default, (datetime.date, datetime.time)):
        return str(default)
    if isinstance(default, (set, frozenset, tuple, list)):
        return type(default)(map(convert_default, default))
    return default
