# Copyright (c) 2023 Feud Developers.
# Distributed under the terms of the MIT License (see the LICENSE file).
# SPDX-License-Identifier: MIT
# This source code is part of the Feud project (https://feud.wiki).

"""Generation of :py:class:`click.Command`s with automatically
defined :py:class:`click.Argument`s and
:py:class:`click.Option`s based on type hints, and help documentation
based on docstrings.
"""

from __future__ import annotations

import typing

import pydantic as pyd

from feud import click
from feud._internal import _command
from feud.config import Config

__all__ = ["command"]


@pyd.validate_call
def command(
    func: typing.Callable | None = None,
    /,
    *,
    negate_flags: bool | None = None,
    show_help_defaults: bool | None = None,
    show_help_datetime_formats: bool | None = None,
    show_help_envvars: bool | None = None,
    pydantic_kwargs: dict[str, typing.Any] | None = None,
    rich_click_kwargs: dict[str, typing.Any] | None = None,
    config: Config | None = None,
    **click_kwargs: typing.Any,
) -> click.Command:
    """Decorate a function and convert it into a
    :py:class:`click.Command` with automatically defined arguments,
    options and help documentation.

    Parameters
    ----------
    func:
        Function used to generate a command.

    negate_flags:
        Whether to automatically add a negated variant for boolean flags.

    show_help_defaults:
        Whether to display default parameter values in command help.

    show_help_datetime_formats:
        Whether to display datetime parameter formats in command help.

    show_help_envvars:
        Whether to display environment variable names in command help.

    pydantic_kwargs:
        Validation settings for
        :py:func:`pydantic.validate_call_decorator.validate_call`.

    rich_click_kwargs:
        Styling settings for ``rich-click``.

        See all available options
        `here <https://github.com/ewels/rich-click/blob/e6a3add46c591d49079d440917700dfe28cf0cfe/src/rich_click/rich_help_configuration.py#L50>`__
        (as of ``rich-click`` v1.7.2).

    config:
        Configuration for the command.

        This argument may be used either in place or in conjunction with the
        other arguments in this function. If a value is provided as both
        an argument to this function, as well as in the provided ``config``,
        the function argument value will take precedence.

    **click_kwargs:
        Keyword arguments to forward :py:func:`click.command`.

    Returns
    -------
    click.Command
        The generated command.

    Examples
    --------
    >>> import feud
    >>> @feud.command(name="my-command", negate_flags=False)
    ... def f(arg: int, *, opt: int) -> tuple[int, int]:
    ...     return arg, opt
    >>> feud.run(f, ["3", "--opt", "-1"], standalone_mode=False)
    (3, -1)

    See Also
    --------
    .run:
        Run a command or group.

    .Config
        Configuration defaults.
    """

    def decorate(__func: typing.Callable, /) -> typing.Callable:
        # sanitize click kwargs
        _command.sanitize_click_kwargs(click_kwargs, name=__func.__name__)
        # create configuration
        cfg = Config._create(  # noqa: SLF001
            base=config,
            negate_flags=negate_flags,
            show_help_defaults=show_help_defaults,
            show_help_datetime_formats=show_help_datetime_formats,
            show_help_envvars=show_help_envvars,
            pydantic_kwargs=pydantic_kwargs,
            rich_click_kwargs=rich_click_kwargs,
        )
        # decorate function
        return _command.get_command(
            __func, config=cfg, click_kwargs=click_kwargs
        )

    return decorate(func) if func else decorate  # type: ignore[return-value]
