# Copyright (c) 2023 Feud Developers.
# Distributed under the terms of the MIT License (see the LICENSE file).
# SPDX-License-Identifier: MIT
# This source code is part of the Feud project (https://feud.wiki).

import inspect
import os
import re
import sys

import pytest

import feud
import feud.core
from feud import click
from feud import typing as t
from feud._internal import _docstring

sys.path.append(os.path.dirname(os.path.realpath(__file__)))
from fixtures import module  # noqa: E402

overrides: dict[str, t.Any] = {
    "name": "overridden",
    "help": "Overridden help.",
    "epilog": "Overridden epilog.",
    "config": feud.config(negate_flags=False),
}


@pytest.mark.parametrize("override", [False, True])
def test_get_runner_command(*, override: bool) -> None:
    kwargs: dict[str, t.Any] = {}
    if override:
        kwargs.update(overrides)

    runner: click.Command | feud.Group = feud.core.get_runner(
        module.command,
        warn=False,
        **kwargs,
    )

    assert isinstance(runner, click.Command)
    assert runner == module.command

    opt: click.Option = runner.params[0]
    assert opt.type == click.BOOL
    assert opt.name == "opt"
    assert opt.help == "This is an option."
    assert opt.secondary_opts == ["--no-opt"]

    assert runner.name == "command"
    assert runner.help == _docstring.get_description(runner)
    assert runner.epilog is None


@pytest.mark.parametrize("override", [False, True])
def test_get_runner_feud_group(*, override: bool) -> None:
    kwargs: dict[str, t.Any] = {}
    if override:
        kwargs.update(overrides)

    runner: click.Command | feud.Group = feud.core.get_runner(
        module.Group,
        warn=False,
        **kwargs,
    )

    assert inspect.isclass(runner)
    assert issubclass(runner, feud.Group)

    click_kwargs = runner.__feud_click_kwargs__
    assert click_kwargs["name"] == "feud-group"
    assert click_kwargs["help"] == runner.__doc__
    assert "epilog" not in click_kwargs
    assert runner.__feud_config__ == feud.config()

    assert runner.__feud_commands__ == ["func"]
    assert runner.func.name == "func"
    assert runner.func.help == _docstring.get_description(runner.func)
    assert runner.func.epilog is None

    opt: click.Option = runner.func.params[0]
    assert opt.type == click.BOOL
    assert opt.name == "opt"
    assert opt.help == "This is an option."
    assert opt.secondary_opts == ["--no-opt"]

    assert runner.subgroups() == [module.Subgroup]


@pytest.mark.parametrize("override", [False, True])
def test_get_runner_click_group(*, override: bool) -> None:
    kwargs: dict[str, t.Any] = {}
    if override:
        kwargs.update(overrides)

    runner: click.Command | feud.Group = feud.core.get_runner(
        module.click_group,
        warn=False,
        **kwargs,
    )

    assert isinstance(runner, click.Group)

    assert runner.name == "click-group"
    assert runner.help == "This is a Click group."
    assert runner.epilog is None

    command: click.Command = runner.commands["func"]
    assert command.name == "func"
    assert command.help == _docstring.get_description(command)
    assert command.epilog is None

    opt: click.Option = command.params[0]
    assert opt.type == click.BOOL
    assert opt.name == "opt"
    assert opt.help == "This is an option."
    assert opt.secondary_opts == ["--no-opt"]


@pytest.mark.parametrize("override", [False, True])
def test_get_runner_function(*, override: bool) -> None:
    kwargs: dict[str, t.Any] = {}
    if override:
        kwargs.update(overrides)

    runner: click.Command | feud.Group = feud.core.get_runner(
        module.func1,
        warn=False,
        **kwargs,
    )

    assert isinstance(runner, click.Command)

    opt: click.Option = runner.params[0]
    assert opt.type == click.BOOL
    assert opt.name == "opt"
    assert opt.help == "This is an option."

    if override:
        assert runner.name == "overridden"
        assert runner.help == "Overridden help."
        assert runner.epilog == "Overridden epilog."
        assert opt.secondary_opts == []
    else:
        assert runner.name == "func1"
        assert runner.help == _docstring.get_description(runner)
        assert runner.epilog is None
        assert opt.secondary_opts == ["--no-opt"]


