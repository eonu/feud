# Copyright (c) 2023 Feud Developers.
# Distributed under the terms of the MIT License (see the LICENSE file).
# SPDX-License-Identifier: MIT
# This source code is part of the Feud project (https://feud.wiki).

"""Core utilities for building and running a command-line interface."""

from __future__ import annotations

import inspect
import sys
import types
import typing as t
import warnings

import feud.exceptions
from feud import click
from feud._internal import _sections
from feud.config import Config
from feud.core.command import *
from feud.core.group import *

__all__ = ["Group", "Section", "build", "command", "run"]

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
    warn: bool = True,
    **click_kwargs: t.Any,
) -> t.Any:
    """Run a function, :py:class:`click.Command`, :py:class:`.Group`,
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

    warn:
        Silences warnings that are produced if ``name``, ``help``, ``epilog``
        or ``config`` are provided when ``obj`` is a :py:class:`click.Command`,
        :py:class:`click.Group` or :py:class:`.Group`.

    **click_kwargs:
        Additional keyword arguments provided to
        :py:class:`click.Command`.

    Returns
    -------
    typing.Any
        Output of the called object.

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
    >>> group: click.Group = CLI.compile()
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
        and all(isinstance(item, str) for item in obj)  # type: ignore[union-attr]
    ):
        args = obj  # type: ignore[assignment]
        obj = None

    # retrieve program name
    prog_name: str | None = click_kwargs.get("prog_name")
    if prog_name is None:
        from click.utils import _detect_program_name

        prog_name = _detect_program_name()

    # get runner
    runner: click.Command | click.Group = build(  # type: ignore[assignment]
        obj,
        name=name,
        help=help,
        epilog=epilog,
        config=config,
        warn=warn,
    )

    # add command and option sections
    if click.is_rich:
        _sections.add_option_sections(runner, context=[prog_name])
        if isinstance(runner, click.Group):
            _sections.add_command_sections(runner, context=[prog_name])

    return runner(args, **click_kwargs)


def get_runner(
    obj: Runner,
    /,
    *,
    name: str | None = None,
    help: str | None = None,  # noqa: A002
    epilog: str | None = None,
    config: Config | None = None,
    convert_func: bool = True,
    warn: bool = True,
) -> click.Command | type[Group]:
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
            items,  # type: ignore[arg-type]
            name=name,
            help=help,
            epilog=epilog,
            config=config,
        )
    if isinstance(obj, t.Iterable):
        items: list[click.Command | type[Group]] = []  # type: ignore[no-redef]
        for v in obj:  # type: ignore[union-attr]
            if isinstance(v, (dict, t.Iterable)):
                msg = (
                    "Groups cannot be constructed from dict or iterable "
                    "objects nested within iterable objects."
                )
                raise feud.exceptions.CompilationError(msg)
            kwargs: dict[str, t.Any] = {}  # type: ignore[no-redef]
            if isinstance(v, types.ModuleType):
                kwargs["config"] = config
            # set convert_func=False to leave @feud.command to group metaclass
            runner = get_runner(v, convert_func=False, warn=False, **kwargs)
            items.append(runner)  # type: ignore[attr-defined]
        return Group.from_iter(
            items,  # type: ignore[arg-type]
            name=name,
            help=help,
            epilog=epilog,
            config=config,
        )
    if isinstance(obj, types.ModuleType):
        return Group.from_module(
            obj, name=name, help=help, epilog=epilog, config=config
        )

    if convert_func:
        kwargs: dict[str, t.Any] = {  # type: ignore[no-redef]
            "name": name,
            "help": help,
            "epilog": epilog,
            "config": config,
        }
        return command(
            obj,
            **{k: v for k, v in kwargs.items() if v is not None},
        )

    return obj  # type: ignore[return-value]


def build(
    obj: Runner | None = None,
    /,
    *,
    name: str | None = None,
    help: str | None = None,  # noqa: A002
    epilog: str | None = None,
    config: Config | None = None,
    warn: bool = True,
    compile: bool = True,  # noqa: A002
) -> click.Command | click.Group | Group:
    """Build a :py:class:`click.Command` or :py:class:`click.Group` from
    a runnable object.

    See :py:func:`.run` for details on runnable objects.

    .. warning::

        ``name``, ``help``, ``epilog`` and ``config`` are ignored if a
        :py:class:`click.Command`, :py:class:`click.Group` or
        :py:class:`.Group` is provided.

    Parameters
    ----------
    obj:
        Runnable group, command or function to run, or :py:obj:`dict`,
        iterable or module of runnable objects.

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

    warn:
        Silences warnings that are produced if ``name``, ``help``, ``epilog``
        or ``config`` are provided when ``obj`` is a :py:class:`click.Command`,
        :py:class:`click.Group` or :py:class:`.Group`.

    compile:
        Whether or not to compile :py:class:`.Group` objects into
        :py:class:`click.Group` objects.

    Returns
    -------
    click.Command | click.Group | Group
        The runnable object.

    Raises
    ------
    CompilationError
        If no runnable object or current module can be determined.

    Examples
    --------
    >>> import feud
    >>> from feud import click
    >>> def func1(*, opt: int) -> int:
    ...     return opt
    >>> def func2(*, opt: float) -> float:
    ...     return opt
    >>> group: click.Group = feud.build([func1, func2])
    >>> isinstance(group, click.Group)
    True
    """
    # use current module if no runner provided
    if obj is None:
        frame = inspect.stack()[1]
        obj = sys.modules.get("__main__", inspect.getmodule(frame[0]))

    if obj is None:
        msg = (
            "Unable to build command - no runnable object was provided "
            "and no current module can be determined in the present context."
        )
        raise feud.CompilationError(msg)

    runner: click.Command | Group = get_runner(  # type: ignore[assignment]
        obj,
        name=name,
        help=help,
        epilog=epilog,
        config=config,
        warn=warn,
    )

    if compile and inspect.isclass(runner) and issubclass(runner, Group):
        return runner.compile()

    return runner
