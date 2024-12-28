# Copyright (c) 2023 Feud Developers.
# Distributed under the terms of the MIT License (see the LICENSE file).
# SPDX-License-Identifier: MIT
# This source code is part of the Feud project (https://feud.wiki).

import os
import re
from typing import Callable
from unittest import mock

import pytest

import feud
from feud import click
from feud import typing as t
from feud._internal import _meta


def assert_help(
    __obj: t.Union[
        feud.Group,
        click.Group,
        click.Command,
        Callable,
    ],
    /,
    *,
    capsys: pytest.CaptureFixture,
    expected: str,
) -> None:
    with pytest.raises(SystemExit):
        feud.run(__obj, ["--help"])
    out, _ = capsys.readouterr()
    assert out.strip() == expected.strip()


@pytest.fixture(scope="module")
def env_command() -> Callable:
    @feud.env(opt1="OPT1", opt2="OPT2", opt3="OPT3")
    def f(
        *, opt1: t.PositiveInt, opt2: bool, opt3: t.NegativeFloat
    ) -> tuple[t.PositiveInt, bool, t.NegativeFloat]:
        """Returns a full path.

        Parameters
        ----------
        opt1:
            First option.
        opt2:
            Second option.
        opt3:
            Third option.
        """
        return opt1, opt2, opt3

    return f


def test_valid_format() -> None:
    @feud.command
    @feud.alias(arg1="-a", arg2="-b")
    def f(*, arg1: int, arg2: bool) -> None:
        pass

    assert [param.opts for param in f.params] == [
        ["--arg1", "-a"],
        ["--arg2", "-b"],
    ]


@pytest.mark.parametrize("negate_flags", [True, False])
def test_multiple_aliases(*, negate_flags: bool) -> None:
    @feud.command(negate_flags=negate_flags)
    @feud.alias(arg1=["-a", "-A"])
    def f(*, arg1: bool) -> None:
        pass

    assert f.params[0].opts == ["--arg1", "-a", "-A"]

    secondary_opts = ["--no-arg1", "--no-a", "--no-A"] if negate_flags else []
    assert f.params[0].secondary_opts == secondary_opts


def test_multiple_aliases_non_unique() -> None:
    with pytest.raises(feud.CompilationError):

        @feud.command
        @feud.alias(arg1=["-a", "-a"])
        def f(*, arg1: int, arg2: bool) -> None:
            pass


def test_undefined_alias() -> None:
    with pytest.raises(feud.CompilationError):

        @feud.alias(arg1="-a", arg2="-b")
        def f(*, arg1: int) -> None:
            pass


def test_invalid_format_alias() -> None:
    with pytest.raises(feud.CompilationError):

        @feud.alias(arg1="-a1")
        def f(*, arg1: int) -> None:
            pass


def test_alias_argument() -> None:
    with pytest.raises(feud.CompilationError):

        @feud.alias(arg1="-a")
        def f(arg1: int) -> None:
            pass


def test_undefined_env() -> None:
    with pytest.raises(feud.CompilationError):

        @feud.env(opt1="-a", opt2="-b")
        def f(*, opt1: int) -> None:
            pass


def test_env_help_with_show(
    capsys: pytest.CaptureFixture, env_command: Callable
) -> None:
    assert_help(
        feud.command(show_help_envvars=True)(env_command),
        capsys=capsys,
        expected="""
Usage: pytest [OPTIONS]

  Returns a full path.

Options:
  --opt1 INTEGER RANGE  First option.  [env var: OPT1; x>0; required]
  --opt2 / --no-opt2    Second option.  [env var: OPT2; required]
  --opt3 FLOAT RANGE    Third option.  [env var: OPT3; x<0; required]
  --help                Show this message and exit.
        """,
    )


