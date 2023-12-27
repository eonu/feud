# Copyright (c) 2023-2025 Feud Developers.
# Distributed under the terms of the MIT License (see the LICENSE file).
# SPDX-License-Identifier: MIT
# This source code is part of the Feud project (https://feud.wiki).

from __future__ import annotations

import dataclasses
import enum
import inspect
import typing as t

try:
    import rich_click as click

    RICH = True
except ImportError:
    import click

    RICH = False

from feud._internal import _decorators, _inflect, _types
from feud.config import Config

CONTEXT_PARAM = "ctx"


class ParameterType(enum.Enum):
    OPTION = enum.auto()
    ARGUMENT = enum.auto()


@dataclasses.dataclass
class ParameterSpec:
    type: ParameterType | None = None  # noqa: A003
    hint: type | None = None
    args: t.Iterable[t.Any] = dataclasses.field(default_factory=list)
    kwargs: dict[str, t.Any] = dataclasses.field(default_factory=dict)


class NameDict(t.TypedDict):
    command: str | None
    params: dict[str, str]


@dataclasses.dataclass
class CommandState:
    config: Config
    click_kwargs: dict[str, t.Any]
    is_group: bool
    names: dict[str, NameDict]  # key: parameter name
    aliases: dict[str, str | list[str]]  # key: parameter name
    envs: dict[str, str]  # key: parameter name
    overrides: dict[str, click.Parameter]  # key: parameter name
    pass_context: bool = False
    # below keys are parameter name
    arguments: dict[str, ParameterSpec] = dataclasses.field(
        default_factory=dict
    )
    options: dict[str, ParameterSpec] = dataclasses.field(default_factory=dict)
    description: str | None = None

    def decorate(  # noqa: PLR0915
        self: CommandState,
        func: t.Callable,
    ) -> click.Command:
        meta_vars: dict[str, str] = {}
        sensitive_vars: dict[str, bool] = {}
        positional: list[str] = []
        var_positional: str | None = None
        params: list[click.Parameter] = []

        sig: inspect.signature = inspect.signature(func)

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
                sensitive = param.hide_input or param.envvar
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
                sensitive = hide_input or envvar

            # get renamed parameter if @feud.rename used
            name: str = self.names["params"].get(param_name, param_name)

            # set parameter name
            param.name = name

            # get meta vars and identify sensitive parameters for validate_call
            meta_vars[name] = self.get_meta_var(param)
            sensitive_vars[name] = sensitive

            # add the parameter
            params.append(param)

        # add any overrides that don't appear in function signature
        # e.g. version_option or anything else
        for param_name, param in self.overrides.items():
            if param_name not in sig.parameters:
                params.append(param)

        # rename command if @feud.rename used
        if command_rename := self.names["command"]:
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
            param_renames=self.names["params"],
            meta_vars=meta_vars,
            sensitive_vars=sensitive_vars,
            positional=positional,
            var_positional=var_positional,
            pydantic_kwargs=self.config.pydantic_kwargs,
        )

        if self.pass_context:
            command = click.pass_context(command)

        if RICH:
            # apply rich-click styling
            command = click.rich_config(
                help_config=click.RichHelpConfiguration(
                    **self.config.rich_click_kwargs
                )
            )(command)

        constructor = click.group if self.is_group else click.command
        command = constructor(**self.click_kwargs)(command)

        command.params = params

        return command

    def get_meta_var(self: CommandState, param: click.Parameter) -> str:
        match param:
            case click.Argument():
                return param.make_metavar()
            case click.Option():
                return param.opts[0]


def pass_context(sig: inspect.Signature) -> bool:
    """Determine whether or not ``click.pass_context`` should be called.

    Context is passed ff the first parameter if the function is named ``ctx``.
    """
    param_name: str | None = dict(enumerate(sig.parameters)).get(0)
    return param_name == CONTEXT_PARAM


def get_option(name: str, *, hint: type, negate_flags: bool) -> str:
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


def get_alias(alias: str, *, hint: type, negate_flags: bool) -> str:
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
