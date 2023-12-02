# Copyright (c) 2023-2025 Feud Developers.
# Distributed under the terms of the MIT License (see the LICENSE file).
# SPDX-License-Identifier: MIT
# This source code is part of the Feud project (https://feud.wiki).

import pytest

import feud


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


def test_invalid_format() -> None:
    with pytest.raises(feud.CompilationError):

        @feud.alias(arg1="-a1")
        def f(*, arg1: int) -> None:
            pass


def test_alias_argument() -> None:
    with pytest.raises(feud.CompilationError):

        @feud.alias(arg1="-a")
        def f(arg1: int) -> None:
            pass
