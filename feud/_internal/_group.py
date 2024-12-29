# Copyright (c) 2023 Feud Developers.
# Distributed under the terms of the MIT License (see the LICENSE file).
# SPDX-License-Identifier: MIT
# This source code is part of the Feud project (https://feud.wiki).

from __future__ import annotations

import typing as t

from feud import click
from feud._internal import _command, _meta

if t.TYPE_CHECKING:
    from feud.core.group import Group


def get_group(__cls: type[Group], /) -> click.Group:  # type[Group]
    func: t.Callable = __cls.__main__
    if isinstance(func, staticmethod):
        func = func.__func__

    state = _command.CommandState(
        config=__cls.__feud_config__,
        click_kwargs=__cls.__feud_click_kwargs__,
        is_group=True,
        meta=getattr(func, "__feud__", _meta.FeudMeta()),
        overrides={
            override.name: override
            for override in getattr(func, "__click_params__", [])
        },
    )

    # construct command state from signature
    _command.build_command_state(
        state, func=func, config=__cls.__feud_config__
    )

    # generate click.Group and attach original function reference
    command: click.Group = state.decorate(func)  # type: ignore[assignment]
    command.__func__ = func  # type: ignore[attr-defined]
    command.__group__ = __cls  # type: ignore[attr-defined]
    return command
