# Copyright (c) 2023 Feud Developers.
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
        """Do something.

        Parameters
        ----------
        arg1:
            Controls something.

        arg2:
            Changes something.
        """

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
    def f(arg1: int, *, arg2: bool) -> tuple[int, bool]:
        return arg1, arg2

    assert feud.run(f, ["1", "--no-arg2"], standalone_mode=False) == (1, False)


def test_run_decorated() -> None:
    @feud.command
    def f(arg1: int, *, arg2: bool) -> tuple[int, bool]:
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


@pytest.mark.parametrize("command", [True, False])
def test_run_dict(capsys: pytest.CaptureFixture, *, command: bool) -> None:
    def first(arg1: int, *, opt1: float, opt2: bool = False) -> None:
        """The first command.

        Parameters
        ----------
        arg1:
            An argument.
        opt1:
            The first option.
        opt2:
            The second option.
        """

    def second(*, opt: int) -> None:
        """The second command.

        Parameters
        ----------
        opt:
            An option.
        """

    if command:
        first = feud.command()(first)
        second = feud.command()(second)

    with pytest.raises(SystemExit):
        feud.run({"1st": first, "2nd": second}, ["--help"])

    out, _ = capsys.readouterr()

    assert (
        out.strip()
        == """
Usage: pytest [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  1st  The first command.
  2nd  The second command.
        """.strip()
    )

    with pytest.raises(SystemExit):
        feud.run({"1st": first, "2nd": second}, ["1st", "--help"])

    out, _ = capsys.readouterr()

    assert (
        out.strip()
        == """
Usage: pytest 1st [OPTIONS] ARG1

  The first command.

Options:
  --opt1 FLOAT        The first option.  [required]
  --opt2 / --no-opt2  The second option.  [default: no-opt2]
  --help              Show this message and exit.
        """.strip()
    )


@pytest.mark.parametrize("command", [True, False])
def test_run_iterable(capsys: pytest.CaptureFixture, *, command: bool) -> None:
    def first(arg1: int, *, opt1: float, opt2: bool = False) -> None:
        """The first command.

        Parameters
        ----------
        arg1:
            An argument.
        opt1:
            The first option.
        opt2:
            The second option.
        """

    def second(*, opt: int) -> None:
        """The second command.

        Parameters
        ----------
        opt:
            An option.
        """

    if command:
        first = feud.command()(first)
        second = feud.command()(second)

    with pytest.raises(SystemExit):
        feud.run((first, second), ["--help"])

    out, _ = capsys.readouterr()

    assert (
        out.strip()
        == """
Usage: pytest [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  first   The first command.
  second  The second command.
        """.strip()
    )

    with pytest.raises(SystemExit):
        feud.run((first, second), ["first", "--help"])

    out, _ = capsys.readouterr()

    assert (
        out.strip()
        == """
Usage: pytest first [OPTIONS] ARG1

  The first command.

Options:
  --opt1 FLOAT        The first option.  [required]
  --opt2 / --no-opt2  The second option.  [default: no-opt2]
  --help              Show this message and exit.
        """.strip()
    )


def test_full_signature(
    capsys: pytest.CaptureFixture,
) -> None:
    @feud.command
    def command(
        a: float,
        /,
        b: str,
        *c: t.PositiveInt,
        d: int,
        e: bool = True,
        **f: float,
    ) -> None:
        """Does something.

        Parameters
        ----------
        a:
            Test 1.
        b:
            Test 2.
        *c:
            Test 3.
        d:
            Test 4.
        e:
            Test 5.
        **f:
            Test 6.
        """
        return a, b, c, d, e, f

    # check params (**f should be ignored)
    params = command.params
    assert len(params) == 5

    a = command.params[0]
    assert isinstance(a, click.Argument)
    assert a.name == "a"
    assert a.type == click.FLOAT
    assert a.opts == ["a"]
    assert a.secondary_opts == []
    assert a.nargs == 1
    assert a.required
    assert a.default is None

    b = command.params[1]
    assert isinstance(b, click.Argument)
    assert b.name == "b"
    assert b.type == click.STRING
    assert b.opts == ["b"]
    assert b.secondary_opts == []
    assert b.nargs == 1
    assert b.required
    assert b.default is None

    c = command.params[2]
    assert isinstance(c, click.Argument)
    assert c.name == "c"
    assert isinstance(c.type, click.IntRange)
    assert c.type.min == 0
    assert c.type.min_open
    assert c.opts == ["c"]
    assert c.secondary_opts == []
    assert c.nargs == -1
    assert not c.required
    assert c.default is None

    d = command.params[3]
    assert isinstance(d, click.Option)
    assert d.name == "d"
    assert d.help == "Test 4."
    assert d.type == click.INT
    assert d.opts == ["--d"]
    assert d.secondary_opts == []
    assert d.nargs == 1
    assert d.required
    assert d.default is None

    e = command.params[4]
    assert isinstance(e, click.Option)
    assert e.name == "e"
    assert e.help == "Test 5."
    assert e.type == click.BOOL
    assert e.opts == ["--e"]
    assert e.secondary_opts == ["--no-e"]
    assert e.nargs == 1
    assert not e.required
    assert e.default is True


