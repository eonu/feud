# Copyright (c) 2023 Feud Developers.
# Distributed under the terms of the MIT License (see the LICENSE file).
# SPDX-License-Identifier: MIT
# This source code is part of the Feud project (https://feud.wiki).

from __future__ import annotations

import abc
import typing as t

from feud import click
from feud._internal import _command
from feud.config import Config
from feud.core.command import command

if t.TYPE_CHECKING:
    from feud.core.group import Group


class GroupBase(abc.ABCMeta):
    def __new__(
        __cls: type[GroupBase],  # noqa: N804
        cls_name: str,
        bases: tuple[type[Group], ...],
        namespace: dict[str, t.Any],
        **kwargs: t.Any,
    ) -> type[Group]:
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

            # extend/inherit information from parent group if subclassed
            help_: str | None = None
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
                    help_ = base.__feud_click_kwargs__.get("help")

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
            _command.sanitize_click_kwargs(
                click_kwargs, name=cls_name, help_=help_
            )

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

        group: type[Group] = super().__new__(  # type: ignore[assignment]
            __cls,
            cls_name,
            bases,
            namespace,
        )

        if bases:
            # use class-level docstring as help if provided
            if doc := group.__doc__:
                click_kwargs["help"] = doc
            # use __main__ function-level docstring as help if provided
            if doc := group.__main__.__doc__:
                click_kwargs["help"] = doc
            # use class-level click kwargs help if provided
            if doc := kwargs.get("help"):
                click_kwargs["help"] = doc

        return group
