Pydantic extra types
====================

.. contents:: Table of Contents
    :class: this-will-duplicate-information-and-it-is-still-useful-here
    :local:
    :backlinks: none
    :depth: 3

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

----

The version number indicates the minimum ``pydantic-extra-types`` version required to use the type. 

If this version requirement is not met, the type is not imported by Feud.

Color type
----------

- :py:obj:`pydantic_extra_types.color.Color` (``>= 2.1.0``)

Coordinate types
----------------

- :py:obj:`pydantic_extra_types.coordinate.Coordinate` (``>= 2.1.0``)
- :py:obj:`pydantic_extra_types.coordinate.Latitude` (``>= 2.1.0``)
- :py:obj:`pydantic_extra_types.coordinate.Longitude` (``>= 2.1.0``)

Country types
-------------

- :py:obj:`pydantic_extra_types.country.CountryAlpha2` (``>= 2.1.0``)
- :py:obj:`pydantic_extra_types.country.CountryAlpha3` (``>= 2.1.0``)
- :py:obj:`pydantic_extra_types.country.CountryNumericCode` (``>= 2.1.0``)
- :py:obj:`pydantic_extra_types.country.CountryOfficialName` (``>= 2.1.0, <2.4.0``)
- :py:obj:`pydantic_extra_types.country.CountryShortName` (``>= 2.1.0``)

ISBN type
---------

- :py:obj:`pydantic_extra_types.isbn.ISBN` (``>= 2.4.0``)

Language types
--------------

- :py:obj:`pydantic_extra_types.language_code.LanguageAlpha2` (``>= 2.7.0``)
- :py:obj:`pydantic_extra_types.language_code.LanguageName` (``>= 2.7.0``)

MAC address type
----------------

- :py:obj:`pydantic_extra_types.mac_address.MacAddress` (``>= 2.1.0``)

Phone number type
-----------------

- :py:obj:`pydantic_extra_types.phone_numbers.PhoneNumber` (``>= 2.1.0``)

Path types
----------

- :py:obj:`pydantic_extra_types.s3.S3Path` (``>= 2.10.0``)

Payment types
-------------

- :py:obj:`pydantic_extra_types.payment.PaymentCardBrand` (``>= 2.1.0``)
- :py:obj:`pydantic_extra_types.payment.PaymentCardNumber` (``>= 2.1.0``)

Routing number type
-------------------

- :py:obj:`pydantic_extra_types.routing_number.ABARoutingNumber` (``>= 2.1.0``)

Semantic version type
---------------------

- :py:obj:`pydantic_extra_types.semantic_version.SemanticVersion` (``>= 2.9.0``)

ULID type
---------

- :py:obj:`pydantic_extra_types.ulid.ULID` (``>= 2.2.0``)
