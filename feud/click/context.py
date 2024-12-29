# Copyright (c) 2023 Feud Developers.
# Distributed under the terms of the MIT License (see the LICENSE file).
# SPDX-License-Identifier: MIT
# This source code is part of the Feud project (https://feud.wiki).

"""Override for :py:class:`click.Context`."""

from __future__ import annotations

import typing as t

import click
from pydantic_core import core_schema

__all__ = ["Context"]


class Context(click.Context):
    """Override :py:class:`click.Context` for type hints that skip
    validation.

    Example
    -------
    >>> import feud
    >>> from feud import click
    >>> class CLI(feud.Group):
    ...     def f(*, arg: int) -> int:
    ...         return arg
    ...     def g(ctx: click.Context, *, arg: int) -> int:
    ...         return ctx.forward(CLI.f)
    >>> feud.run(CLI, ["g", "--arg", "3"], standalone_mode=False)
    3
    """

    @classmethod
    def __get_pydantic_core_schema__(
        cls: type[Context], _source: t.Any, _handler: t.Any
    ) -> core_schema.CoreSchema:
        """Override pydantic schema to validate as typing.Any."""
        return core_schema.any_schema()
