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
except ImportError:
    import click

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


@dataclasses.dataclass
class CommandState:
    config: Config
    click_kwargs: dict[str, t.Any]
    context: bool
    is_group: bool
    # below keys are parameter name
    arguments: dict[str, ParameterSpec] = dataclasses.field(
        default_factory=dict
    )
    options: dict[str, ParameterSpec] = dataclasses.field(default_factory=dict)
    aliases: dict[str, str] = dataclasses.field(default_factory=dict)
    overrides: dict[str, click.Parameter] = dataclasses.field(
        default_factory=dict
    )

    def decorate(self: CommandState, func: t.Callable) -> click.Command:
        meta_vars: dict[str, str] = {}
        sensitive_vars: dict[str, bool] = {}
        params: list[click.Parameter] = []

        if self.is_group:
            for param in self.overrides.values():
                params.append(param)  # noqa: PERF402

            command = func
        else:
            for i, param_name in enumerate(inspect.signature(func).parameters):
                sensitive: bool = False
                if self.context and i == 0:
                    continue
                if param_name in self.overrides:
                    param: click.Parameter = self.overrides[param_name]
                    sensitive = param.hide_input
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
                meta_vars[param_name] = self.get_meta_var(param)
                sensitive_vars[param_name] = sensitive
                params.append(param)

            command = _decorators.validate_call(
                func,
                name=self.click_kwargs["name"],
                meta_vars=meta_vars,
                sensitive_vars=sensitive_vars,
                pydantic_kwargs=self.config.pydantic_kwargs,
            )

            if self.context:
                command = click.pass_context(command)

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
    click_kwargs: dict[str, t.Any], *, name: str
) -> None:
    """Sanitize click command/group arguments.

    Removes the ``commands`` argument and sets a name if not present.
    """
    # remove pre-specified commands
    click_kwargs.pop("commands", None)
    # sanitize the provided name
    # (only necessary for auto-naming a Group by class name)
    click_kwargs["name"] = click_kwargs.get("name", _inflect.sanitize(name))
