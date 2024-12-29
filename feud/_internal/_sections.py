# Copyright (c) 2023 Feud Developers.
# Distributed under the terms of the MIT License (see the LICENSE file).
# SPDX-License-Identifier: MIT
# This source code is part of the Feud project (https://feud.wiki).

from __future__ import annotations

import dataclasses
from collections import defaultdict

from feud import click
from feud._internal import _meta


def add_command_sections(group: click.Group, context: list[str]) -> None:
    from rich_click.utils import CommandGroupDict

    if feud_group := getattr(group, "__group__", None):
        command_groups: dict[str, list[CommandGroupDict]] = {
            " ".join(context): [
                CommandGroupDict(
                    name=section.name,
                    commands=[
                        item if isinstance(item, str) else item.name()
                        for item in section.items
                    ],
                )
                for section in feud_group.__sections__()
            ]
        }

        for sub in group.commands.values():
            if sub.name and isinstance(sub, click.Group):
                add_command_sections(sub, context=[*context, sub.name])

        settings = group.context_settings
        if help_config := settings.get("rich_help_config"):
            settings["rich_help_config"] = dataclasses.replace(
                help_config, command_groups=command_groups
            )
        else:
            settings["rich_help_config"] = click.RichHelpConfiguration(
                command_groups=command_groups
            )


def add_option_sections(
    obj: click.Command | click.Group, context: list[str]
) -> None:
    if isinstance(obj, click.Group):
        update_command(obj, context=context)
        for sub in obj.commands.values():
            if sub.name is None:
                continue
            if isinstance(sub, click.Group):
                add_option_sections(sub, context=[*context, sub.name])
            else:
                update_command(sub, context=[*context, sub.name])
    else:
        update_command(obj, context=context)


def get_opts(option: str, *, command: click.Command) -> list[str]:
    func = command.__func__  # type: ignore[attr-defined]
    name_map = lambda name: name  # noqa: E731
    meta: _meta.FeudMeta | None = getattr(func, "__feud__", None)
    if meta and meta.names:
        names = meta.names
        name_map = lambda name: names["params"].get(name, name)  # noqa: E731
    return next(
        param.opts
        for param in command.params
        if param.name == name_map(option)
    )


def update_command(command: click.Command, context: list[str]) -> None:
    from rich_click.utils import OptionGroupDict

    if func := getattr(command, "__func__", None):
        meta: _meta.FeudMeta | None = getattr(func, "__feud__", None)
        if meta and meta.sections:
            options = meta.sections
            sections = defaultdict(list)
            for option, section_name in options.items():
                opts: list[str] = get_opts(option, command=command)
                sections[section_name].append(opts[0])
            option_groups: dict[str, list[OptionGroupDict]] = {
                " ".join(context): [
                    OptionGroupDict(name=name, options=options)
                    for name, options in sections.items()
                ]
            }

            settings = command.context_settings
            if help_config := settings.get("rich_help_config"):
                settings["rich_help_config"] = dataclasses.replace(
                    help_config, option_groups=option_groups
                )
            else:
                settings["rich_help_config"] = click.RichHelpConfiguration(
                    option_groups=option_groups
                )
