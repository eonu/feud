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
from feud._internal import _command, _docstring, _types
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
            show_help_envvars=show_help_envvars,
            pydantic_kwargs=pydantic_kwargs,
            rich_click_kwargs=rich_click_kwargs,
        )
        # decorate function
        return get_command(__func, config=cfg, click_kwargs=click_kwargs)

    return decorate(func) if func else decorate


def build_command_state(  # noqa: PLR0915
    state: _command.CommandState, *, func: callable, config: Config
) -> None:
    doc: docstring_parser.Docstring
    if state.is_group:
        doc = docstring_parser.parse(state.click_kwargs.get("help", ""))
    else:
        doc = docstring_parser.parse_from_object(func)

    state.description: str | None = _docstring.get_description(doc)

    sig: inspect.Signature = inspect.signature(func)

    for param, spec in sig.parameters.items():
        meta = _command.ParameterSpec()
        meta.hint: type = spec.annotation

        # get renamed parameter if @feud.rename used
        name: str = state.names["params"].get(param, param)

        if _command.pass_context(sig) and param == _command.CONTEXT_PARAM:
            # skip handling for click.Context argument
            state.pass_context = True

        if spec.kind in (spec.POSITIONAL_ONLY, spec.POSITIONAL_OR_KEYWORD):
            # function positional arguments correspond to CLI arguments
            meta.type = _command.ParameterType.ARGUMENT

            # add the argument
            meta.args = [name]

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

            # handle option default
            if spec.default is inspect._empty:  # noqa: SLF001
                # specify as required option
                # (if no default provided in function signature)
                meta.kwargs["required"] = True
            else:
                # convert and show default
                # (if default provided in function signature)
                meta.kwargs["default"] = _types.defaults.convert_default(
                    spec.default
                )
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
                    name, hint=meta.hint, negate_flags=config.negate_flags
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

            # add env var - if specified by feud.env decorator
            if env := state.envs.get(param):
                meta.kwargs["envvar"] = env
                meta.kwargs["show_envvar"] = config.show_help_envvars

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
        elif spec.kind == spec.VAR_POSITIONAL:
            # function positional arguments correspond to CLI arguments
            meta.type = _command.ParameterType.ARGUMENT

            # add the argument
            meta.args = [name]

            # special handling for variable-length collections
            meta.kwargs["nargs"] = -1

            # special handling for feud.typing.custom counting types
            if custom.is_counter(meta.hint):
                msg = (
                    "Counting may only be used in conjunction with "
                    "keyword-only function parameters (command-line "
                    "options), not positional function parameters "
                    "(command-line arguments)."
                )
                raise feud.exceptions.CompilationError(msg)

        # add the parameter
        if meta.type == _command.ParameterType.ARGUMENT:
            state.arguments[param] = meta
        elif meta.type == _command.ParameterType.OPTION:
            state.options[param] = meta


def get_command(
    func: typing.Callable,
    /,
    *,
    config: Config,
    click_kwargs: dict[str, typing.Any],
) -> click.Command:
    if isinstance(func, staticmethod):
        func = func.__func__

    state = _command.CommandState(
        config=config,
        click_kwargs=click_kwargs,
        is_group=False,
        aliases=getattr(func, "__feud_aliases__", {}),
        envs=getattr(func, "__feud_envs__", {}),
        names=getattr(
            func, "__feud_names__", _command.NameDict(command=None, params={})
        ),
        overrides={
            override.name: override
            for override in getattr(func, "__click_params__", [])
        },
    )

    # construct command state from signature
    build_command_state(state, func=func, config=config)

    # generate click.Command and attach original function reference
    command = state.decorate(func)
    command.__func__ = func
    return command
