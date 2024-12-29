# Copyright (c) 2023 Feud Developers.
# Distributed under the terms of the MIT License (see the LICENSE file).
# SPDX-License-Identifier: MIT
# This source code is part of the Feud project (https://feud.wiki).

"""Supplementary decorators for modifying commands or their parameters."""

from __future__ import annotations

import inspect
import re
import typing as t

import pydantic as pyd

from feud._internal import _meta
from feud.exceptions import CompilationError

__all__ = ["alias", "env", "rename", "section"]


@pyd.validate_call
def alias(**aliases: str | list[str]) -> t.Callable:
    """Alias command options.

    Decorates a function by attaching command option alias metadata,
    to be used at compile time to alias :py:class:`click.Option` objects.

    Aliases may only be defined for command-line options, not arguments.

    Parameters
    ----------
    **aliases:
        Mapping of option names to aliases.
        Option names must be keyword-only parameters in the decorated
        function signature.

    Returns
    -------
    Function decorated with command option alias metadata.

    Examples
    --------
    Aliasing a single option.

    >>> import feud
    >>> @feud.alias(verbose="-v")
    ... def func(*, verbose: bool) -> bool:
    ...     return verbose
    >>> feud.run(func, ["--verbose"], standalone_mode=False)
    True
    >>> feud.run(func, ["-v"], standalone_mode=False)
    True
    >>> feud.run(func, ["--no-verbose"], standalone_mode=False)
    False
    >>> feud.run(func, ["--no-v"], standalone_mode=False)
    False

    Aliasing a single option with multiple aliases.

    >>> import feud
    >>> @feud.alias(verbose=["-v", "-V"])
    >>> def func(*, verbose: bool) -> bool:
    ...     return verbose
    >>> feud.run(func, ["-v"], standalone_mode=False)
    True
    >>> feud.run(func, ["--no-v"], standalone_mode=False)
    False
    >>> feud.run(func, ["-V"], standalone_mode=False)
    True
    >>> feud.run(func, ["--no-V"], standalone_mode=False)
    False

    Aliasing multiple options.

    >>> import feud
    >>> from feud.typing import Counter
    >>> @feud.alias(verbose="-v", stringify="-s")
    ... def func(*, verbose: Counter, stringify: bool) -> int | str:
    ...     return f"Verbose level: {verbose}" if stringify else verbose
    >>> feud.run(func, ["-vvvs"], standalone_mode=False)
    "Verbose level: 3"
    >>> feud.run(func, ["-v", "-v", "-v", "-s"], standalone_mode=False)
    "Verbose level: 3"
    >>> feud.run(func, ["-vvv", "--no-s"], standalone_mode=False)
    3
    """

    def decorator(f: t.Callable) -> t.Callable:
        # check provided aliases and parameters match
        sig = inspect.signature(f)
        specified = set(aliases.keys())
        received = {
            p.name for p in sig.parameters.values() if p.kind == p.KEYWORD_ONLY
        }
        if len(specified - received) > 0:
            msg = (
                f"Arguments provided to 'alias' decorator must "
                f"also be keyword parameters for function {f.__name__!r}. "
                f"Received extra arguments: {specified - received!r}."
            )
            raise CompilationError(msg)

        # check alias uniqueness
        flat_aliases: list[str] = []
        for alias in aliases.values():
            if isinstance(alias, str):
                flat_aliases.append(alias)
            else:
                flat_aliases.extend(alias)

        if len(set(flat_aliases)) < len(flat_aliases):
            msg = f"Aliases for function {f.__name__!r} must be unique."
            raise CompilationError(msg)

        # check alias formats
        fmt = r"^-[a-zA-Z0-9]$"
        invalid = [alias for alias in flat_aliases if not re.match(fmt, alias)]
        if invalid:
            msg = (
                f"Invalid aliases provided for function {f.__name__!r}. "
                f"Aliases must be of the format {fmt!r}."
            )
            raise CompilationError(msg)

        aliases_ = {
            k: ([v] if isinstance(v, str) else v) for k, v in aliases.items()
        }

        if meta := getattr(f, "__feud__", None):
            meta.aliases = aliases_
        else:
            f.__feud__ = _meta.FeudMeta(  # type: ignore[attr-defined]
                aliases=aliases_,
            )

        return f

    return decorator


