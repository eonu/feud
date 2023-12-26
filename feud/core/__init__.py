# Copyright (c) 2023-2025 Feud Developers.
# Distributed under the terms of the MIT License (see the LICENSE file).
# SPDX-License-Identifier: MIT
# This source code is part of the Feud project (https://feud.wiki).

"""Core utilities for building and running a command-line interface."""

from __future__ import annotations

import contextlib
import inspect
import sys
import types
import typing as t
import warnings

try:
    import rich_click as click

    RICH = True
except ImportError:
    import click

    RICH = False

import feud.exceptions
from feud.config import Config
from feud.core.command import *
from feud.core.group import *

__all__ = ["Group", "compile", "command", "run"]

RICH_DEFAULTS = {"SHOW_ARGUMENTS": True}

Runner = t.Union[
    click.Command,
    type[Group],
    t.Callable,
    types.ModuleType,
    # t.Iterable[click.Command | type[Group] | t.Callable | types.ModuleType],
    t.Iterable,
    # dict[str, click.Command | type[Group] | t.Callable | types.ModuleType],
    dict,
    # dict[str, "Runner"],
]


def run(
    obj: Runner | None = None,
    /,
    args: list[str] | None = None,
    *,
    name: str | None = None,
    help: str | None = None,  # noqa: A002
    epilog: str | None = None,
    config: Config | None = None,
    rich_settings: dict[str, t.Any] | None = None,
    warn: bool = True,
    **click_kwargs: t.Any,
) -> t.Any:
    """

    Run a function, :py:class:`click.Command`, :py:class:`.Group`,
    or :py:class:`click.Group`.

    Multiple functions/commands can also be provided as a :py:obj:`dict`,
    iterable or module object. :py:obj:`dict` objects may also be nested.

    If called on a function, it will be automatically decorated with
    :py:func:`.command` using the default configuration to convert it into a
    :py:class:`click.Command` which will then be executed.

    If no runnable object is provided, automatic discovery will be done
    on the current module.

    .. warning::

        ``name``, ``help``, ``epilog`` and ``config`` are ignored if a
        :py:class:`click.Command`, :py:class:`click.Group` or
        :py:class:`.Group` is provided.

    Parameters
    ----------
    obj:
        Runnable group, command or function to run, or :py:obj:`dict`,
        iterable or module of runnable objects.

    args:
        Command-line arguments provided to
        :py:class:`click.Command`.

    name:
        CLI command or group name.

    help:
        CLI command or group description, displayed when ``--help``
        is called. If not set, the docstring of the object will be used if
        available.

    epilog:
        CLI command or group epilog. Appears at the bottom of ``--help``.

    config:
        Configuration for the command or group.

        If a :py:obj:`dict`, iterable or module ``obj`` is provided, the
        configuration will be forwarded to the nested runnable objects within.

    rich_settings:
        Styling options for ``rich-click``, e.g.
        ``{"SHOW_ARGUMENTS": False, "MAX_WIDTH": 60}``.

        See all available options
        `here <https://github.com/ewels/rich-click/blob/e6a3add46c591d49079d440917700dfe28cf0cfe/src/rich_click/rich_click.py#L48-L131>`__
        (as of ``rich-click`` v1.7.2).

    warn:
        Silences warnings that are produced if ``name``, ``help``, ``epilog``
        or ``config`` are provided when ``obj`` is a :py:class:`click.Command`,
        :py:class:`click.Group` or :py:class:`.Group`.

    **click_kwargs:
        Additional keyword arguments provided to
        :py:class:`click.Command`.

    Returns
    -------
    Output of the called object.

    Raises
    ------
    feud.exceptions.CompilationError
        If no runnable object or current module can be determined.

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

    Running a :py:obj:`dict` of functions, commands, groups or modules.

    >>> import feud
    >>> def func1(*, opt: int) -> int:
    ...     return opt
    >>> def func2(*, opt: float) -> float:
    ...     return opt
    >>> feud.run(
    ...     {"f": func1, "g": func2},
    ...     ["g", "--opt", "0.12"],
    ...     standalone_mode=False,
    ... )
    0.12

    Running an iterable of functions, commands, groups or modules.

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

    Running a module of functions, commands or groups.

    >>> import feud
    >>> import types
    >>> feud.run(types)  # doctest: +SKIP

    Running with automatic discovery

    >>> import feud
    >>> def func1(*, opt: int) -> int:
    ...     return opt
    >>> feud.run()  # doctest: +SKIP
    """
    # swap 'obj' and 'args' if empty 'args'
    if (
        args is None
        and isinstance(obj, t.Iterable)
        and not isinstance(obj, dict)
        and all(isinstance(item, str) for item in obj)
    ):
        args = obj
        obj = None

    # use current module if no runner provided
    if obj is None:
        frame = inspect.stack()[1]
        obj = inspect.getmodule(frame[0]) or sys.modules.get("__main__")

    if obj is None:
        msg = (
            "Unable to build command - no runnable object was provided "
            "and no current module can be determined in the present context."
        )
        raise feud.CompilationError(msg)

    # get runner
    runner: click.Command | type[Group] = get_runner(
        obj,
        name=name,
        help=help,
        epilog=epilog,
        config=config,
        warn=warn,
    )

    # set (and unset) feud/user-specified rich-click settings
    with rich_styler(rich_settings or {}):
        return runner(args, **click_kwargs)


