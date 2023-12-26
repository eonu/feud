# Copyright (c) 2023-2025 Feud Developers.
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
    STRING = "string"


@pytest.mark.parametrize("mode", list(Mode))
def test_get_description_function_no_doc(mode: Mode) -> None:
    def f() -> None:
        pass

    if mode == Mode.COMMAND:
        f = feud.command()(f)
    elif mode == Mode.STRING:
        f = f.__doc__

    assert _docstring.get_description(f) is None


@pytest.mark.parametrize("mode", list(Mode))
def test_get_description_function_single_line_doc(mode: Mode) -> None:
    def f() -> None:
        """Line 1."""

    if mode == Mode.COMMAND:
        f = feud.command()(f)
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
        assert f.params[0].help == "An option."
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
        assert f.params[0].help == "An option."
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
        assert f.params[0].help == "An option."
    elif mode == Mode.STRING:
        f = f.__doc__

    assert _docstring.get_description(f) == "Line 1.\n\nLine 2."
