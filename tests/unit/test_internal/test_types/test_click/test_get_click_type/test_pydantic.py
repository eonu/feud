# Copyright (c) 2023 Feud Developers.
# Distributed under the terms of the MIT License (see the LICENSE file).
# SPDX-License-Identifier: MIT
# This source code is part of the Feud project (https://feud.wiki).

from __future__ import annotations

import click
import pydantic as pyd
import pytest

from feud import typing as t
from feud._internal._types.click import DateTime
from feud.config import Config


@pytest.mark.parametrize("annotated", [False, True])
@pytest.mark.parametrize(
    ("hint", "expected"),
    [
        # pydantic types
        (t.AmqpDsn, None),
        (t.AnyHttpUrl, None),
        (t.AnyUrl, None),
        (
            t.AwareDatetime,
            lambda x: (
                isinstance(x, DateTime) and x.name == t.datetime.__name__
            ),
        ),
        (t.Base64Bytes, None),
        (t.Base64Str, click.STRING),
        (t.ByteSize, None),
        (t.CockroachDsn, None),
        (
            t.DirectoryPath,
            lambda x: isinstance(x, click.Path) and x.exists is True,
        ),
        (t.EmailStr, None),
        (
            t.FilePath,
            lambda x: isinstance(x, click.Path) and x.exists is True,
        ),
        (t.FileUrl, None),
        (t.FiniteFloat, click.FLOAT),
        (
            t.FutureDate,
            lambda x: isinstance(x, DateTime) and x.name == t.date.__name__,
        ),
        (
            t.FutureDatetime,
            lambda x: (
                isinstance(x, DateTime) and x.name == t.datetime.__name__
            ),
        ),
        (t.HttpUrl, None),
        (t.IPvAnyAddress, None),
        (t.IPvAnyInterface, None),
        (t.IPvAnyNetwork, None),
        (t.ImportString, None),
        (t.Json, None),
        (t.KafkaDsn, None),
        (t.MariaDBDsn, None),
        (t.MongoDsn, None),
        (t.MySQLDsn, None),
        (
            t.NaiveDatetime,
            lambda x: (
                isinstance(x, DateTime) and x.name == t.datetime.__name__
            ),
        ),
        (t.NameEmail, None),
        (
            t.NegativeFloat,
            lambda x: isinstance(x, click.FloatRange)
            and x.min is None
            and x.min_open is False
            and x.max == 0
            and x.max_open is True,
        ),
        (
            t.NegativeInt,
            lambda x: isinstance(x, click.IntRange)
            and x.min is None
            and x.min_open is False
            and x.max == 0
            and x.max_open is True,
        ),
        (
            t.NewPath,
            lambda x: isinstance(x, click.Path) and x.exists is False,
        ),
        (
            t.NonNegativeFloat,
            lambda x: isinstance(x, click.FloatRange)
            and x.min == 0
            and x.min_open is False
            and x.max is None
            and x.max_open is False,
        ),
        (
            t.NonNegativeInt,
            lambda x: isinstance(x, click.IntRange)
            and x.min == 0
            and x.min_open is False
            and x.max is None
            and x.max_open is False,
        ),
        (
            t.NonPositiveFloat,
            lambda x: isinstance(x, click.FloatRange)
            and x.min is None
            and x.min_open is False
            and x.max == 0
            and x.max_open is False,
        ),
        (
            t.NonPositiveInt,
            lambda x: isinstance(x, click.IntRange)
            and x.min is None
            and x.min_open is False
            and x.max == 0
            and x.max_open is False,
        ),
        (
            t.PastDate,
            lambda x: isinstance(x, DateTime) and x.name == t.date.__name__,
        ),
        (
            t.PastDatetime,
            lambda x: (
                isinstance(x, DateTime) and x.name == t.datetime.__name__
            ),
        ),
        (
            t.PositiveFloat,
            lambda x: isinstance(x, click.FloatRange)
            and x.min == 0
            and x.min_open is True
            and x.max is None
            and x.max_open is False,
        ),
        (
            t.PositiveInt,
            lambda x: isinstance(x, click.IntRange)
            and x.min == 0
            and x.min_open is True
            and x.max is None
            and x.max_open is False,
        ),
        (t.PostgresDsn, None),
        (t.RedisDsn, None),
        (t.SecretBytes, None),
        (t.SecretStr, None),
        (t.SkipValidation, None),
        (t.StrictBool, click.BOOL),
        (t.StrictBytes, None),
        (t.StrictFloat, click.FLOAT),
        (t.StrictInt, click.INT),
        (t.StrictStr, click.STRING),
        (t.UUID1, click.UUID),
        (t.UUID3, click.UUID),
        (t.UUID4, click.UUID),
        (t.UUID5, click.UUID),
        (t.conbytes(max_length=1), None),
        (
            t.condate(lt=t.date.today()),
            lambda x: isinstance(x, DateTime) and x.name == t.date.__name__,
        ),
        (
            t.condecimal(lt=t.Decimal("3.14"), ge=t.Decimal("0.01")),
            lambda x: isinstance(x, click.FloatRange)
            and x.min == t.Decimal("0.01")
            and x.min_open is False
            and x.max == t.Decimal("3.14")
            and x.max_open is True,
        ),
        (
            t.confloat(lt=3.14, ge=0.01),
            lambda x: isinstance(x, click.FloatRange)
            and x.min == 0.01
            and x.min_open is False
            and x.max == 3.14
            and x.max_open is True,
        ),
        (t.confrozenset(int, max_length=1), click.INT),
        (
            t.conint(lt=3, ge=0),
            lambda x: isinstance(x, click.IntRange)
            and x.min == 0
            and x.min_open is False
            and x.max == 3
            and x.max_open is True,
        ),
        (t.conlist(int, max_length=1), click.INT),
        (t.conset(int, max_length=1), click.INT),
        (t.constr(max_length=1), click.STRING),
        (t.Annotated[int, pyd.AfterValidator(lambda x: x + 1)], click.INT),
        (t.Base64UrlBytes, None),
        (t.Base64UrlStr, click.STRING),
        (t.JsonValue, None),
        (t.NatsDsn, None),
        (t.ClickHouseDsn, None),
        (t.FtpUrl, None),
        (t.WebsocketUrl, None),
        (t.AnyWebsocketUrl, None),
        (t.SnowflakeDsn, None),
        (t.SocketPath, lambda x: isinstance(x, click.Path)),
    ],
)
def test_pydantic(
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