def test_env_help_without_show(
    capsys: pytest.CaptureFixture, env_command: Callable
) -> None:
    assert_help(
        feud.command(show_help_envvars=False)(env_command),
        capsys=capsys,
        expected="""
Usage: pytest [OPTIONS]

  Returns a full path.

Options:
  --opt1 INTEGER RANGE  First option.  [x>0; required]
  --opt2 / --no-opt2    Second option.  [required]
  --opt3 FLOAT RANGE    Third option.  [x<0; required]
  --help                Show this message and exit.
        """,
    )


def test_env_call_no_env(env_command: Callable) -> None:
    with pytest.raises(click.MissingParameter):
        feud.run(env_command, [], standalone_mode=False)


@mock.patch.dict(os.environ, {"OPT1": "long"}, clear=True)
def test_env_call_hidden() -> None:
    @feud.env(opt1="OPT1")
    def f(*, opt1: t.constr(max_length=3)) -> None:
        pass

    msg = "String should have at most 3 characters [input_value=hidden]"
    with pytest.raises(click.UsageError, match=re.escape(msg)):
        feud.run(f, [], standalone_mode=False)


@mock.patch.dict(
    os.environ, {"OPT1": "1", "OPT2": "true", "OPT3": "-0.1"}, clear=True
)
def test_env_call_with_env(env_command: Callable) -> None:
    assert feud.run(env_command, [], standalone_mode=False) == (1, True, -0.1)


@mock.patch.dict(os.environ, {"OPT": "long"}, clear=True)
def test_override_env_hidden() -> None:
    @click.option("--opt", type=str, envvar="OPT")
    def f(*, opt: t.constr(max_length=3)) -> str:
        return opt

    msg = "String should have at most 3 characters [input_value=hidden]"
    with pytest.raises(click.UsageError, match=re.escape(msg)):
        feud.run(f, [], standalone_mode=False)


def test_rename_command() -> None:
    @feud.command
    @feud.rename("func")
    def f(*, opt: int) -> int:
        return opt

    assert f.name == "func"


def test_rename_params() -> None:
    @feud.rename(arg1="arg-1", arg2="arg-2", opt1="opt-1", opt2="opt-2")
    def f(
        ctx: click.Context, arg1: int, arg2: str, *, opt1: bool, opt2: float
    ) -> None:
        return arg1, arg2, opt1, opt2

    cmd = feud.command(f)

    # check arg1 -> arg-1 rename
    assert cmd.params[0].name == "arg-1"

    # check arg2 -> arg-2 rename
    assert cmd.params[1].name == "arg-2"

    # check opt1 -> opt-1 rename
    # should create options --opt-1/--no-opt-1
    assert cmd.params[2].name == "opt-1"
    assert cmd.params[2].opts == ["--opt-1"]
    assert cmd.params[2].secondary_opts == ["--no-opt-1"]

    # check opt2 -> opt-2 rename
    # should create option --opt-2
    assert cmd.params[3].name == "opt-2"
    assert cmd.params[3].opts == ["--opt-2"]

    # test call
    assert cmd(
        ["2", "test", "--no-opt-1", "--opt-2", "0.2"], standalone_mode=False
    ) == (2, "test", False, 0.2)


def test_rename_command_and_params(capsys: pytest.CaptureFixture) -> None:
    @feud.rename(
        "func", arg1="arg-1", arg2="arg-2", opt1="opt-1", opt2="opt-2"
    )
    def f(
        ctx: click.Context, arg1: int, arg2: str, *, opt1: bool, opt2: float
    ) -> None:
        return arg1, arg2, opt1, opt2

    cmd = feud.command(f)

    # check command name
    assert cmd.name == "func"

    # check arg1 -> arg-1 rename
    assert cmd.params[0].name == "arg-1"

    # check arg2 -> arg-2 rename
    assert cmd.params[1].name == "arg-2"

    # check opt1 -> opt-1 rename
    # should create options --opt-1/--no-opt-1
    assert cmd.params[2].name == "opt-1"
    assert cmd.params[2].opts == ["--opt-1"]
    assert cmd.params[2].secondary_opts == ["--no-opt-1"]

    # check opt2 -> opt-2 rename
    # should create option --opt-2
    assert cmd.params[3].name == "opt-2"
    assert cmd.params[3].opts == ["--opt-2"]

    # check help
    assert_help(
        cmd,
        capsys=capsys,
        expected="""
Usage: pytest [OPTIONS] ARG-1 ARG-2

Options:
  --opt-1 / --no-opt-1  [required]
  --opt-2 FLOAT         [required]
  --help                Show this message and exit.
        """,
    )

    # test call
    assert cmd(
        ["2", "test", "--no-opt-1", "--opt-2", "0.2"], standalone_mode=False
    ) == (2, "test", False, 0.2)


