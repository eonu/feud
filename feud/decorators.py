# Copyright (c) 2023-2025 Feud Developers.
# Distributed under the terms of the MIT License (see the LICENSE file).
# SPDX-License-Identifier: MIT
# This source code is part of the Feud project (https://feud.wiki).

"""Supplementary decorators for modifying commands or their parameters."""

from __future__ import annotations

import inspect
import re
import typing as t
from functools import partial

import pydantic as pyd

from feud.exceptions import CompilationError

__all__ = ["alias"]


@pyd.validate_call
def alias(**aliases: str | list[str]) -> t.Callable:
    """Alias command options.

    Decorates a function by attaching command option alias metadata,
    to be used at compile time to alias :py:class:`click.Option` objects.

    Aliases may only be defined for command-line options, not arguments.
    This translates to keyword-only parameters, i.e. those
    positioned after the ``*`` operator in a function signature.

    Parameters
    ----------
    **aliases:

        Mapping of option names to aliases.

        Option names must be keyword-only parameters defined in
        the signature of the decorated function.

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

    def decorator(
        f: t.Callable, *, aliases: dict[str, str | list[str]]
    ) -> t.Callable:
        # check provided aliases and parameters match
        sig = inspect.signature(f)
        specified = set(aliases.keys())
        received = {
            p.name for p in sig.parameters.values() if p.kind == p.KEYWORD_ONLY
        }
        if specified > received:
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

        f.__feud_aliases__ = {
            k: ([v] if isinstance(v, str) else v) for k, v in aliases.items()
        }
        return f

    return partial(decorator, aliases=aliases)


# def rename(command: str | None = None, /, **params: str) -> t.Callable:
# rename("cmd") renames the command without requiring @feud.command(name="cmd")
