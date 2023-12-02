# Copyright (c) 2023-2025 Feud Developers.
# Distributed under the terms of the MIT License (see the LICENSE file).
# SPDX-License-Identifier: MIT
# This source code is part of the Feud project (https://feud.wiki).

from __future__ import annotations

import abc
import typing as t

from feud._internal import _command
from feud.config import Config
from feud.core.command import command

try:
    import rich_click as click
except ImportError:
    import click


class GroupBase(abc.ABCMeta):
    def __new__(
        cls: type[GroupBase],
        cls_name: str,
        bases: tuple[type, ...],
        namespace: dict[str, t.Any],
        **kwargs: t.Any,
    ) -> type:  # type[Group], but circular import
        """Metaclass for creating groups.

        Parameters
        ----------
        cls_name:
            The name of the class to be created.

        bases:
            The base classes of the class to be created.

        namespace:
            The attribute dictionary of the class to be created.

        **kwargs:
            Catch-all for any other keyword arguments.

            This can be a combination of:
            - click command/group key-word arguments,
            - feud configuration key-word arguments,
            - a feud configuration object.

        Returns
        -------
        The new class created by the metaclass.
        """
        if bases:
            base_config: Config | None = None
            click_kwargs: dict[str, t.Any] = {}
            subgroups: list[type] = []  # type[Group], but circular import
            commands: list[str] = []

            # extend/inherit from parent group if subclassed
            for base in bases:
                if config := getattr(base, "__feud_config__", None):
                    # NOTE: may want **dict(config) depending on behaviour
                    base_config = Config._create(  # noqa: SLF001
                        base=base_config,
                        **config.model_dump(exclude_unset=True),
                    )
                    click_kwargs = {
                        **click_kwargs,
                        **base.__feud_click_kwargs__,
                    }
                    subgroups += [
                        subgroup
                        for subgroup in base.__feud_subgroups__
                        if subgroup not in subgroups
                    ]
                    commands += [
                        cmd
                        for cmd in base.__feud_commands__
                        if cmd not in commands
                    ]

            # deconstruct base config, override config kwargs and click kwargs
            config_kwargs: dict[str, t.Any] = {}
            for k, v in kwargs.items():
                if k == "config":
                    # NOTE: may want base_config = v depending on behaviour
                    base_config = Config._create(  # noqa: SLF001
                        base=base_config, **v.model_dump(exclude_unset=True)
                    )
                else:
                    d = (
                        config_kwargs
                        if k in Config.model_fields
                        else click_kwargs
                    )
                    d[k] = v

            # sanitize click kwargs
            _command.sanitize_click_kwargs(click_kwargs, name=cls_name)

            # members to consider as commands
            funcs = {
                name: attr
                for name, attr in namespace.items()
                if callable(attr) and not name.startswith("_")
            }

            # set config and click kwargs
            # (override feud.command decorator settings)
            namespace["__feud_config__"] = Config._create(  # noqa: SLF001
                base=base_config, **config_kwargs
            )
            namespace["__feud_click_kwargs__"] = click_kwargs
            namespace["__feud_subgroups__"] = subgroups
            namespace["__feud_commands__"] = commands + [
                func for func in funcs if func not in commands
            ]

            # auto-generate commands
            for name, func in funcs.items():
                if not isinstance(func, click.Command):
                    namespace[name] = command(
                        func, config=namespace["__feud_config__"]
                    )

        return super().__new__(cls, cls_name, bases, namespace)
