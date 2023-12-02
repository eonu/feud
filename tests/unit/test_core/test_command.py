# Copyright (c) 2023-2025 Feud Developers.
# Distributed under the terms of the MIT License (see the LICENSE file).
# SPDX-License-Identifier: MIT
# This source code is part of the Feud project (https://feud.wiki).

import re

import pytest

import feud
from feud import click
from feud import typing as t


def test_help_docstring(capsys: pytest.CaptureFixture) -> None:
    @feud.command
    def f(arg1: int, *, arg2: bool) -> None:
        """Do something."""

    with pytest.raises(SystemExit):
        f(["--help"])

    out, _ = capsys.readouterr()

    assert (
        out.strip()
        == """
Usage: pytest [OPTIONS] ARG1

  Do something.

Options:
  --arg2 / --no-arg2  [required]
  --help              Show this message and exit.
    """.strip()
    )


def test_help_click_kwarg(capsys: pytest.CaptureFixture) -> None:
    @feud.command(help="Do something.")
    def f(arg1: int, *, arg2: bool) -> None:
        pass

    with pytest.raises(SystemExit):
        f(["--help"])

    out, _ = capsys.readouterr()

    assert (
        out.strip()
        == """
Usage: pytest [OPTIONS] ARG1

  Do something.

Options:
  --arg2 / --no-arg2  [required]
  --help              Show this message and exit.
    """.strip()
    )


def test_param_help_docstring(capsys: pytest.CaptureFixture) -> None:
    @feud.command
    def f(arg1: int, *, arg2: bool) -> None:
        """Do something.\f

        Parameters
        ----------
        arg1:
            Controls something.

        arg2:
            Changes something.
        """  # noqa: D301, D400

    with pytest.raises(SystemExit):
        f(["--help"])

    out, _ = capsys.readouterr()

    assert (
        out.strip()
        == """
Usage: pytest [OPTIONS] ARG1

  Do something.

Options:
  --arg2 / --no-arg2  Changes something.  [required]
  --help              Show this message and exit.
    """.strip()
    )


def test_param_help_click_override(capsys: pytest.CaptureFixture) -> None:
    @feud.command
    @click.option(
        "--arg2/--no-arg2", type=bool, required=True, help="Changes something."
    )
    def f(arg1: int, *, arg2: bool) -> None:
        """Do something."""

    with pytest.raises(SystemExit):
        f(["--help"])

    out, _ = capsys.readouterr()

    assert (
        out.strip()
        == """
Usage: pytest [OPTIONS] ARG1

  Do something.

Options:
  --arg2 / --no-arg2  Changes something.  [required]
  --help              Show this message and exit.
    """.strip()
    )


def test_no_call() -> None:
    @feud.command
    def f(arg1: int, *, arg2: bool) -> None:
        pass

    assert isinstance(f, click.Command)


def test_empty_call() -> None:
    @feud.command()
    def f(arg1: int, *, arg2: bool) -> None:
        pass

    assert isinstance(f, click.Command)


def test_kwarg_call() -> None:
    @feud.command(config=feud.config())
    def f(arg1: int, *, arg2: bool) -> None:
        pass

    assert isinstance(f, click.Command)


def test_config_propagation() -> None:
    """Check that configuration options propagate to command parameters.

    Only if not overriden.
    """

    @feud.command(show_help_defaults=True)
    def f(*, arg1: bool = True, arg2: int = 1) -> None:
        pass

    assert all(param.show_default is True for param in f.params)

    @feud.command(show_help_defaults=False)
    def f(*, arg1: bool = True, arg2: int = 1) -> None:
        pass

    assert all(not param.show_default for param in f.params)

    @feud.command(show_help_defaults=False)
    @click.option("--arg2", type=int, default=1, show_default=True)
    def f(*, arg1: bool = True, arg2: int = 1) -> None:
        pass

    assert f.params[0].show_default is False
    assert f.params[1].show_default is True


def test_forward() -> None:
    @feud.command
    def g(*, arg1: bool) -> bool:
        return arg1

    @feud.command
    def f(ctx: click.Context, *, arg1: bool) -> bool:
        return ctx.forward(g)

    assert not f(["--no-arg1"], standalone_mode=False)


def test_invoke() -> None:
    @feud.command
    def g(*, arg1: bool) -> bool:
        return arg1

    @feud.command
    def f(ctx: click.Context, *, arg1: bool) -> bool:
        return ctx.invoke(g, arg1=arg1)

    assert not f(["--no-arg1"], standalone_mode=False)


def test_run_undecorated() -> None:
    def f(arg1: int, *, arg2: bool) -> tuple[int, bool]:  # noqa: FA102
        return arg1, arg2

    assert feud.run(f, ["1", "--no-arg2"], standalone_mode=False) == (1, False)


def test_run_decorated() -> None:
    @feud.command
    def f(arg1: int, *, arg2: bool) -> tuple[int, bool]:  # noqa: FA102
        return arg1, arg2

    assert feud.run(f, ["1", "--no-arg2"], standalone_mode=False) == (1, False)


def test_sensitive_input() -> None:
    @feud.command
    @click.option("--password", type=str, hide_input=True)
    def f(*, password: t.constr(min_length=10)) -> None:
        pass

    msg = """1 validation error for command 'f'
--password
  String should have at least 10 characters [input_value=hidden]
    """.strip()
    with pytest.raises(click.UsageError, match=re.escape(msg)):
        feud.run(f, ["--password", "abc"], standalone_mode=False)
