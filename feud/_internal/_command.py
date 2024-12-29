# Copyright (c) 2023 Feud Developers.
# Distributed under the terms of the MIT License (see the LICENSE file).
# SPDX-License-Identifier: MIT
# This source code is part of the Feud project (https://feud.wiki).

from __future__ import annotations

import dataclasses
import enum
import inspect
import typing as t

import docstring_parser

import feud.exceptions
from feud import click
from feud._internal import _decorators, _docstring, _inflect, _meta, _types
from feud.config import Config
from feud.typing import custom

CONTEXT_PARAM = "ctx"


class ParameterType(enum.Enum):
    OPTION = enum.auto()
    ARGUMENT = enum.auto()


@dataclasses.dataclass
class ParameterSpec:
    type: ParameterType | None = None  # noqa: A003
    hint: type | None = None  # type: ignore[valid-type]
    args: t.Sequence[str] = dataclasses.field(default_factory=list)
    kwargs: dict[str, t.Any] = dataclasses.field(default_factory=dict)


@dataclasses.dataclass
class CommandState:
    config: Config
    click_kwargs: dict[str, t.Any]
    is_group: bool
    meta: _meta.FeudMeta
    overrides: dict[str, click.Parameter]  # key: parameter name
    pass_context: bool = False
    # below keys are parameter name
    arguments: dict[str, ParameterSpec] = dataclasses.field(
        default_factory=dict
    )
    options: dict[str, ParameterSpec] = dataclasses.field(default_factory=dict)
    description: str | None = None

    def decorate(  # noqa: PLR0915
        self: t.Self,
        func: t.Callable,
    ) -> click.Command | click.Group:
        meta_vars: dict[str, str] = {}
        sensitive_vars: dict[str, bool] = {}
        positional: list[str] = []
        var_positional: str | None = None
        params: list[click.Parameter] = []

        sig: inspect.Signature = inspect.signature(func, eval_str=True)

        for i, (param_name, param_spec) in enumerate(sig.parameters.items()):
            # store names of positional arguments
            if param_spec.kind in (
                param_spec.POSITIONAL_ONLY,
                param_spec.POSITIONAL_OR_KEYWORD,
            ):
                positional.append(param_name)
            # store name of variable positional arguments (i.e. *args)
            if param_spec.kind == param_spec.VAR_POSITIONAL:
                var_positional = param_name
            # ignore variable keyword arguments (i.e. **kwargs)
            if param_spec.kind == param_spec.VAR_KEYWORD:
                continue

            # create Click parameters
            sensitive: bool = False
            if self.pass_context and i == 0:
                continue
            if param_name in self.overrides:
                param: click.Parameter = self.overrides[param_name]
                sensitive |= bool(param.envvar)
                if isinstance(param, click.Option):
                    sensitive |= param.hide_input
            elif param_name in self.arguments:
                spec = self.arguments[param_name]
                spec.kwargs["type"] = _types.click.get_click_type(
                    spec.hint, config=self.config
                )
                param = click.Argument(spec.args, **spec.kwargs)
            elif param_name in self.options:
                spec = self.options[param_name]
                spec.kwargs["type"] = _types.click.get_click_type(
                    spec.hint, config=self.config
                )
                param = click.Option(spec.args, **spec.kwargs)
                hide_input = spec.kwargs.get("hide_input")
                envvar = spec.kwargs.get("envvar")
                sensitive |= hide_input or bool(envvar)

            # get renamed parameter if @feud.rename used
            name: str = self.meta.names["params"].get(param_name, param_name)

            # set parameter name
            param.name = name

            # get meta vars and identify sensitive parameters for validate_call
            meta_vars[name] = self.get_meta_var(param) or name
            sensitive_vars[name] = sensitive

            # add the parameter
            params.append(param)

        # add any overrides that don't appear in function signature
        # e.g. version_option or anything else
        for param_name, param in self.overrides.items():
            if param_name not in sig.parameters:
                params.append(param)

        # rename command if @feud.rename used
        if command_rename := self.meta.names["command"]:
            self.click_kwargs = {**self.click_kwargs, "name": command_rename}

        # set help to docstring description if not provided
        if self.is_group:
            if "help" in self.click_kwargs:
                self.click_kwargs["help"] = self.description
        elif help_ := self.click_kwargs.get("help", self.description):
            self.click_kwargs["help"] = help_

        command = _decorators.validate_call(
            func,
            name=self.click_kwargs["name"],
            param_renames=self.meta.names["params"],
            meta_vars=meta_vars,
            sensitive_vars=sensitive_vars,
            positional=positional,
            var_positional=var_positional,
            pydantic_kwargs=self.config.pydantic_kwargs,
        )

        if self.pass_context:
            command = click.pass_context(command)  # type: ignore[assignment, arg-type]

        if click.is_rich:
            # apply rich-click styling
            command = click.rich_config(
                help_config=click.RichHelpConfiguration(
                    **self.config.rich_click_kwargs
                )
            )(command)

        constructor = click.group if self.is_group else click.command
        compiled: click.Command | click.Group = constructor(
            **self.click_kwargs,
        )(command)
        compiled.params = params

        return compiled

    def get_meta_var(self: t.Self, param: click.Parameter) -> str | None:
        match param:
            case click.Argument():
                return param.make_metavar()
            case click.Option():
                return param.opts[0]
        return None


