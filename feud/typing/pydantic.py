# Copyright (c) 2023-2025 Feud Developers.
# Distributed under the terms of the MIT License (see the LICENSE file).
# SPDX-License-Identifier: MIT
# This source code is part of the Feud project (https://feud.wiki).

"""Officially supported types from the ``pydantic`` package."""

from pydantic import (
    UUID1,
    UUID3,
    UUID4,
    UUID5,
    AmqpDsn,
    AnyHttpUrl,
    AnyUrl,
    AwareDatetime,
    Base64Bytes,
    Base64Str,
    ByteSize,
    CockroachDsn,
    DirectoryPath,
    EmailStr,
    FilePath,
    FileUrl,
    FiniteFloat,
    FutureDate,
    FutureDatetime,
    HttpUrl,
    ImportString,
    IPvAnyAddress,
    IPvAnyInterface,
    IPvAnyNetwork,
    Json,
    KafkaDsn,
    MariaDBDsn,
    MongoDsn,
    MySQLDsn,
    NaiveDatetime,
    NameEmail,
    NegativeFloat,
    NegativeInt,
    NewPath,
    NonNegativeFloat,
    NonNegativeInt,
    NonPositiveFloat,
    NonPositiveInt,
    PastDate,
    PastDatetime,
    PositiveFloat,
    PositiveInt,
    PostgresDsn,
    RedisDsn,
    SecretBytes,
    SecretStr,
    SkipValidation,
    StrictBool,
    StrictBytes,
    StrictFloat,
    StrictInt,
    StrictStr,
    conbytes,
    condate,
    condecimal,
    confloat,
    confrozenset,
    conint,
    conlist,
    conset,
    constr,
)
