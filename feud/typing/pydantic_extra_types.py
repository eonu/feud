# Copyright (c) 2023 Feud Developers.
# Distributed under the terms of the MIT License (see the LICENSE file).
# SPDX-License-Identifier: MIT
# This source code is part of the Feud project (https://feud.wiki).

"""Officially supported types from the ``pydantic-extra-types`` package."""

from __future__ import annotations

__all__: list[str] = []

from operator import attrgetter

import packaging.version


def split(string: str) -> str:
    return string.split(".")[-1]


try:
    import pydantic_extra_types  # type: ignore[import-not-found]

    version: packaging.version.Version = packaging.version.parse(
        pydantic_extra_types.__version__,
    )

    if version >= packaging.version.parse("2.1.0"):
        import pydantic_extra_types.color  # type: ignore[import-not-found]
        import pydantic_extra_types.coordinate  # type: ignore[import-not-found]
        import pydantic_extra_types.country  # type: ignore[import-not-found]
        import pydantic_extra_types.mac_address  # type: ignore[import-not-found]
        import pydantic_extra_types.payment  # type: ignore[import-not-found]
        import pydantic_extra_types.phone_numbers  # type: ignore[import-not-found]
        import pydantic_extra_types.routing_number  # type: ignore[import-not-found]

        types: list[str] = [
            "color.Color",
            "coordinate.Coordinate",
            "coordinate.Latitude",
            "coordinate.Longitude",
            "country.CountryAlpha2",
            "country.CountryAlpha3",
            "country.CountryNumericCode",
            "country.CountryShortName",
            "mac_address.MacAddress",
            "payment.PaymentCardBrand",
            "payment.PaymentCardNumber",
            "phone_numbers.PhoneNumber",
            "routing_number.ABARoutingNumber",
        ]

        if version < packaging.version.parse("2.4.0"):
            types.append("country.CountryOfficialName")

        globals().update(
            {
                split(attr): attrgetter(attr)(pydantic_extra_types)
                for attr in types
            }
        )

        __all__.extend(map(split, types))

    if version >= packaging.version.parse("2.2.0"):
        from pydantic_extra_types.ulid import (  # type: ignore[import-not-found]
            ULID,
        )

        __all__.append("ULID")

    if version >= packaging.version.parse("2.4.0"):
        from pydantic_extra_types.isbn import (  # type: ignore[import-not-found]
            ISBN,
        )

        __all__.append("ISBN")

    if version >= packaging.version.parse("2.7.0"):
        from pydantic_extra_types.language_code import (  # type: ignore[import-not-found]
            LanguageAlpha2,
            LanguageName,
        )

        __all__.extend(["LanguageAlpha2", "LanguageName"])

    if version >= packaging.version.parse("2.9.0"):
        from pydantic_extra_types.semantic_version import (  # type: ignore[import-not-found]
            SemanticVersion,
        )

        __all__.append("SemanticVersion")

    if version >= packaging.version.parse("2.10.0"):
        from pydantic_extra_types.s3 import (  # type: ignore[import-not-found]
            S3Path,
        )

        __all__.append("S3Path")

except ImportError:
    pass