@pytest.mark.parametrize("override", [False, True])
def test_get_runner_iterable(*, override: bool) -> None:
    kwargs: dict[str, t.Any] = {}
    if override:
        kwargs.update(overrides)

    runner: click.Command | feud.Group = feud.core.get_runner(
        [module.func1, module.command, module.Group, module.click_group],
        warn=False,
        **kwargs,
    )

    # check top-level group settings

    assert inspect.isclass(runner)
    assert issubclass(runner, feud.Group)
    click_kwargs = runner.__feud_click_kwargs__

    if override:
        assert click_kwargs["name"] == "overridden"
        assert click_kwargs["help"] == "Overridden help."
        assert click_kwargs["epilog"] == "Overridden epilog."
        assert runner.__feud_config__ == overrides["config"]
    else:
        assert click_kwargs["name"] == "__feud_group__"
        assert "help" not in click_kwargs
        assert "epilog" not in click_kwargs
        assert runner.__feud_config__ == feud.config()

    assert runner.__feud_commands__ == ["func1", "command", "click-group"]

    # check undecorated function

    func1: click.Command = runner.func1
    assert func1.name == "func1"
    assert func1.help == _docstring.get_description(func1)
    assert func1.epilog is None

    opt: click.Option = func1.params[0]
    if override:
        assert opt.secondary_opts == []
    else:
        assert opt.secondary_opts == ["--no-opt"]

    # check decorated command

    command: click.Command = runner.command
    opt: click.Option = command.params[0]
    assert opt.type == click.BOOL
    assert opt.name == "opt"
    assert opt.help == "This is an option."
    assert opt.secondary_opts == ["--no-opt"]

    assert command.name == "command"
    assert command.help == _docstring.get_description(command)
    assert command.epilog is None

    # check click.Group

    group: click.Group = getattr(runner, "click-group")
    assert group.name == "click-group"
    assert group.help == "This is a Click group."
    assert group.epilog is None

    command: click.Command = group.commands["func"]
    assert command.name == "func"
    assert command.help == _docstring.get_description(command)
    assert command.epilog is None

    opt: click.Option = command.params[0]
    assert opt.type == click.BOOL
    assert opt.name == "opt"
    assert opt.help == "This is an option."
    assert opt.secondary_opts == ["--no-opt"]

    # check feud.Group

    assert runner.subgroups() == [module.Group]
    group: feud.Group = runner.subgroups()[0]

    click_kwargs = group.__feud_click_kwargs__
    assert click_kwargs["name"] == "feud-group"
    assert click_kwargs["help"] == group.__doc__
    assert "epilog" not in click_kwargs
    assert group.__feud_config__ == feud.config()

    assert group.__feud_commands__ == ["func"]
    assert group.func.name == "func"
    assert group.func.help == _docstring.get_description(group.func)
    assert group.func.epilog is None

    opt: click.Option = group.func.params[0]
    assert opt.type == click.BOOL
    assert opt.name == "opt"
    assert opt.help == "This is an option."
    assert opt.secondary_opts == ["--no-opt"]

    assert group.subgroups() == [module.Subgroup]


def test_get_runner_iterable_nested() -> None:
    msg = (
        "Groups cannot be constructed from dict or iterable "
        "objects nested within iterable objects."
    )

    with pytest.raises(feud.exceptions.CompilationError, match=re.escape(msg)):
        feud.core.get_runner([module.func1, [module.func1]])

    with pytest.raises(feud.exceptions.CompilationError, match=re.escape(msg)):
        feud.core.get_runner([module.func1, {"func": module.func1}])


