# Copyright (c) 2023 Feud Developers.
# Distributed under the terms of the MIT License (see the LICENSE file).
# SPDX-License-Identifier: MIT
# This source code is part of the Feud project (https://feud.wiki).

"""Unit tests for ``feud.decorators``."""

import enum

import pytest

from feud import click
from feud import typing as t
from feud._internal import _decorators


def test_validate_call_single_invalid() -> None:
    """Check output when ``validate_call`` receives a single invalid input
    value.
    """
    name = "func"
    param_renames = {}
    meta_vars = {"arg2": "--arg2"}
    sensitive_vars = {"arg2": False}
    positional = []
    var_positional = None
    pydantic_kwargs = {}

    def f(*, arg2: t.Literal["a", "b", "c"]) -> None:
        pass

    with pytest.raises(click.UsageError) as e:
        _decorators.validate_call(
            f,
            name=name,
            param_renames=param_renames,
            meta_vars=meta_vars,
            sensitive_vars=sensitive_vars,
            positional=positional,
            var_positional=var_positional,
            pydantic_kwargs=pydantic_kwargs,
        )(arg2="invalid")

    assert (
        str(e.value)
        == """
1 validation error for command 'func'
--arg2
  Input should be 'a', 'b' or 'c' [input_value='invalid']
""".strip()
    )


def test_validate_call_multiple_invalid() -> None:
    """Check output when ``validate_call`` receives multiple invalid
    input values.
    """
    name = "func"
    param_renames = {}
    meta_vars = {"0": "ARG1", "arg2": "--arg2"}
    sensitive_vars = {"0": False, "arg2": False}
    positional = []
    var_positional = None
    pydantic_kwargs = {}

    def f(arg1: int, *, arg2: t.Literal["a", "b", "c"]) -> None:
        pass

    with pytest.raises(click.UsageError) as e:
        _decorators.validate_call(
            f,
            name=name,
            param_renames=param_renames,
            meta_vars=meta_vars,
            sensitive_vars=sensitive_vars,
            positional=positional,
            var_positional=var_positional,
            pydantic_kwargs=pydantic_kwargs,
        )("invalid", arg2="invalid")

    assert (
        str(e.value)
        == """
2 validation errors for command 'func'
ARG1
  Input should be a valid integer, unable to parse string as an integer [input_value='invalid']
--arg2
  Input should be 'a', 'b' or 'c' [input_value='invalid']
""".strip()  # noqa: E501
    )


def test_validate_call_list() -> None:
    """Check output when ``validate_call`` receives an invalid input value for
    a list argument.
    """
    name = "func"
    param_renames = {}
    meta_vars = {"0": "[ARG1]..."}
    sensitive_vars = {"0": False}
    positional = []
    var_positional = None
    pydantic_kwargs = {}

    def f(arg1: list[t.conint(multiple_of=2)]) -> None:
        pass

    with pytest.raises(click.UsageError) as e:
        _decorators.validate_call(
            f,
            name=name,
            param_renames=param_renames,
            meta_vars=meta_vars,
            sensitive_vars=sensitive_vars,
            positional=positional,
            var_positional=var_positional,
            pydantic_kwargs=pydantic_kwargs,
        )([1, 2, 3])

    assert (
        str(e.value)
        == """
2 validation errors for command 'func'
[ARG1]... [0]
  Input should be a multiple of 2 [input_value=1]
[ARG1]... [2]
  Input should be a multiple of 2 [input_value=3]
""".strip()
    )


def test_validate_call_enum() -> None:
    """Check output when ``validate_call`` receives an invalid input value
    for an enum parameter.
    """
    name = "func"
    param_renames = {}
    meta_vars = {"arg2": "--arg2"}
    sensitive_vars = {"arg2": False}
    positional = []
    var_positional = None
    pydantic_kwargs = {}

    class Choice(enum.Enum):
        A = "a"
        B = "b"
        C = "c"

    def f(*, arg2: Choice) -> None:
        pass

    with pytest.raises(click.UsageError) as e:
        _decorators.validate_call(
            f,
            name=name,
            param_renames=param_renames,
            meta_vars=meta_vars,
            sensitive_vars=sensitive_vars,
            positional=positional,
            var_positional=var_positional,
            pydantic_kwargs=pydantic_kwargs,
        )(arg2="invalid")

    assert (
        str(e.value)
        == """
1 validation error for command 'func'
--arg2
  Input should be 'a', 'b' or 'c' [input_value='invalid']
""".strip()
    )


def test_validate_call_datetime() -> None:
    """Check output when ``validate_call`` receives an invalid input value
    for a datetime parameter.
    """
    name = "func"
    param_renames = {}
    meta_vars = {"time": "--time"}
    sensitive_vars = {"time": False}
    positional = []
    var_positional = None
    pydantic_kwargs = {}

    def f(*, time: t.FutureDatetime) -> None:
        pass

    with pytest.raises(click.UsageError) as e:
        _decorators.validate_call(
            f,
            name=name,
            param_renames=param_renames,
            meta_vars=meta_vars,
            sensitive_vars=sensitive_vars,
            positional=positional,
            var_positional=var_positional,
            pydantic_kwargs=pydantic_kwargs,
        )(time=t.datetime.now())

    assert str(e.value).startswith(
        """
1 validation error for command 'func'
--time
  Input should be in the future
""".strip()
    )
