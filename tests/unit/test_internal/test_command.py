# Copyright (c) 2023 Feud Developers.
# Distributed under the terms of the MIT License (see the LICENSE file).
# SPDX-License-Identifier: MIT
# This source code is part of the Feud project (https://feud.wiki).

from __future__ import annotations

import inspect

import pytest

from feud import click
from feud import typing as t
from feud._internal import _command


def test_get_context_ctx_no_annotation() -> None:
    def f(ctx, a: t.Any, b: t.Any, c: t.Any) -> None:  # noqa: ANN001
        pass

    sig = inspect.signature(f)
    assert _command.pass_context(sig)


def test_get_context_ctx_with_annotation() -> None:
    def f(ctx: click.Context, a: t.Any, b: t.Any, c: t.Any) -> None:
        pass

    sig = inspect.signature(f)
    assert _command.pass_context(sig)


def test_get_context_wrong_name_no_annotation() -> None:
    def f(context, a: t.Any, b: t.Any, c: t.Any) -> None:  # noqa: ANN001
        pass

    sig = inspect.signature(f)
    assert not _command.pass_context(sig)


def test_get_context_wrong_name_with_annotation() -> None:
    def f(context: click.Context, a: t.Any, b: t.Any, c: t.Any) -> None:
        pass

    sig = inspect.signature(f)
    assert not _command.pass_context(sig)


def test_get_context_wrong_position() -> None:
    def f(a: t.Any, b: t.Any, c: t.Any, ctx: click.Context) -> None:
        pass

    sig = inspect.signature(f)
    assert not _command.pass_context(sig)


def test_get_context_positional_only() -> None:
    def f(ctx: click.Context, /, a: t.Any, b: t.Any, c: t.Any) -> None:
        pass

    sig = inspect.signature(f)
    assert _command.pass_context(sig)


def test_get_context_keyword_only() -> None:
    def f(*, ctx: click.Context, a: t.Any, b: t.Any, c: t.Any) -> None:
        pass

    sig = inspect.signature(f)
    assert _command.pass_context(sig)


@pytest.mark.parametrize(
    ("hint", "negate_flags", "expected"),
    [
        (str, False, "--opt"),
        (str, True, "--opt"),
        (bool, False, "--opt"),
        (bool, True, "--opt/--no-opt"),
    ],
)
def test_get_option(hint: type, *, negate_flags: bool, expected: str) -> None:
    assert (
        _command.get_option("opt", hint=hint, negate_flags=negate_flags)
        == expected
    )


@pytest.mark.parametrize(
    ("hint", "negate_flags", "expected"),
    [
        (str, False, "-o"),
        (str, True, "-o"),
        (bool, False, "-o"),
        (bool, True, "-o/--no-o"),
    ],
)
def test_get_alias(hint: type, *, negate_flags: bool, expected: str) -> None:
    assert (
        _command.get_alias("-o", hint=hint, negate_flags=negate_flags)
        == expected
    )


@pytest.mark.parametrize(
    ("click_kwargs", "name", "expected"),
    [
        (
            {"commands": ["a", "b", "c"], "key": "value"},
            "test",
            {"key": "value", "name": "test"},
        ),
        (
            {"key": "value"},
            "a_name",
            {"key": "value", "name": "a_name"},
        ),
        (
            {"key": "value"},
            "_a_name",
            {"key": "value", "name": "_a_name"},
        ),
        (
            {"key": "value"},
            "-a-name",
            {"key": "value", "name": "a-name"},
        ),
        (
            {"key": "value"},
            "--a-name",
            {"key": "value", "name": "a-name"},
        ),
        (
            {"key": "value"},
            "AName",
            {"key": "value", "name": "aname"},
        ),
        (
            {"key": "value"},
            "ClassName",
            {"key": "value", "name": "classname"},
        ),
    ],
)
def test_sanitize_click_kwargs(
    click_kwargs: dict[str, str], name: str, expected: dict[str, str]
) -> None:
    _command.sanitize_click_kwargs(click_kwargs, name=name)
    assert click_kwargs == expected