def pass_context(sig: inspect.Signature) -> bool:
    """Determine whether or not ``click.pass_context`` should be called.

    Context is passed ff the first parameter if the function is named ``ctx``.
    """
    param_name: str | None = dict(enumerate(sig.parameters)).get(0)
    return param_name == CONTEXT_PARAM


def get_option(name: str, *, hint: t.Any, negate_flags: bool) -> str:
    """Convert a name into a command-line option.

    Additionally negates the option if a boolean flag is provided
    and ``negate_flags`` is ``True``, and returns a joint declaration.

    Example
    -------
    >>> get_option("opt-name", hint=bool, negate_flags=True)
    "--opt-name/--no-opt-name"
    """
    option: str = _inflect.optionize(name)
    base_type, _, _, _ = _types.click.get_base_type(hint)
    if base_type is bool and negate_flags:
        negated_option: str = _inflect.negate_option(option)
        return f"{option}/{negated_option}"
    return option


def get_alias(alias: str, *, hint: t.Any, negate_flags: bool) -> str:
    """Negate an alias for a boolean flag and returns a joint declaration
    if ``negate_flags`` is ``True``.

    Example
    -------
    >>> get_alias("-a", hint=bool, negate_flags=True)
    "-a/--no-a"
    >>> get_alias("-a", hint=bool, negate_flags=False)
    "-a"
    >>> get_alias("-a", hint=str, negate_flags=True)
    "-a"
    """
    base_type, _, _, _ = _types.click.get_base_type(hint)
    if base_type is bool and negate_flags:
        negated_alias: str = _inflect.negate_alias(alias)
        return f"{alias}/{negated_alias}"
    return alias


def sanitize_click_kwargs(
    click_kwargs: dict[str, t.Any], *, name: str, help_: str | None = None
) -> None:
    """Sanitize click command/group arguments.

    Removes the ``commands`` argument and sets a name if not present.
    """
    # remove pre-specified commands
    click_kwargs.pop("commands", None)
    # sanitize the provided name
    # (only necessary for auto-naming a Group by class name)
    click_kwargs["name"] = click_kwargs.get("name", _inflect.sanitize(name))
    # set help if provided
    if help_:
        click_kwargs["help"] = help_


def build_command_state(  # noqa: PLR0915
    state: CommandState, *, func: t.Callable, config: Config
) -> None:
    doc: docstring_parser.Docstring
    if state.is_group:
        doc = docstring_parser.parse(state.click_kwargs.get("help", ""))
    else:
        doc = docstring_parser.parse_from_object(func)

    state.description = _docstring.get_description(doc)

    sig: inspect.Signature = inspect.signature(func, eval_str=True)

    for param, spec in sig.parameters.items():
        meta = ParameterSpec()
        meta.hint = spec.annotation

        # get renamed parameter if @feud.rename used
        name: str = state.meta.names["params"].get(param, param)

        if pass_context(sig) and param == CONTEXT_PARAM:
            # skip handling for click.Context argument
            state.pass_context = True

        if spec.kind in (spec.POSITIONAL_ONLY, spec.POSITIONAL_OR_KEYWORD):
            # function positional arguments correspond to CLI arguments
            meta.type = ParameterType.ARGUMENT

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
            meta.type = ParameterType.OPTION

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
                get_option(
                    name, hint=meta.hint, negate_flags=config.negate_flags
                )
            ]

            # add aliases - if specified by feud.alias decorator
            for alias in state.meta.aliases.get(param, []):
                meta.args.append(
                    get_alias(
                        alias,
                        hint=meta.hint,
                        negate_flags=config.negate_flags,
                    )
                )

            # add env var - if specified by feud.env decorator
            if env := state.meta.envs.get(param):
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
            meta.type = ParameterType.ARGUMENT

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
        if meta.type == ParameterType.ARGUMENT:
            state.arguments[param] = meta
        elif meta.type == ParameterType.OPTION:
            state.options[param] = meta


def get_command(
    func: t.Callable,
    /,
    *,
    config: Config,
    click_kwargs: dict[str, t.Any],
) -> click.Command:
    if isinstance(func, staticmethod):
        func = func.__func__

    state = CommandState(
        config=config,
        click_kwargs=click_kwargs,
        is_group=False,
        meta=getattr(func, "__feud__", _meta.FeudMeta()),
        overrides={
            override.name: override
            for override in getattr(func, "__click_params__", [])
        },
    )

    # construct command state from signature
    build_command_state(state, func=func, config=config)

    # generate click.Command and attach original function reference
    command = state.decorate(func)
    command.__func__ = func  # type: ignore[attr-defined]
    return command