@pytest.mark.parametrize("override", [False, True])
def test_get_runner_dict(*, override: bool) -> None:
    kwargs: dict[str, t.Any] = {}
    if override:
        kwargs.update(overrides)

    runner: click.Command | feud.Group = feud.core.get_runner(
        {
            "test-func": module.func1,
            "test-command": module.command,
            "test-feud-group": module.Group,
            "test-click-group": module.click_group,
        },
        warn=False,
        **kwargs,
    )

    # check top-level group settings

    assert inspect.isclass(runner)
    assert issubclass(runner, feud.Group)
    click_kwargs = runner.__feud_click_kwargs__

    if override:
        assert click_kwargs["name"] == "overridden"
        assert click_kwargs["help"] == "Overridden help."
        assert click_kwargs["epilog"] == "Overridden epilog."
        assert runner.__feud_config__ == overrides["config"]
    else:
        assert click_kwargs["name"] == "__feud_group__"
        assert "help" not in click_kwargs
        assert "epilog" not in click_kwargs
        assert runner.__feud_config__ == feud.config()

    assert runner.__feud_commands__ == [
        "test-func",
        "test-command",
        "test-click-group",
    ]

    # check undecorated function

    func: click.Command = getattr(runner, "test-func")
    assert func.name == "test-func"
    assert func.help == _docstring.get_description(func)
    assert func.epilog is None

    opt: click.Option = func.params[0]
    if override:
        assert opt.secondary_opts == []
    else:
        assert opt.secondary_opts == ["--no-opt"]

    # check decorated command

    command: click.Command = getattr(runner, "test-command")
    opt: click.Option = command.params[0]
    assert opt.type == click.BOOL
    assert opt.name == "opt"
    assert opt.help == "This is an option."
    assert opt.secondary_opts == ["--no-opt"]

    assert command.name == "test-command"
    assert command.help == _docstring.get_description(command)
    assert command.epilog is None

    # check click.Group

    group: click.Group = getattr(runner, "test-click-group")
    assert group.name == "test-click-group"
    assert group.help == "This is a Click group."
    assert group.epilog is None

    command: click.Command = group.commands["func"]
    assert command.name == "func"
    assert command.help == _docstring.get_description(command)
    assert command.epilog is None

    opt: click.Option = command.params[0]
    assert opt.type == click.BOOL
    assert opt.name == "opt"
    assert opt.help == "This is an option."
    assert opt.secondary_opts == ["--no-opt"]

    # check feud.Group

    group: feud.Group = runner.subgroups()[0]

    click_kwargs = group.__feud_click_kwargs__
    assert click_kwargs["name"] == "test-feud-group"
    assert click_kwargs["help"] == group.__doc__
    assert "epilog" not in click_kwargs
    assert group.__feud_config__ == feud.config()

    assert group.__feud_commands__ == ["func"]
    assert group.func.name == "func"
    assert group.func.help == _docstring.get_description(group.func)
    assert group.func.epilog is None

    opt: click.Option = group.func.params[0]
    assert opt.type == click.BOOL
    assert opt.name == "opt"
    assert opt.help == "This is an option."
    assert opt.secondary_opts == ["--no-opt"]

    assert group.subgroups() == [module.Subgroup]


@pytest.mark.parametrize("override", [False, True])
def test_get_runner_dict_nested(*, override: bool) -> None:
    kwargs: dict[str, t.Any] = {}
    if override:
        kwargs.update(overrides)

    runner: click.Command | feud.Group = feud.core.get_runner(
        {"a": {"b": module.func1, "c": {"d": module.func1}}},
        warn=False,
        **kwargs,
    )

    # check top-level group settings

    assert inspect.isclass(runner)
    assert issubclass(runner, feud.Group)
    click_kwargs = runner.__feud_click_kwargs__

    if override:
        assert click_kwargs["name"] == "overridden"
        assert click_kwargs["help"] == "Overridden help."
        assert click_kwargs["epilog"] == "Overridden epilog."
        assert runner.__feud_config__ == overrides["config"]
    else:
        assert click_kwargs["name"] == "__feud_group__"
        assert "help" not in click_kwargs
        assert "epilog" not in click_kwargs
        assert runner.__feud_config__ == feud.config()

    assert runner.__feud_commands__ == []

    # check subgroup

    subgroups: list[type[feud.Group]] = runner.subgroups()
    assert len(subgroups) == 1
    subgroup: type[feud.Group] = subgroups[0]

    click_kwargs = subgroup.__feud_click_kwargs__
    assert click_kwargs["name"] == "a"
    assert "help" not in click_kwargs
    assert "epilog" not in click_kwargs
    assert subgroup.__feud_config__ == runner.__feud_config__

    # check subgroup commands

    assert subgroup.__feud_commands__ == ["b"]

    command: click.Command = subgroup.b
    assert command.name == "b"
    assert command.help == _docstring.get_description(command)
    assert command.epilog is None

    opt: click.Option = command.params[0]
    assert opt.type == click.BOOL
    assert opt.name == "opt"
    assert opt.help == "This is an option."
    if override:
        assert opt.secondary_opts == []
    else:
        assert opt.secondary_opts == ["--no-opt"]

    # check subsubgroup

    subgroups: list[type[feud.Group]] = subgroup.subgroups()
    assert len(subgroups) == 1
    subgroup: type[feud.Group] = subgroups[0]

    click_kwargs = subgroup.__feud_click_kwargs__
    assert click_kwargs["name"] == "c"
    assert "help" not in click_kwargs
    assert "epilog" not in click_kwargs
    assert subgroup.__feud_config__ == runner.__feud_config__

    # check subsubgroup commands

    assert subgroup.__feud_commands__ == ["d"]

    command: click.Command = subgroup.d
    assert command.name == "d"
    assert command.help == _docstring.get_description(command)
    assert command.epilog is None

    opt: click.Option = command.params[0]
    assert opt.type == click.BOOL
    assert opt.name == "opt"

    assert opt.help == "This is an option."
    if override:
        assert opt.secondary_opts == []
    else:
        assert opt.secondary_opts == ["--no-opt"]


