# Copyright (c) 2023-2025 Feud Developers.
# Distributed under the terms of the MIT License (see the LICENSE file).
# SPDX-License-Identifier: MIT
# This source code is part of the Feud project (https://feud.wiki).

"""Core utilities for building and running a command-line interface."""

from __future__ import annotations

import contextlib
import inspect
import re
import typing as t
import warnings

try:
    import rich_click as click

    RICH = True
except ImportError:
    import click

    RICH = False

from feud.core.command import *
from feud.core.group import *

__all__ = ["Group", "compile", "command", "run"]

RICH_SETTINGS_REGEX = r"^[A-Z]+(_[A-Z]+)*$"  # screaming snake case
RICH_DEFAULTS = {"SHOW_ARGUMENTS": True}


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

    # set (and unset) feud/user-specified rich-click settings
    with rich_styler(kwargs) as runner_kwargs:
        return runner(args, **runner_kwargs)


@contextlib.contextmanager
def rich_styler(
    original_kwargs: dict[str, t.Any],
    /,
) -> t.Generator[dict[str, t.Any]]:
    """Temporarily applies Feud and user-specified rich-click settings if
    rich-click is installed and rich-click keywords were provided to feud.run.
    """
    kwargs: dict[str, t.Any] = original_kwargs.copy()

    # get rich_click settings
    rich_kwargs: dict[str, t.Any] = {
        k: kwargs.pop(k)
        for k in original_kwargs
        if re.match(RICH_SETTINGS_REGEX, k)
    }

    try:
        if RICH:
            # alias click.rich_click
            rich = click.rich_click

            # check for screaming snake case kwargs that are invalid
            invalid_kwargs: dict[str, t.Any] = {
                k: rich_kwargs.pop(k)
                for k in rich_kwargs.copy()
                if not hasattr(rich, k)
            }

            # warn if any invalid kwargs
            if invalid_kwargs:
                warnings.warn(
                    "The following invalid rich-click settings will be "
                    f"ignored: {invalid_kwargs}.",
                    stacklevel=1,
                )

            # override: true defaults -> feud defaults -> specified settings
            true_defaults = {k: getattr(rich, k) for k in rich_kwargs}
            rich_kwargs = {**true_defaults, **RICH_DEFAULTS, **rich_kwargs}

            # set rich_click settings
            for k, v in rich_kwargs.items():
                setattr(rich, k, v)

            # yield kwargs for the runner
            yield kwargs
        else:
            if rich_kwargs:
                warnings.warn(
                    "rich-click settings were provided to feud.run, "
                    "but rich-click is not installed - these settings "
                    "will be ignored.",
                    stacklevel=1,
                )

            # yield kwargs for the runner
            yield kwargs
    finally:
        # restore rich_click defaults
        if RICH:
            for k, v in true_defaults.items():
                setattr(rich, k, v)
