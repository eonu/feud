# Copyright (c) 2023 Feud Developers.
# Distributed under the terms of the MIT License (see the LICENSE file).
# SPDX-License-Identifier: MIT
# This source code is part of the Feud project (https://feud.wiki).

import click

import feud


@feud.command
def func(ctx: feud.click.Context) -> None:
    return ctx


def test_no_validation() -> None:
    """Test that the context argument is not validated,
    and returns the current Click context.
    """
    ctx: click.core.Context = func([], standalone_mode=False)
    assert isinstance(ctx, click.core.Context)
