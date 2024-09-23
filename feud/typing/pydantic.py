# Copyright (c) 2023-2025 Feud Developers.
# Distributed under the terms of the MIT License (see the LICENSE file).
# SPDX-License-Identifier: MIT
# This source code is part of the Feud project (https://feud.wiki).

"""Officially supported types from the ``pydantic`` package."""

from __future__ import annotations

__all__ = []

import packaging.version
import pydantic

version: packaging.version.Version = packaging.version.parse(
    pydantic.__version__,
)

if version >= packaging.version.parse("2.0.3"):
    __all__.extend(
        [
            "UUID1",
            "UUID3",
            "UUID4",
            "UUID5",
            "AmqpDsn",
            "AnyHttpUrl",
            "AnyUrl",
            "AwareDatetime",
            "Base64Bytes",
            "Base64Str",
            "ByteSize",
            "CockroachDsn",
            "DirectoryPath",
            "EmailStr",
            "FilePath",
            "FileUrl",
            "FiniteFloat",
            "FutureDate",
            "FutureDatetime",
            "HttpUrl",
            "ImportString",
            "IPvAnyAddress",
            "IPvAnyInterface",
            "IPvAnyNetwork",
            "Json",
            "KafkaDsn",
            "MariaDBDsn",
            "MongoDsn",
            "MySQLDsn",
            "NaiveDatetime",
            "NameEmail",
            "NegativeFloat",
            "NegativeInt",
            "NewPath",
            "NonNegativeFloat",
            "NonNegativeInt",
            "NonPositiveFloat",
            "NonPositiveInt",
            "PastDate",
            "PastDatetime",
            "PositiveFloat",
            "PositiveInt",
            "PostgresDsn",
            "RedisDsn",
            "SecretBytes",
            "SecretStr",
            "SkipValidation",
            "StrictBool",
            "StrictBytes",
            "StrictFloat",
            "StrictInt",
            "StrictStr",
            "conbytes",
            "condate",
            "condecimal",
            "confloat",
            "confrozenset",
            "conint",
            "conlist",
            "conset",
            "constr",
        ]
    )

if version >= packaging.version.parse("2.4.0"):
    types: list[str] = ["Base64UrlBytes", "Base64UrlStr"]

    __all__.extend(types)

if version >= packaging.version.parse("2.5.0"):
    types: list[str] = ["JsonValue"]

    __all__.extend(types)

if version >= packaging.version.parse("2.6.0"):
    types: list[str] = ["NatsDsn"]

    __all__.extend(types)

if version >= packaging.version.parse("2.7.0"):
    types: list[str] = ["ClickHouseDsn"]

    __all__.extend(types)

if version >= packaging.version.parse("2.7.1"):
    types: list[str] = ["FtpUrl", "WebsocketUrl", "AnyWebsocketUrl"]

    __all__.extend(types)

if version >= packaging.version.parse("2.9.0"):
    types: list[str] = ["SnowflakeDsn"]

    __all__.extend(types)

globals().update({attr: getattr(pydantic, attr) for attr in __all__})