@mock.patch.dict(os.environ, {"OPT1": "1", "OPT2": "true"}, clear=True)
def test_all_decorators(capsys: pytest.CaptureFixture) -> None:
    @feud.rename("cmd", opt1="opt-1", opt2="opt-2", opt3="opt_3")
    @feud.env(opt1="OPT1", opt2="OPT2")
    @feud.alias(opt3="-o")
    @feud.section(opt1="odd", opt2="even", opt3="odd")
    def command(
        *, opt1: t.PositiveInt, opt2: bool, opt3: t.NegativeFloat
    ) -> t.Path:
        """Returns a full path.

        Parameters
        ----------
        opt1:
            First option.
        opt2:
            Second option.
        opt3:
            Third option.
        """
        return opt1, opt2, opt3

    # check decorated function metadata
    assert command.__feud__ == _meta.FeudMeta(
        aliases={"opt3": ["-o"]},
        envs={"opt1": "OPT1", "opt2": "OPT2"},
        names={
            "command": "cmd",
            "params": {"opt1": "opt-1", "opt2": "opt-2", "opt3": "opt_3"},
        },
        sections={"opt1": "odd", "opt2": "even", "opt3": "odd"},
    )

    cmd = feud.command(command)

    # check command name
    assert cmd.name == "cmd"

    # check opt1 -> opt-1 rename
    # should create option --opt-1
    assert cmd.params[0].name == "opt-1"
    assert cmd.params[0].opts == ["--opt-1"]
    assert cmd.params[0].envvar == "OPT1"

    # check opt2 -> opt-2 rename
    # should create option --opt-2
    assert cmd.params[1].name == "opt-2"
    assert cmd.params[1].opts == ["--opt-2"]
    assert cmd.params[1].envvar == "OPT2"

    # check opt3 -> opt_3 rename
    # should create option --opt_3
    assert cmd.params[2].name == "opt_3"
    assert cmd.params[2].opts == ["--opt_3", "-o"]

    # check help
    assert_help(
        cmd,
        capsys=capsys,
        expected="""
Usage: pytest [OPTIONS]

  Returns a full path.

Options:
  --opt-1 INTEGER RANGE    First option.  [env var: OPT1; x>0; required]
  --opt-2 / --no-opt-2     Second option.  [env var: OPT2; required]
  -o, --opt_3 FLOAT RANGE  Third option.  [x<0; required]
  --help                   Show this message and exit.
        """,
    )

    # test call
    assert cmd(["--opt_3", "-1.2"], standalone_mode=False) == (1, True, -1.2)


def test_rename_group(capsys: pytest.CaptureFixture) -> None:
    class Test(feud.Group):
        @staticmethod
        @feud.rename("test-group", opt1="opt-1")
        def __main__(ctx: click.Context, *, opt1: int) -> None:
            ctx.obj = {"opt1": opt1}

        @staticmethod
        @feud.rename("func", opt2="opt_2")
        def f(ctx: click.Context, *, opt2: int) -> int:
            return ctx.obj["opt1"], opt2

    assert Test(
        ["--opt-1", "1", "func", "--opt_2", "2"],
        standalone_mode=False,
    ) == (1, 2)
