# Copyright (c) 2023 Feud Developers.
# Distributed under the terms of the MIT License (see the LICENSE file).
# SPDX-License-Identifier: MIT
# This source code is part of the Feud project (https://feud.wiki).

from __future__ import annotations

import enum

import click
import pytest

from feud import typing as t
from feud._internal import _types
from feud.config import Config


@pytest.mark.parametrize("annotated", [False, True])
@pytest.mark.parametrize(
    ("hint", "expected"),
    [
        *[
            (
                path_type,
                lambda x: isinstance(x, click.Path) and x.exists is False,
            )
            for path_type in _types.click.PATH_TYPES
        ],
        (t.UUID, click.UUID),
        (t.Decimal, click.FLOAT),
        (t.Fraction, click.FLOAT),
        (
            t.date,
            lambda x: isinstance(x, _types.click.DateTime)
            and x.name == t.date.__name__,
        ),
        (
            t.time,
            lambda x: isinstance(x, _types.click.DateTime)
            and x.name == t.time.__name__,
        ),
        (
            t.datetime,
            lambda x: isinstance(x, _types.click.DateTime)
            and x.name == t.datetime.__name__,
        ),
        (
            t.timedelta,
            lambda x: isinstance(x, _types.click.DateTime)
            and x.name == t.timedelta.__name__,
        ),
        (
            enum.Enum("TestEnum", {"A": "a", "B": "b"}),
            lambda x: isinstance(x, click.Choice) and x.choices == ["a", "b"],
        ),
    ],
)
def test_stdlib(
    helpers: type,
    *,
    config: Config,
    annotated: bool,
    hint: t.Any,
    expected: click.ParamType | None,
) -> None:
    helpers.check_get_click_type(
        config=config,
        annotated=annotated,
        hint=hint,
        expected=expected,
    )
