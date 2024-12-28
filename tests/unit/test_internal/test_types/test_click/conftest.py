# Copyright (c) 2023 Feud Developers.
# Distributed under the terms of the MIT License (see the LICENSE file).
# SPDX-License-Identifier: MIT
# This source code is part of the Feud project (https://feud.wiki).

from __future__ import annotations

import typing as t

import pytest


class Helpers:
    @staticmethod
    def annotate(hint: t.Any) -> t.Annotated[t.Any, "annotation"]:
        return t.Annotated[hint, "annotation"]


@pytest.fixture(scope="module")
def helpers() -> type[Helpers]:
    return Helpers
