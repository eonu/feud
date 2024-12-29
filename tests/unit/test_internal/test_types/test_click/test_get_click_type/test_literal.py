# Copyright (c) 2023 Feud Developers.
# Distributed under the terms of the MIT License (see the LICENSE file).
# SPDX-License-Identifier: MIT
# This source code is part of the Feud project (https://feud.wiki).

from __future__ import annotations

from collections import deque

import click
import pytest

from feud import typing as t
from feud.config import Config


def annotate(hint: t.Any) -> t.Annotated[t.Any, "annotation"]:
    return t.Annotated[hint, "annotation"]


@pytest.mark.parametrize("annotated", [False, True])
@pytest.mark.parametrize(
    ("hint", "expected"),
    [
        (bool, click.BOOL),
        (bool | None, click.BOOL),
        (annotate(bool) | None, click.BOOL),
        (int, click.INT),
        (int | None, click.INT),
        (annotate(int) | None, click.INT),
        (float, click.FLOAT),
        (float | None, click.FLOAT),
        (annotate(float) | None, click.FLOAT),
        (str, click.STRING),
        (str | None, click.STRING),
        (annotate(str) | None, click.STRING),
        (tuple, None),
        (tuple[int], (click.INT,)),
        (tuple[annotate(int)], (click.INT,)),
        (tuple[int, str], (click.INT, click.STRING)),
        (tuple[annotate(int), annotate(str)], (click.INT, click.STRING)),
        (tuple[int, ...], click.INT),
        (tuple[annotate(int), ...], click.INT),
        (tuple | None, None),
        (annotate(tuple) | None, None),
        (tuple[int] | None, (click.INT,)),
        (tuple[annotate(int)] | None, (click.INT,)),
        (tuple[int, str] | None, (click.INT, click.STRING)),
        (
            tuple[annotate(int), annotate(str)] | None,
            (click.INT, click.STRING),
        ),
        (tuple[int, ...] | None, click.INT),
        (tuple[annotate(int), ...] | None, click.INT),
        (list, None),
        (list[int], click.INT),
        (list[annotate(int)], click.INT),
        (list | None, None),
        (annotate(list) | None, None),
        (list[int] | None, click.INT),
        (list[annotate(int)] | None, click.INT),
        (set, None),
        (set[int], click.INT),
        (set[annotate(int)], click.INT),
        (set | None, None),
        (annotate(set) | None, None),
        (set[int] | None, click.INT),
        (set[annotate(int)] | None, click.INT),
        (frozenset, None),
        (frozenset[int], click.INT),
        (frozenset[annotate(int)], click.INT),
        (frozenset | None, None),
        (annotate(frozenset) | None, None),
        (frozenset[int] | None, click.INT),
        (frozenset[annotate(int)] | None, click.INT),
        (deque, None),
        (deque[int], click.INT),
        (deque[annotate(int)], click.INT),
        (deque | None, None),
        (annotate(deque) | None, None),
        (deque[int] | None, click.INT),
        (deque[annotate(int)] | None, click.INT),
        (type(None), None),
        (annotate(type(None)) | None, None),
    ],
)
def test_literal(
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
