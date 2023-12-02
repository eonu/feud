# Copyright (c) 2023-2025 Feud Developers.
# Distributed under the terms of the MIT License (see the LICENSE file).
# SPDX-License-Identifier: MIT
# This source code is part of the Feud project (https://feud.wiki).

"""Generation of :py:class:`click.Command`s with automatically
defined :py:class:`click.Argument`s and
:py:class:`click.Option`s based on type hints, and help documentation
based on docstrings.
"""

from __future__ import annotations

import inspect
import typing

import docstring_parser
import pydantic as pyd

try:
    import rich_click as click
except ImportError:
    import click

import feud.exceptions
from feud._internal import _command, _types
from feud.config import Config
from feud.typing import custom

__all__ = ["command"]


@pyd.validate_call
def command(
    func: typing.Callable | None = None,
    /,
    *,
    negate_flags: bool | None = None,
    show_help_defaults: bool | None = None,
    show_help_datetime_formats: bool | None = None,
    pydantic_kwargs: dict[str, typing.Any] | None = None,
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

    pydantic_kwargs:
        Validation settings for
        :py:func:`pydantic.validate_call_decorator.validate_call`.

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
    The generated :py:class:`click.Command`.

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
            pydantic_kwargs=pydantic_kwargs,
        )
        # decorate function
        return get_command(__func, config=cfg, click_kwargs=click_kwargs)

    return decorate(func) if func else decorate


def get_command(
    func: typing.Callable,
    /,
    *,
    config: Config,
    click_kwargs: dict[str, typing.Any],
) -> click.Command:
    if isinstance(func, staticmethod):
        func = func.__func__

    doc: docstring_parser.Docstring = docstring_parser.parse_from_object(func)
    sig: inspect.Signature = inspect.signature(func)
    pass_context: bool = _command.pass_context(sig)

    state = _command.CommandState(
        config=config,
        click_kwargs=click_kwargs,
        context=pass_context,
        is_group=False,
        aliases=getattr(func, "__feud_aliases__", {}),
        overrides={
            override.name: override
            for override in getattr(func, "__click_params__", [])
        },
    )

    for param, spec in sig.parameters.items():
        meta = _command.ParameterSpec()
        meta.hint: type = spec.annotation

        if pass_context and param == _command.CONTEXT_PARAM:
            # skip handling for click.Context argument
            continue

        if spec.kind in (spec.POSITIONAL_ONLY, spec.POSITIONAL_OR_KEYWORD):
            # function positional arguments correspond to CLI arguments
            meta.type = _command.ParameterType.ARGUMENT

            # add the argument
            meta.args = [param]

            # special handling for variable-length collections
            is_collection, base_type = _types.click.is_collection_type(
                meta.hint
            )
            if is_collection:
                meta.kwargs["nargs"] = -1
                meta.hint = base_type

            # special handling for feud.typing.custom counting types
            if custom.is_counter(meta.hint):
                msg = (
                    "Counting may only be used in conjunction with "
                    "keyword-only function parameters (command-line "
                    "options), not positional function parameters "
                    "(command-line arguments)."
                )
                raise feud.exceptions.CompilationError(msg)
        elif spec.kind == spec.KEYWORD_ONLY:
            # function keyword-only arguments correspond to CLI options
            meta.type = _command.ParameterType.OPTION

            # special handling for variable-length collections
            is_collection, base_type = _types.click.is_collection_type(
                meta.hint
            )
            if is_collection:
                meta.kwargs["multiple"] = True
                meta.hint = base_type

            # special handling for feud.typing.custom counting types
            if custom.is_counter(meta.hint):
                meta.kwargs["count"] = True
                meta.kwargs["metavar"] = "COUNT"

            # add the option
            meta.args = [
                _command.get_option(
                    param, hint=meta.hint, negate_flags=config.negate_flags
                )
            ]

            # add aliases - if specified by feud.alias decorator
            for alias in state.aliases.get(param, []):
                meta.args.append(
                    _command.get_alias(
                        alias,
                        hint=meta.hint,
                        negate_flags=config.negate_flags,
                    )
                )

            # add help - fetch parameter description from docstring
            if doc_param := next(
                (p for p in doc.params if p.arg_name == param), None
            ):
                meta.kwargs["help"] = doc_param.description

            # handle option default
            if spec.default is inspect._empty:  # noqa: SLF001
                # specify as required option
                # (if no default provided in function signature)
                meta.kwargs["required"] = True
            else:
                # convert and show default
                # (if default provided in function signature)
                meta.kwargs["show_default"] = config.show_help_defaults
                meta.kwargs["default"] = _types.defaults.convert_default(
                    spec.default
                )

        # add the parameter
        if meta.type == _command.ParameterType.ARGUMENT:
            state.arguments[param] = meta
        elif meta.type == _command.ParameterType.OPTION:
            state.options[param] = meta

    # generate click.Command and attach original function reference
    command = state.decorate(func)
    command.__func__ = func
    return command
