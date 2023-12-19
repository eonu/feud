# Copyright (c) 2023-2025 Feud Developers.
# Distributed under the terms of the MIT License (see the LICENSE file).
# SPDX-License-Identifier: MIT
# This source code is part of the Feud project (https://feud.wiki).

"""Core utilities for building and running a command-line interface."""

from __future__ import annotations

import inspect
import typing as t

import pydantic as pyd

try:
    import rich_click as click
except ImportError:
    import click

from feud.core.command import *
from feud.core.group import *

__all__ = ["Group", "compile", "command", "run"]


def run(
    obj: t.Union[  # noqa: UP007
        type[Group],
        click.Command,
        t.Callable,
        dict[str, click.Command | t.Callable],
        t.Iterable[click.Command | t.Callable],
    ],
    args: list[str] | None = None,
    /,
    **kwargs: t.Any,
) -> t.Any:
    """Run a :py:class:`.Group`, :py:class:`click.Command`,
    or :py:class:`click.Group`.

    Multiple functions/commands can also be provided as a :py:obj:`dict`
    or iterable object.

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

    Running a :py:obj:`dict` of functions/commands.

    >>> import feud
    >>> def func1(*, opt: int) -> int:
    ...     return opt
    >>> def func2(*, opt: float) -> float:
    ...     return opt
    >>> feud.run(
    ...     {"func1": func1, "func2": func2},
    ...     ["func2", "--opt", "0.12"],
    ...     standalone_mode=False,
    ... )
    0.12

    Running a collection of functions/commands.

    >>> import feud
    >>> def func1(*, opt: int) -> int:
    ...     return opt
    >>> def func2(*, opt: float) -> float:
    ...     return opt
    >>> feud.run(
    ...     (func1, func2),
    ...     ["func2", "--opt", "0.12"],
    ...     standalone_mode=False,
    ... )
    0.12
    """
    runner: t.Callable | None = None

    if inspect.isclass(obj) or isinstance(obj, click.Command):
        runner = obj
    elif isinstance(obj, dict):
        runner = type("group", (Group,), obj)
    elif isinstance(obj, t.Iterable):
        runner = type(
            "group",
            (Group,),
            {
                o.name if isinstance(o, click.Command) else o.__name__: o
                for o in obj
            },
        )
    else:
        runner = command(obj)

    return runner(args, **kwargs)
