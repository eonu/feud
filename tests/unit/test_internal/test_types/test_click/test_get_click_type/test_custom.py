# Copyright (c) 2023 Feud Developers.
# Distributed under the terms of the MIT License (see the LICENSE file).
# SPDX-License-Identifier: MIT
# This source code is part of the Feud project (https://feud.wiki).

from __future__ import annotations

import click
import pytest

from feud import typing as t
from feud.config import Config


@pytest.mark.parametrize("annotated", [False, True])
@pytest.mark.parametrize(
    ("hint", "expected"),
    [
        # counter types
        (t.Counter, click.INT),
        (
            t.concounter(ge=0, le=3),
            lambda x: isinstance(x, click.IntRange)
            and x.min == 0
            and x.min_open is False
            and x.max == 3
            and x.max_open is False,
        ),
    ],
)
def test_custom(
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
