# Copyright (c) 2023-2025 Feud Developers.
# Distributed under the terms of the MIT License (see the LICENSE file).
# SPDX-License-Identifier: MIT
# This source code is part of the Feud project (https://feud.wiki).

from __future__ import annotations

import dataclasses
from collections import defaultdict
from typing import TypedDict

from feud import click


class CommandGroup(TypedDict):
    name: str
    commands: list[str]


class OptionGroup(TypedDict):
    name: str
    options: list[str]


def add_command_sections(
    group: click.Group, context: list[str]
) -> click.Group:
    if feud_group := getattr(group, "__group__", None):
        command_groups: dict[str, list[CommandGroup]] = {
            " ".join(context): [
                CommandGroup(
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
            if isinstance(sub, click.Group):
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
) -> click.Command | click.Group:
    if isinstance(obj, click.Group):
        update_command(obj, context=context)
        for sub in obj.commands.values():
            if isinstance(sub, click.Group):
                add_option_sections(sub, context=[*context, sub.name])
            else:
                update_command(sub, context=[*context, sub.name])
    else:
        update_command(obj, context=context)


def get_opts(option: str, *, command: click.Command) -> list[str]:
    name_map = lambda name: name  # noqa: E731
    if names := getattr(command.__func__, "__feud_names__", None):
        name_map = lambda name: names["params"].get(name, name)  # noqa: E731
    return next(
        param.opts
        for param in command.params
        if param.name == name_map(option)
    )


def update_command(command: click.Command, context: list[str]) -> None:
    if func := getattr(command, "__func__", None):  # noqa: SIM102
        if options := getattr(func, "__feud_sections__", None):
            sections = defaultdict(list)
            for option, section_name in options.items():
                opts: list[str] = get_opts(option, command=command)
                sections[section_name].append(opts[0])
            option_groups: dict[str, list[OptionGroup]] = {
                " ".join(context): [
                    OptionGroup(name=name, options=options)
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
