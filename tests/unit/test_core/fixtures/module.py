# Copyright (c) 2023 Feud Developers.
# Distributed under the terms of the MIT License (see the LICENSE file).
# SPDX-License-Identifier: MIT
# This source code is part of the Feud project (https://feud.wiki).

"""This is a module."""

import types

import feud
from feud import click


def func1(*, opt: bool) -> bool:
    """This is the first function.

    Parameters
    ----------
    opt:
        This is an option.
    """
    return opt


@feud.command
def command(*, opt: bool) -> bool:
    """This is a command.

    Parameters
    ----------
    opt:
        This is an option.
    """
    return opt


class Group(feud.Group, name="feud-group"):
    """This is a Feud group."""

    def func(*, opt: bool) -> bool:
        """This is a function in the group.

        Parameters
        ----------
        opt:
            This is an option.
        """
        return opt


class Subgroup(feud.Group, name="feud-subgroup"):
    """This is a subgroup."""

    def func(*, opt: bool) -> bool:
        """This is a function in the subgroup.

        Parameters
        ----------
        opt:
            This is an option.
        """
        return opt


Group.register(Subgroup)

click_group: click.Group = types.new_class(
    "ClickGroup",
    bases=(Group,),
    kwds={
        "name": "click-group",
        "help": "This is a Click group.",
    },
).compile()
