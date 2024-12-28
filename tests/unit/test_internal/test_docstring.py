# Copyright (c) 2023 Feud Developers.
# Distributed under the terms of the MIT License (see the LICENSE file).
# SPDX-License-Identifier: MIT
# This source code is part of the Feud project (https://feud.wiki).

import enum

import pytest

import feud
from feud._internal import _docstring


class Mode(enum.Enum):
    FUNCTION = "function"
    COMMAND = "command"
    COMMAND_WITH_HELP = "command_with_help"
    STRING = "string"


@pytest.mark.parametrize("mode", list(Mode))
def test_get_description_function_no_doc(mode: Mode) -> None:
    def f() -> None:
        pass

    if mode == Mode.COMMAND:
        f = feud.command()(f)
        assert f.help == _docstring.get_description(f)
    elif mode == Mode.COMMAND_WITH_HELP:
        f = feud.command(help="Override.")(f)
        assert f.help == "Override."
    elif mode == Mode.STRING:
        f = f.__doc__

    assert _docstring.get_description(f) is None


@pytest.mark.parametrize("mode", list(Mode))
def test_get_description_function_single_line_doc(mode: Mode) -> None:
    def f() -> None:
        """Line 1."""

    if mode == Mode.COMMAND:
        f = feud.command()(f)
        assert f.help == _docstring.get_description(f)
    elif mode == Mode.COMMAND_WITH_HELP:
        f = feud.command(help="Override.")(f)
        assert f.help == "Override."
    elif mode == Mode.STRING:
        f = f.__doc__

    assert _docstring.get_description(f) == "Line 1."


@pytest.mark.parametrize("mode", list(Mode))
def test_get_description_function_multi_line_doc(mode: Mode) -> None:
    def f() -> None:
        """Line 1.

        Line 2.
        """

    if mode == Mode.COMMAND:
        f = feud.command()(f)
        assert f.help == _docstring.get_description(f)
    elif mode == Mode.COMMAND_WITH_HELP:
        f = feud.command(help="Override.")(f)
        assert f.help == "Override."
    elif mode == Mode.STRING:
        f = f.__doc__

    assert _docstring.get_description(f) == "Line 1.\n\nLine 2."


@pytest.mark.parametrize("mode", list(Mode))
def test_get_description_function_multi_line_doc_with_f(mode: Mode) -> None:
    def f() -> None:
        """Line 1.

        Line 2.\f
        """

    if mode == Mode.COMMAND:
        f = feud.command()(f)
        assert f.help == _docstring.get_description(f)
    elif mode == Mode.COMMAND_WITH_HELP:
        f = feud.command(help="Override.")(f)
        assert f.help == "Override."
    elif mode == Mode.STRING:
        f = f.__doc__

    assert _docstring.get_description(f) == "Line 1.\n\nLine 2."


@pytest.mark.parametrize("mode", list(Mode))
def test_get_description_function_single_line_doc_with_params(
    mode: Mode
) -> None:
    def f(*, opt: int) -> None:
        """Line 1.

        Parameters
        ----------
        opt:
            An option.
        """

    if mode == Mode.COMMAND:
        f = feud.command()(f)
        assert f.help == _docstring.get_description(f)
        assert f.params[0].help == "An option."
    elif mode == Mode.COMMAND_WITH_HELP:
        f = feud.command(help="Override.")(f)
        assert f.help == "Override."
    elif mode == Mode.STRING:
        f = f.__doc__

    assert _docstring.get_description(f) == "Line 1."


@pytest.mark.parametrize("mode", list(Mode))
def test_get_description_function_multi_line_doc_with_params(
    mode: Mode
) -> None:
    def f(*, opt: int) -> None:
        """Line 1.

        Line 2.

        Parameters
        ----------
        opt:
            An option.
        """

    if mode == Mode.COMMAND:
        f = feud.command()(f)
        assert f.help == _docstring.get_description(f)
        assert f.params[0].help == "An option."
    elif mode == Mode.COMMAND_WITH_HELP:
        f = feud.command(help="Override.")(f)
        assert f.help == "Override."
    elif mode == Mode.STRING:
        f = f.__doc__

    assert _docstring.get_description(f) == "Line 1.\n\nLine 2."


@pytest.mark.parametrize("mode", list(Mode))
def test_get_description_function_multi_line_doc_with_params_and_f(
    mode: Mode,
) -> None:
    def f(*, opt: int) -> None:
        """Line 1.

        Line 2.\f

        Parameters
        ----------
        opt
            An option.
        """

    if mode == Mode.COMMAND:
        f = feud.command()(f)
        assert f.help == _docstring.get_description(f)
        assert f.params[0].help == "An option."
    elif mode == Mode.COMMAND_WITH_HELP:
        f = feud.command(help="Override.")(f)
        assert f.help == "Override."
    elif mode == Mode.STRING:
        f = f.__doc__

    assert _docstring.get_description(f) == "Line 1.\n\nLine 2."


def test_get_description_class_single_line_no_doc() -> None:
    class Group(feud.Group):
        pass

    assert Group.compile().help is None


def test_get_description_class_single_line_doc() -> None:
    class Group(feud.Group):
        """Line 1."""

    assert Group.compile().help == "Line 1."


def test_get_description_class_single_line_doc_with_examples() -> None:
    class Group(feud.Group):
        """Line 1.

        Examples
        --------
        >>> # Hello World!
        """

    assert Group.compile().help == "Line 1."


def test_get_description_class_multi_line_doc() -> None:
    class Group(feud.Group):
        """Line 1.

        Line 2.
        """

    assert Group.compile().help == "Line 1.\n\nLine 2."


def test_get_description_class_multi_line_doc_with_examples() -> None:
    class Group(feud.Group):
        """Line 1.

        Line 2.

        Examples
        --------
        >>> # Hello World!
        """

    assert Group.compile().help == "Line 1.\n\nLine 2."


def test_get_description_class_multi_line_doc_with_f() -> None:
    class Group(feud.Group):
        """Line 1.

        Line 2.\f
        """

    assert Group.compile().help == "Line 1.\n\nLine 2."


def test_get_description_class_multi_line_doc_with_examples_and_f() -> None:
    class Group(feud.Group):
        """Line 1.

        Line 2.\f

        Examples
        --------
        >>> # Hello World!
        """

    assert Group.compile().help == "Line 1.\n\nLine 2."


def test_get_description_class_main() -> None:
    class Group(feud.Group):
        def __main__() -> None:
            """Line 1.

            Line 2.\f

            Examples
            --------
            >>> # Hello World!
            """

    assert Group.compile().help == "Line 1.\n\nLine 2."


def test_get_description_class_override() -> None:
    class Group(feud.Group, help="Override."):
        """Line 1.

        Line 2.\f

        Examples
        --------
        >>> # Hello World!
        """

    assert Group.compile().help == "Override."
