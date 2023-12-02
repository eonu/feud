# Copyright (c) 2023-2025 Feud Developers.
# Distributed under the terms of the MIT License (see the LICENSE file).
# SPDX-License-Identifier: MIT
# This source code is part of the Feud project (https://feud.wiki).

"""Officially supported types from the ``pydantic-extra-types`` package."""

try:
    from pydantic_extra_types.color import Color
    from pydantic_extra_types.coordinate import (
        Coordinate,
        Latitude,
        Longitude,
    )
    from pydantic_extra_types.country import (
        CountryAlpha2,
        CountryAlpha3,
        CountryNumericCode,
        CountryOfficialName,
        CountryShortName,
    )
    from pydantic_extra_types.mac_address import MacAddress
    from pydantic_extra_types.payment import (
        PaymentCardBrand,
        PaymentCardNumber,
    )
    from pydantic_extra_types.phone_numbers import PhoneNumber
    from pydantic_extra_types.routing_number import ABARoutingNumber
except ImportError:
    pass
