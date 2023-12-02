# Copyright (c) 2023-2025 Feud Developers.
# Distributed under the terms of the MIT License (see the LICENSE file).
# SPDX-License-Identifier: MIT
# This source code is part of the Feud project (https://feud.wiki).

from __future__ import annotations

import click
import pytest

from feud import typing as t
from feud.config import Config


@pytest.mark.parametrize("annotated", [False, True])
@pytest.mark.parametrize(
    ("hint", "expected"),
    [
        # pydantic extra types
        (t.Color, click.STRING),
        (t.Latitude, click.FLOAT),
        (t.Longitude, click.FLOAT),
        (t.Coordinate, (click.FLOAT, click.FLOAT)),
        (t.CountryAlpha2, click.STRING),
        (t.CountryAlpha3, click.STRING),
        (t.CountryNumericCode, click.STRING),
        (t.CountryShortName, click.STRING),
        (t.CountryOfficialName, click.STRING),
        (t.MacAddress, click.STRING),
        (t.PaymentCardNumber, click.STRING),
        (
            t.PaymentCardBrand,
            lambda x: isinstance(x, click.Choice)
            and x.choices
            == ["American Express", "Mastercard", "Visa", "Mir", "other"],
        ),
        (t.PhoneNumber, click.STRING),
        (t.ABARoutingNumber, click.STRING),
    ],
)
def test_pydantic_extra(
    helpers: type,
    *,
    config: Config,
    annotated: bool,
    hint: t.Any,
    expected: click.ParamType | None,
) -> None:
    helpers.check_get_click_type(
        config=config,
        annotated=annotated,
        hint=hint,
        expected=expected,
    )
