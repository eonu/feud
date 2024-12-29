# Copyright (c) 2023 Feud Developers.
# Distributed under the terms of the MIT License (see the LICENSE file).
# SPDX-License-Identifier: MIT
# This source code is part of the Feud project (https://feud.wiki).

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TypedDict

__all__ = ["NameDict", "FeudMeta"]


class NameDict(TypedDict):
    command: str | None
    params: dict[str, str]


@dataclass
class FeudMeta:
    aliases: dict[str, list[str]] = field(default_factory=dict)
    envs: dict[str, str] = field(default_factory=dict)
    names: NameDict = field(
        default_factory=lambda: NameDict(command=None, params={})
    )
    sections: dict[str, str] = field(default_factory=dict)
