# Copyright (c) 2023 Feud Developers.
# Distributed under the terms of the MIT License (see the LICENSE file).
# SPDX-License-Identifier: MIT
# This source code is part of the Feud project (https://feud.wiki).

import feud
from feud import click


def test_metaclass_default() -> None:
    class Test(feud.Group):
        def command(*, opt: bool) -> None:
            pass

    assert Test.__feud_config__ == feud.config()
    assert Test.__feud_click_kwargs__ == {"name": "test"}

    command = Test.command
    assert isinstance(command, click.Command)

    arg = command.params[0]
    assert arg.opts == ["--opt"]
    assert arg.secondary_opts == ["--no-opt"]


def test_metaclass_base_config() -> None:
    config = feud.config(negate_flags=False)

    class Test(feud.Group, config=config):
        def command(*, opt: bool) -> None:
            pass

    assert Test.__feud_config__ == config
    assert Test.__feud_click_kwargs__ == {"name": "test"}

    command = Test.command
    assert isinstance(command, click.Command)

    arg = command.params[0]
    assert arg.opts == ["--opt"]
    assert arg.secondary_opts == []


def test_metaclass_feud_kwargs() -> None:
    class Test(feud.Group, negate_flags=False):
        def command(*, opt: bool) -> None:
            pass

    assert Test.__feud_config__ == feud.config(negate_flags=False)
    assert Test.__feud_click_kwargs__ == {"name": "test"}

    command = Test.command
    assert isinstance(command, click.Command)

    arg = command.params[0]
    assert arg.opts == ["--opt"]
    assert arg.secondary_opts == []


def test_metaclass_config_with_feud_kwargs() -> None:
    config = feud.config(negate_flags=False)

    class Test(feud.Group, config=config, negate_flags=True):
        def command(*, opt: bool) -> None:
            pass

    assert Test.__feud_config__ == feud.config(negate_flags=True)
    assert Test.__feud_click_kwargs__ == {"name": "test"}

    command = Test.command
    assert isinstance(command, click.Command)

    arg = command.params[0]
    assert arg.opts == ["--opt"]
    assert arg.secondary_opts == ["--no-opt"]


def test_metaclass_click_kwargs() -> None:
    name = "custom"
    epilog = "Visit https://www.com for more information."

    class Test(feud.Group, name=name, epilog=epilog):
        def command(*, opt: bool) -> None:
            pass

    assert Test.__feud_config__ == feud.config()
    assert Test.__feud_click_kwargs__ == {"name": name, "epilog": epilog}

    group = Test.compile()
    assert group.name == name
    assert group.epilog == epilog

    # group-level click kwargs should not be propagated to commands
    command = Test.command
    assert isinstance(command, click.Command)
    assert command.name == "command"
    assert command.epilog is None

    arg = command.params[0]
    assert arg.opts == ["--opt"]
    assert arg.secondary_opts == ["--no-opt"]


def test_metaclass_config_with_feud_kwargs_and_click_kwargs() -> None:
    name = "custom"
    epilog = "Visit https://www.com for more information."
    config = feud.config(negate_flags=False)

    class Test(
        feud.Group, name=name, epilog=epilog, config=config, negate_flags=True
    ):
        def command(*, opt: bool) -> None:
            pass

    assert Test.__feud_config__ == feud.config(negate_flags=True)
    assert Test.__feud_click_kwargs__ == {"name": name, "epilog": epilog}

    group = Test.compile()
    assert group.name == name
    assert group.epilog == epilog

    # group-level click kwargs should not be propagated to commands
    command = Test.command
    assert isinstance(command, click.Command)
    assert command.name == "command"
    assert command.epilog is None

    arg = command.params[0]
    assert arg.opts == ["--opt"]
    assert arg.secondary_opts == ["--no-opt"]
