# Copyright (c) 2023-2025 Feud Developers.
# Distributed under the terms of the MIT License (see the LICENSE file).
# SPDX-License-Identifier: MIT
# This source code is part of the Feud project (https://feud.wiki).

"""Core utilities for building and running a command-line interface."""

from __future__ import annotations

import inspect
import typing

import pydantic as pyd

try:
    import rich_click as click
except ImportError:
    import click

from feud.core.command import *
from feud.core.group import *

__all__ = ["Group", "compile", "command", "run"]


@pyd.validate_call(config=pyd.ConfigDict(arbitrary_types_allowed=True))
def run(
    obj: type[Group] | click.Command | typing.Callable,
    args: list[str] | None = None,
    /,
    **kwargs: typing.Any,
) -> typing.Any:
    """Run a :py:class:`.Group`, :py:class:`click.Command`,
    or :py:class:`click.Group`.

    If called on a function, it will be decorated with :py:func:`.command`
    using the default configuration to convert it into a
    :py:class:`click.Command` which will then be executed.

    Parameters
    ----------
    obj:
        Group, command or function to run.

    args:
        Command-line arguments provided to
        :py:class:`click.Command`.

    **kwargs:
        Additional keyword arguments provided to
        :py:class:`click.Command`.

    Returns
    -------
    Output of the called :py:class:`click.Command`.

    Examples
    --------
    Running an undecorated function.

    >>> import feud
    >>> def func(*, opt: int) -> int:
    ...     return opt
    >>> feud.run(func, ["--opt", "3"], standalone_mode=False)
    3

    Running a :py:class:`click.Command`.

    >>> import feud
    >>> @feud.command
    ... def func(*, opt: int) -> int:
    ...     return opt
    >>> feud.run(func, ["--opt", "3"], standalone_mode=False)
    3

    Running a :py:class:`.Group`.

    >>> import feud
    >>> class CLI(feud.Group):
    ...     def func(*, opt: int) -> int:
    ...         return opt
    >>> feud.run(CLI, ["func", "--opt", "3"], standalone_mode=False)
    3

    Running a :py:class:`click.Group`.

    >>> import feud
    >>> from feud import click
    >>> class CLI(feud.Group):
    ...     def func(*, opt: int) -> int:
    ...         return opt
    >>> group: click.Group = feud.compile(CLI)
    >>> feud.run(group, ["func", "--opt", "3"], standalone_mode=False)
    3
    """
    if inspect.isclass(obj) or isinstance(obj, click.Command):
        return obj(args, **kwargs)
    return command(obj)(args, **kwargs)
