# Copyright (c) 2023-2025 Feud Developers.
# Distributed under the terms of the MIT License (see the LICENSE file).
# SPDX-License-Identifier: MIT
# This source code is part of the Feud project (https://feud.wiki).

from feud import click
from feud._internal import _command


def get_group(__cls: type, /) -> click.Group:  # type[Group]
    func: callable = __cls.__main__
    if isinstance(func, staticmethod):
        func = func.__func__

    state = _command.CommandState(
        config=__cls.__feud_config__,
        click_kwargs=__cls.__feud_click_kwargs__,
        is_group=True,
        aliases=getattr(func, "__feud_aliases__", {}),
        envs=getattr(func, "__feud_envs__", {}),
        names=getattr(
            func,
            "__feud_names__",
            _command.NameDict(command=None, params={}),
        ),
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
    command = state.decorate(func)
    command.__func__ = func
    command.__group__ = __cls
    return command
