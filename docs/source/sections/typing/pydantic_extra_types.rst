Pydantic extra types
====================

`Pydantic Extra Types <https://github.com/pydantic/pydantic-extra-types>`__ 
is a package that extends `Pydantic <https://docs.pydantic.dev/latest/>`__
with support for additional types.

The following types can be used as type hints for Feud commands.

.. important::

    This page may only list a subset of types from the Pydantic Extra Types package.
    
    All `extra types <https://github.com/pydantic/pydantic-extra-types>`__ 
    (including those not listed on this page) are compatible with Feud.

.. tip::

    All of the types listed on this page are easily accessible from the :py:mod:`feud.typing` module.

    It is recommended to import the :py:mod:`feud.typing` module with an alias such as ``t`` for convenient short-hand use, e.g.

    .. code:: python

        from feud import typing as t

        t.PhoneNumber  # pydantic_extra_types.phone_number.PhoneNumbers
        t.PaymentCardNumber  # pydantic_extra_types.payment.PaymentCardNumber
        t.Latitude  # pydantic_extra_types.coordinate.Latitude
        t.Color  # pydantic_extra_types.color.Color

.. contents:: Table of Contents
    :class: this-will-duplicate-information-and-it-is-still-useful-here
    :local:
    :backlinks: none
    :depth: 3

----

Color type
----------

- :py:obj:`pydantic_extra_types.color.Color`

Coordinate types
----------------

- :py:obj:`pydantic_extra_types.coordinate.Coordinate`
- :py:obj:`pydantic_extra_types.coordinate.Latitude`
- :py:obj:`pydantic_extra_types.coordinate.Longitude`

Country types
-------------

- :py:obj:`pydantic_extra_types.country.CountryAlpha2`
- :py:obj:`pydantic_extra_types.country.CountryAlpha3`
- :py:obj:`pydantic_extra_types.country.CountryNumericCode`
- :py:obj:`pydantic_extra_types.country.CountryOfficialName`
- :py:obj:`pydantic_extra_types.country.CountryShortName`

Phone number type
-----------------

- :py:obj:`pydantic_extra_types.phone_numbers.PhoneNumber`

Payment types
-------------

- :py:obj:`pydantic_extra_types.payment.PaymentCardBrand`
- :py:obj:`pydantic_extra_types.payment.PaymentCardNumber`

MAC address type
----------------

- :py:obj:`pydantic_extra_types.mac_address.MacAddress`

Routing number type
-------------------

- :py:obj:`pydantic_extra_types.routing_number.ABARoutingNumber`
