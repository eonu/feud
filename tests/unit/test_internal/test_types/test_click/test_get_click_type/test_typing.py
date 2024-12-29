# Copyright (c) 2023 Feud Developers.
# Distributed under the terms of the MIT License (see the LICENSE file).
# SPDX-License-Identifier: MIT
# This source code is part of the Feud project (https://feud.wiki).

from __future__ import annotations

import click
import pytest

from feud import typing as t
from feud._internal._types.click import Union
from feud.config import Config


def annotate(hint: t.Any) -> t.Annotated[t.Any, "annotation"]:
    return t.Annotated[hint, "annotation"]


@pytest.mark.parametrize("annotated", [False, True])
@pytest.mark.parametrize(
    ("hint", "expected"),
    [
        (t.Any, None),
        (t.Text, click.STRING),
        (t.Pattern, None),
        (t.Optional[int], click.INT),
        (t.Optional[annotate(int)], click.INT),
        (
            t.Literal["a", "b"],
            lambda x: isinstance(x, click.Choice) and x.choices == ["a", "b"],
        ),
        (t.Tuple, None),
        (t.Tuple[int], (click.INT,)),
        (t.Tuple[annotate(int)], (click.INT,)),
        (t.Tuple[int, str], (click.INT, click.STRING)),
        (t.Tuple[annotate(int), annotate(str)], (click.INT, click.STRING)),
        (t.Tuple[int, ...], click.INT),
        (t.Tuple[annotate(int), ...], click.INT),
        (t.List, None),
        (t.List[int], click.INT),
        (t.List[annotate(int)], click.INT),
        (t.Set, None),
        (t.Set[int], click.INT),
        (t.Set[annotate(int)], click.INT),
        (t.FrozenSet, None),
        (t.FrozenSet[int], click.INT),
        (t.FrozenSet[annotate(int)], click.INT),
        (t.Deque, None),
        (t.Deque[int], click.INT),
        (t.Deque[annotate(int)], click.INT),
        (t.NamedTuple("Point", x=int, y=str), (click.INT, click.STRING)),
        (
            t.NamedTuple("Point", x=annotate(int), y=annotate(str)),
            (click.INT, click.STRING),
        ),
        (
            t.Union[int, str],
            lambda x: isinstance(x, Union)
            and x.types == [click.INT, click.STRING],
        ),
    ],
)
def test_typing(
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
