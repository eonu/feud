# Copyright (c) 2023 Feud Developers.
# Distributed under the terms of the MIT License (see the LICENSE file).
# SPDX-License-Identifier: MIT
# This source code is part of the Feud project (https://feud.wiki).

"""Custom types for counting options."""

from __future__ import annotations

import typing as t

from pydantic import conint

__all__ = ["Counter", "concounter"]


class CounterType:
    pass


#: Keep count of a repeated command-line option.
#:
#: Examples
#: --------
#: >>> import feud
#: >>> from feud.typing import Counter
#: >>> @feud.alias(verbose="-v")
#: ... def func(*, verbose: Counter) -> int:
#: ...     return verbose
#: >>> feud.run(func, ["-vvv"], standalone_mode=False)
#: 3
Counter = t.Annotated[int, CounterType]


def concounter(
    *,
    strict: bool | None = None,
    gt: int | None = None,
    ge: int | None = None,
    lt: int | None = None,
    le: int | None = None,
    multiple_of: int | None = None,
) -> t.Annotated[int, ...]:
    """Wrap :py:obj:`pydantic.types.conint` to allow for constrained counting
    options.

    Parameters
    ----------
    strict:
        Whether to validate the integer in strict mode. Defaults to ``None``.

    gt:
        The value must be greater than this.

    ge:
        The value must be greater than or equal to this.

    lt:
        The value must be less than this.

    le:
        The value must be less than or equal to this.

    multiple_of:
        The value must be a multiple of this.

    Returns
    -------
    The wrapped :py:obj:`pydantic.types.conint` type.

    Examples
    --------
    >>> import feud
    >>> from feud.typing import concounter
    >>> @feud.alias(verbose="-v")
    ... def func(*, verbose: concounter(le=3)) -> int:
    ...     return verbose
    >>> feud.run(func, ["-vvv"], standalone_mode=False)
    3
    """
    return t.Annotated[  # type: ignore[return-value]
        conint(
            strict=strict,
            gt=gt,
            ge=ge,
            lt=lt,
            le=le,
            multiple_of=multiple_of,
        ),
        CounterType,
    ]


def is_counter(hint: t.Any) -> bool:
    args = t.get_args(hint)
    if len(args) > 1:
        return args[0] is int and CounterType in args
    return False
