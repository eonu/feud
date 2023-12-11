# Copyright (c) 2023-2025 Feud Developers.
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
        """Returns a full path.\f

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