def env(**envs: str) -> t.Callable:
    """Specify environment variable inputs for command options.

    Decorates a function by attaching command option environment variable
    metadata, to be used at compile time by :py:class:`click.Option` objects.

    Environment variables may only be defined for command-line options, not
    arguments. This translates to keyword-only parameters, i.e. those
    positioned after the ``*`` operator in a function signature.

    Parameters
    ----------
    **envs:
        Mapping of option names to environment variables.
        Option names must be keyword-only parameters in the decorated
        function signature.

    Returns
    -------
    Function decorated with command option environment variable metadata.

    Examples
    --------
    Using an environment variable for a single option.

    >>> import os
    >>> import feud
    >>> @feud.env(token="TOKEN")
    ... def func(*, token: str) -> str:
    ...     return token
    >>> os.environ["TOKEN"] = "Hello world!"
    >>> feud.run(func, [], standalone_mode=False)
    "Hello World!"

    Using environment variables for multiple options.

    >>> import os
    >>> import feud
    >>> @feud.env(token="TOKEN", key="API_KEY")
    >>> def func(*, token: str, key: str) -> tuple[str, str]:
    ...     return token, key
    >>> os.environ["TOKEN"] = "Hello world!"
    >>> os.environ["API_KEY"] = "This is a secret key."
    >>> feud.run(func, [], standalone_mode=False)
    ("Hello world!", "This is a secret key.")
    """

    def decorator(f: t.Callable) -> t.Callable:
        # check provided envs and parameters match
        sig = inspect.signature(f)
        specified = set(envs.keys())
        received = {
            p.name for p in sig.parameters.values() if p.kind == p.KEYWORD_ONLY
        }
        if len(specified - received) > 0:
            msg = (
                f"Arguments provided to 'env' decorator must "
                f"also be keyword parameters for function {f.__name__!r}. "
                f"Received extra arguments: {specified - received!r}."
            )
            raise CompilationError(msg)

        if meta := getattr(f, "__feud__", None):
            meta.envs = envs
        else:
            f.__feud__ = _meta.FeudMeta(  # type: ignore[attr-defined]
                envs=envs,
            )

        return f

    return decorator


def rename(command: str | None = None, /, **params: str) -> t.Callable:
    """Rename a command and/or its parameters.

    Useful for command/parameter names that use hyphens, reserved Python
    keywords or in-built function names.

    Parameters
    ----------
    command:
        New command name. If ``None``, the command is not renamed.

    **params:
        Mapping of parameter names to new names.
        Parameter names must be defined in the decorated function signature.

    Returns
    -------
    Function decorated with command/parameter renaming metadata.

    Examples
    --------
    Renaming a command.

    >>> import feud
    >>> @feud.rename("my-func")
    ... def my_func(arg_1: int, *, opt_1: str, opt_2: bool):
    ...     pass

    Renaming parameters.

    >>> import feud
    >>> @feud.rename(arg_1="arg-1", opt_2="opt-2")
    ... def my_func(arg_1: int, *, opt_1: str, opt_2: bool):
    ...     pass

    Renaming a command and parameters.

    >>> import feud
    >>> @feud.rename("my-func", arg_1="arg-1", opt_2="opt-2")
    ... def my_func(arg_1: int, *, opt_1: str, opt_2: bool):
    ...     pass
    """

    def decorator(f: t.Callable) -> t.Callable:
        # check provided names and parameters match
        sig = inspect.signature(f)
        specified = set(params.keys())
        received = {p.name for p in sig.parameters.values()}
        if len(specified - received) > 0:
            msg = (
                f"Arguments provided to 'env' decorator must "
                f"also be parameters for function {f.__name__!r}. "
                f"Received extra arguments: {specified - received!r}."
            )
            raise CompilationError(msg)

        names = _meta.NameDict(command=command, params=params)

        if meta := getattr(f, "__feud__", None):
            meta.names = names
        else:
            f.__feud__ = _meta.FeudMeta(  # type: ignore[attr-defined]
                names=names,
            )

        return f

    return decorator


def section(**options: str) -> t.Callable:
    """Partition command options into sections.

    These sections are displayed on the group help page if ``rich-click``
    is installed.

    Parameters
    ----------
    **options:
        Mapping of option names to section names.
        Option names must be keyword-only parameters in the decorated
        function signature.

    Returns
    -------
    Function decorated with section metadata.

    Examples
    --------
    >>> import feud
    >>> @feud.section(
    ...     opt1="Basic options",
    ...     opt2="Advanced options",
    ...     opt3="Basic options",
    ... )
    ... def my_func(arg1: int, *, opt1: str, opt2: bool, opt3: float):
    ...     pass
    """

    def decorator(f: t.Callable) -> t.Callable:
        # check provided names and parameters match
        sig = inspect.signature(f)
        specified = set(options.keys())
        received = {
            p.name for p in sig.parameters.values() if p.kind == p.KEYWORD_ONLY
        }
        if len(specified - received) > 0:
            msg = (
                f"Arguments provided to 'section' decorator must "
                f"also be keyword parameters for function {f.__name__!r}. "
                f"Received extra arguments: {specified - received!r}."
            )
            raise CompilationError(msg)

        sections = options.copy()

        if meta := getattr(f, "__feud__", None):
            meta.sections = sections
        else:
            f.__feud__ = _meta.FeudMeta(  # type: ignore[attr-defined]
                sections=sections,
            )

        return f

    return decorator