@pytest.mark.parametrize("override", [False, True])
def test_get_runner_module(*, override: bool) -> None:
    kwargs: dict[str, t.Any] = {}
    if override:
        kwargs.update(overrides)

    runner: click.Command | feud.Group = feud.core.get_runner(
        module, warn=False, **kwargs
    )

    # check top-level group settings

    assert inspect.isclass(runner)
    assert issubclass(runner, feud.Group)
    click_kwargs = runner.__feud_click_kwargs__

    if override:
        assert click_kwargs["name"] == "overridden"
        assert click_kwargs["help"] == "Overridden help."
        assert click_kwargs["epilog"] == "Overridden epilog."
        assert runner.__feud_config__ == overrides["config"]
    else:
        assert click_kwargs["name"] == "module"
        assert click_kwargs["help"] == module.__doc__
        assert "epilog" not in click_kwargs
        assert runner.__feud_config__ == feud.config()

    assert runner.__feud_commands__ == ["func1", "command", "click-group"]

    # check undecorated function

    func1: click.Command = runner.func1
    assert func1.name == "func1"
    assert func1.help == _docstring.get_description(func1)
    assert func1.epilog is None

    opt: click.Option = func1.params[0]
    if override:
        assert opt.secondary_opts == []
    else:
        assert opt.secondary_opts == ["--no-opt"]

    # check decorated command

    command: click.Command = runner.command
    opt: click.Option = command.params[0]
    assert opt.type == click.BOOL
    assert opt.name == "opt"
    assert opt.help == "This is an option."
    assert opt.secondary_opts == ["--no-opt"]

    assert command.name == "command"
    assert command.help == _docstring.get_description(command)
    assert command.epilog is None

    # check click.Group

    group: click.Group = getattr(runner, "click-group")
    assert group.name == "click-group"
    assert group.help == "This is a Click group."
    assert group.epilog is None

    command: click.Command = group.commands["func"]
    assert command.name == "func"
    assert command.help == _docstring.get_description(command)
    assert command.epilog is None

    opt: click.Option = command.params[0]
    assert opt.type == click.BOOL
    assert opt.name == "opt"
    assert opt.help == "This is an option."
    assert opt.secondary_opts == ["--no-opt"]

    # check feud.Group

    assert runner.subgroups() == [module.Group]
    group: feud.Group = runner.subgroups()[0]

    click_kwargs = group.__feud_click_kwargs__
    assert click_kwargs["name"] == "feud-group"
    assert click_kwargs["help"] == group.__doc__
    assert "epilog" not in click_kwargs
    assert group.__feud_config__ == feud.config()

    assert group.__feud_commands__ == ["func"]
    assert group.func.name == "func"
    assert group.func.help == _docstring.get_description(group.func)
    assert group.func.epilog is None

    opt: click.Option = group.func.params[0]
    assert opt.type == click.BOOL
    assert opt.name == "opt"
    assert opt.help == "This is an option."
    assert opt.secondary_opts == ["--no-opt"]

    assert group.subgroups() == [module.Subgroup]