def test_full_signature_string_hints(
    capsys: pytest.CaptureFixture,
) -> None:
    @feud.command
    def command(
        a: "float",
        /,
        b: "str",
        *c: "t.PositiveInt",
        d: "int",
        e: "bool" = True,
        **f: "float",
    ) -> None:
        """Does something.

        Parameters
        ----------
        a:
            Test 1.
        b:
            Test 2.
        *c:
            Test 3.
        d:
            Test 4.
        e:
            Test 5.
        **f:
            Test 6.
        """
        return a, b, c, d, e, f

    # check params (**f should be ignored)
    params = command.params
    assert len(params) == 5

    a = command.params[0]
    assert isinstance(a, click.Argument)
    assert a.name == "a"
    assert a.type == click.FLOAT
    assert a.opts == ["a"]
    assert a.secondary_opts == []
    assert a.nargs == 1
    assert a.required
    assert a.default is None

    b = command.params[1]
    assert isinstance(b, click.Argument)
    assert b.name == "b"
    assert b.type == click.STRING
    assert b.opts == ["b"]
    assert b.secondary_opts == []
    assert b.nargs == 1
    assert b.required
    assert b.default is None

    c = command.params[2]
    assert isinstance(c, click.Argument)
    assert c.name == "c"
    assert isinstance(c.type, click.IntRange)
    assert c.type.min == 0
    assert c.type.min_open
    assert c.opts == ["c"]
    assert c.secondary_opts == []
    assert c.nargs == -1
    assert not c.required
    assert c.default is None

    d = command.params[3]
    assert isinstance(d, click.Option)
    assert d.name == "d"
    assert d.help == "Test 4."
    assert d.type == click.INT
    assert d.opts == ["--d"]
    assert d.secondary_opts == []
    assert d.nargs == 1
    assert d.required
    assert d.default is None

    e = command.params[4]
    assert isinstance(e, click.Option)
    assert e.name == "e"
    assert e.help == "Test 5."
    assert e.type == click.BOOL
    assert e.opts == ["--e"]
    assert e.secondary_opts == ["--no-e"]
    assert e.nargs == 1
    assert not e.required
    assert e.default is True


def test_argument_default() -> None:
    @feud.command
    def f(
        a: int,
        /,
        b: float,
        c: bool = True,  # noqa: FBT001, FBT002
    ) -> None:
        pass

    assert len(f.params) == 3

    a = f.params[0]
    assert isinstance(a, click.Argument)
    assert a.name == "a"
    assert a.type == click.INT
    assert a.opts == ["a"]
    assert a.secondary_opts == []
    assert a.nargs == 1
    assert a.required
    assert a.default is None

    b = f.params[1]
    assert isinstance(b, click.Argument)
    assert b.name == "b"
    assert b.type == click.FLOAT
    assert b.opts == ["b"]
    assert b.secondary_opts == []
    assert b.nargs == 1
    assert b.required
    assert b.default is None

    c = f.params[2]
    assert isinstance(c, click.Argument)
    assert c.name == "c"
    assert c.type == click.BOOL
    assert c.opts == ["c"]
    assert c.secondary_opts == []
    assert c.nargs == 1
    assert not c.required
    assert c.default is True
