# Copyright (c) 2023 Feud Developers.
# Distributed under the terms of the MIT License (see the LICENSE file).
# SPDX-License-Identifier: MIT
# This source code is part of the Feud project (https://feud.wiki).

import pytest

from feud import typing as t
from feud._internal import _types
from feud.config import Config


@pytest.fixture(scope="module")
def config() -> Config:
    return Config._create()  # noqa: SLF001


@pytest.fixture(scope="module")
def helpers(helpers: type) -> type:  # type[Helpers]
    def is_lambda(__obj: t.Any, /) -> bool:
        return (
            callable(__obj)
            and getattr(__obj, "__name__", None) == (lambda: None).__name__
        )

    # register is_lambda helper
    helpers.is_lambda = is_lambda

    def check_get_click_type(
        *,
        config: Config,
        annotated: bool,
        hint: t.Any,
        expected: t.Tuple[bool, t.Any],
    ) -> None:
        if annotated:
            hint = helpers.annotate(hint)

        result = _types.click.get_click_type(hint, config=config)

        if helpers.is_lambda(expected):
            assert expected(result)
        else:
            assert result == expected

    # register check_get_click_type helper
    helpers.check_get_click_type = check_get_click_type

    return helpers