def get_runner(
    obj: Runner,
    *,
    name: str | None = None,
    help: str | None = None,  # noqa: A002
    epilog: str | None = None,
    config: Config | None = None,
    convert_func: bool = True,
    warn: bool = True,
) -> click.Command | Group:
    """Generate a :py:class:`click.Command` or :py:class:`.Group` from any
    runnable object.
    """
    provided_kwargs: list[str] = [
        k
        for k, v in {
            "name": name,
            "help": help,
            "epilog": epilog,
            "config": config,
        }.items()
        if v is not None
    ]

    if inspect.isclass(obj) and issubclass(obj, Group):
        if warn and provided_kwargs:
            msg = (
                f"The keyword arguments {provided_kwargs!r} provided to "
                f"feud.run will be ignored.\nConsider redefining the "
                f"specified group with:\n\n\tclass {obj.__name__}(feud.Group"
                f", {', '.join(f'{k}=...' for k in provided_kwargs)})"
                f"\n\nIf this is expected behaviour, this warning can be "
                "silenced by specifying warn=False to feud.run."
            )
            warnings.warn(msg, stacklevel=1)
        return obj
    if isinstance(obj, click.Group):
        if warn and provided_kwargs:
            msg = (
                f"The keyword arguments {provided_kwargs!r} provided to "
                f"feud.run will be ignored.\nConsider providing these "
                f"settings during group construction."
            )
            warnings.warn(msg, stacklevel=1)
        return obj
    if isinstance(obj, click.Command):
        if warn and provided_kwargs:
            msg = (
                f"The keyword arguments {provided_kwargs!r} provided to "
                f"feud.run will be ignored.\nConsider redefining the "
                f"specified command with:\n\n\t@feud.command("
                f"{', '.join(f'{k}=...' for k in provided_kwargs)})"
                f"\n\nIf this is expected behaviour, this warning can be "
                "silenced by specifying warn=False to feud.run."
            )
            warnings.warn(msg, stacklevel=1)
        return obj
    if isinstance(obj, dict):
        items: dict[str, click.Command | type[Group]] = {}
        for k, v in obj.items():
            kwargs: dict[str, t.Any] = {"name": k}
            if isinstance(v, (dict, t.Iterable, types.ModuleType)):
                kwargs["config"] = config
            # set convert_func=False to leave @feud.command to group metaclass
            items[k] = get_runner(v, convert_func=False, warn=False, **kwargs)
        return Group.from_dict(
            items, name=name, help=help, epilog=epilog, config=config
        )
    if isinstance(obj, t.Iterable):
        items: list[click.Command | type[Group]] = []
        for v in obj:
            if isinstance(v, (dict, t.Iterable)):
                msg = (
                    "Groups cannot be constructed from dict or iterable "
                    "objects nested within iterable objects."
                )
                raise feud.exceptions.CompilationError(msg)
            kwargs: dict[str, t.Any] = {}
            if isinstance(v, types.ModuleType):
                kwargs["config"] = config
            # set convert_func=False to leave @feud.command to group metaclass
            runner = get_runner(v, convert_func=False, warn=False, **kwargs)
            items.append(runner)
        return Group.from_iter(
            items, name=name, help=help, epilog=epilog, config=config
        )
    if isinstance(obj, types.ModuleType):
        return Group.from_module(
            obj, name=name, help=help, epilog=epilog, config=config
        )

    if convert_func:
        kwargs: dict[str, t.Any] = {
            "name": name,
            "help": help,
            "epilog": epilog,
            "config": config,
        }
        return command(
            obj,
            **{k: v for k, v in kwargs.items() if v is not None},
        )

    return obj


@contextlib.contextmanager
def rich_styler(
    kwargs: dict[str, t.Any] | None,
    /,
) -> t.Generator[dict[str, t.Any]]:
    """Temporarily applies Feud and user-specified rich-click settings if
    rich-click is installed and rich-click keywords were provided to feud.run.
    """
    # avoid mutating
    kwargs: dict[str, t.Any] = kwargs.copy()

    try:
        if RICH:
            # alias click.rich_click
            rich = click.rich_click

            # check for screaming snake case kwargs that are invalid
            invalid_kwargs: dict[str, t.Any] = {
                k: kwargs.pop(k) for k in kwargs.copy() if not hasattr(rich, k)
            }

            # warn if any invalid kwargs
            if invalid_kwargs:
                msg = (
                    "The following invalid rich-click settings will be "
                    f"ignored: {invalid_kwargs}."
                )
                warnings.warn(msg, stacklevel=1)

            # override: true defaults -> feud defaults -> specified settings
            true_defaults = {k: getattr(rich, k) for k in kwargs}
            kwargs = {**true_defaults, **RICH_DEFAULTS, **kwargs}

            # set rich_click settings
            for k, v in kwargs.items():
                setattr(rich, k, v)

            yield
        else:
            if kwargs:
                msg = (
                    "rich-click settings were provided to feud.run, "
                    "but rich-click is not installed - these settings "
                    "will be ignored."
                )
                warnings.warn(msg, stacklevel=1)

            yield
    finally:
        # restore rich_click defaults
        if RICH:
            for k, v in true_defaults.items():
                setattr(rich, k, v)