@pytest.mark.parametrize("override", [False, True])
def test_get_runner_dict_module(*, override: bool) -> None:
    kwargs: dict[str, t.Any] = {}
    if override:
        kwargs.update(overrides)

    runner: click.Command | feud.Group = feud.core.get_runner(
        {"test-module": module},
        warn=False,
        **kwargs,
    )

    # check top-level group settings

    assert inspect.isclass(runner)
    assert issubclass(runner, feud.Group)
    click_kwargs = runner.__feud_click_kwargs__

    if override:
        assert click_kwargs["name"] == "overridden"
        assert click_kwargs["help"] == "Overridden help."
        assert click_kwargs["epilog"] == "Overridden epilog."
        assert runner.__feud_config__ == overrides["config"]
    else:
        assert click_kwargs["name"] == "__feud_group__"
        assert "help" not in click_kwargs
        assert "epilog" not in click_kwargs
        assert runner.__feud_config__ == feud.config()

    assert runner.__feud_commands__ == []

    # check module

    group: feud.Group = runner.subgroups()[0]

    click_kwargs = group.__feud_click_kwargs__
    assert click_kwargs["name"] == "test-module"
    assert click_kwargs["help"] == module.__doc__
    assert "epilog" not in click_kwargs
    assert group.__feud_commands__ == ["func1", "command", "click-group"]
    if override:
        assert group.__feud_config__ == overrides["config"]
    else:
        assert group.__feud_config__ == feud.config()

    # check undecorated function

    func1: click.Command = group.func1
    assert func1.name == "func1"
    assert func1.help == _docstring.get_description(func1)
    assert func1.epilog is None

    opt: click.Option = func1.params[0]
    if override:
        assert opt.secondary_opts == []
    else:
        assert opt.secondary_opts == ["--no-opt"]

    # check decorated command

    command: click.Command = group.command
    opt: click.Option = command.params[0]
    assert opt.type == click.BOOL
    assert opt.name == "opt"
    assert opt.help == "This is an option."
    assert opt.secondary_opts == ["--no-opt"]

    assert command.name == "command"
    assert command.help == _docstring.get_description(command)
    assert command.epilog is None

    # check click.Group

    subgroup: click.Group = getattr(group, "click-group")
    assert subgroup.name == "click-group"
    assert subgroup.help == "This is a Click group."
    assert subgroup.epilog is None

    command: click.Command = subgroup.commands["func"]
    assert command.name == "func"
    assert command.help == _docstring.get_description(command)
    assert command.epilog is None

    opt: click.Option = command.params[0]
    assert opt.type == click.BOOL
    assert opt.name == "opt"
    assert opt.help == "This is an option."
    assert opt.secondary_opts == ["--no-opt"]


@pytest.mark.parametrize("override", [False, True])
def test_get_runner_dict_iterable(*, override: bool) -> None:
    kwargs: dict[str, t.Any] = {}
    if override:
        kwargs.update(overrides)

    runner: click.Command | feud.Group = feud.core.get_runner(
        {"funcs": [module.func1, module.command]},
        warn=False,
        **kwargs,
    )

    # check top-level group settings

    assert inspect.isclass(runner)
    assert issubclass(runner, feud.Group)
    click_kwargs = runner.__feud_click_kwargs__

    if override:
        assert click_kwargs["name"] == "overridden"
        assert click_kwargs["help"] == "Overridden help."
        assert click_kwargs["epilog"] == "Overridden epilog."
        assert runner.__feud_config__ == overrides["config"]
    else:
        assert click_kwargs["name"] == "__feud_group__"
        assert "help" not in click_kwargs
        assert "epilog" not in click_kwargs
        assert runner.__feud_config__ == feud.config()

    assert runner.__feud_commands__ == []

    # check group settings

    group: feud.Group = runner.subgroups()[0]

    click_kwargs = group.__feud_click_kwargs__
    assert click_kwargs["name"] == "funcs"
    assert "help" not in click_kwargs
    assert "epilog" not in click_kwargs
    assert group.__feud_commands__ == ["func1", "command"]
    if override:
        assert group.__feud_config__ == overrides["config"]
    else:
        assert group.__feud_config__ == feud.config()

    # check undecorated function

    func1: click.Command = group.func1
    assert func1.name == "func1"
    assert func1.help == _docstring.get_description(func1)
    assert func1.epilog is None

    opt: click.Option = func1.params[0]
    if override:
        assert opt.secondary_opts == []
    else:
        assert opt.secondary_opts == ["--no-opt"]

    # check decorated command

    command: click.Command = group.command
    opt: click.Option = command.params[0]
    assert opt.type == click.BOOL
    assert opt.name == "opt"
    assert opt.help == "This is an option."
    assert opt.secondary_opts == ["--no-opt"]

    assert command.name == "command"
    assert command.help == _docstring.get_description(command)
    assert command.epilog is None
