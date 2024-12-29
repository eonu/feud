Pydantic types
==============

.. contents:: Table of Contents
    :class: this-will-duplicate-information-and-it-is-still-useful-here
    :local:
    :backlinks: none
    :depth: 3

`Pydantic <https://docs.pydantic.dev/latest/>`__ is a validation library that provides 
a rich selection of useful types for command-line inputs.

The following commonly used Pydantic types can be used as type hints for Feud commands.

.. important::

    This page only lists a subset of Pydantic types, i.e. those which would commonly
    be used as command-line inputs. 
    
    All `Pydantic types <https://docs.pydantic.dev/latest/concepts/types/>`__ 
    (including those not listed on this page) are compatible with Feud.

.. tip::

    All of the types listed on this page are easily accessible from the :py:mod:`feud.typing` module.

    It is recommended to import the :py:mod:`feud.typing` module with an alias such as ``t`` for convenient short-hand use, e.g.

    .. code:: python

        from feud import typing as t

        t.PositiveInt  # pydantic.types.PositiveInt
        t.FutureDatetime  # pydantic.types.FutureDatetime
        t.conint  # pydantic.types.conint
        t.IPvAnyAddress  # pydantic.networks.IPvAnyAddress

----

The version number indicates the minimum ``pydantic`` version required to use the type. 

If this version requirement is not met, the type is not imported by Feud.

String types
------------

- :py:obj:`pydantic.types.ImportString` (``>= 2.0.3``)
- :py:obj:`pydantic.types.SecretStr` (``>= 2.0.3``)
- :py:obj:`pydantic.types.StrictStr` (``>= 2.0.3``)
- :py:obj:`pydantic.types.constr` (``>= 2.0.3``)

Integer types
-------------

- :py:obj:`pydantic.types.NegativeInt` (``>= 2.0.3``)
- :py:obj:`pydantic.types.NonNegativeInt` (``>= 2.0.3``)
- :py:obj:`pydantic.types.NonPositiveInt` (``>= 2.0.3``)
- :py:obj:`pydantic.types.PositiveInt` (``>= 2.0.3``)
- :py:obj:`pydantic.types.StrictInt` (``>= 2.0.3``)
- :py:obj:`pydantic.types.conint` (``>= 2.0.3``)

Float types
-----------

- :py:obj:`pydantic.types.FiniteFloat` (``>= 2.0.3``)
- :py:obj:`pydantic.types.NegativeFloat` (``>= 2.0.3``)
- :py:obj:`pydantic.types.NonNegativeFloat` (``>= 2.0.3``)
- :py:obj:`pydantic.types.NonPositiveFloat` (``>= 2.0.3``)
- :py:obj:`pydantic.types.PositiveFloat` (``>= 2.0.3``)
- :py:obj:`pydantic.types.StrictFloat` (``>= 2.0.3``)
- :py:obj:`pydantic.types.confloat` (``>= 2.0.3``)

Sequence types
--------------

- :py:obj:`pydantic.types.confrozenset` (``>= 2.0.3``)
- :py:obj:`pydantic.types.conlist` (``>= 2.0.3``)
- :py:obj:`pydantic.types.conset` (``>= 2.0.3``)

Datetime types
--------------

- :py:obj:`pydantic.types.AwareDatetime` (``>= 2.0.3``)
- :py:obj:`pydantic.types.FutureDate` (``>= 2.0.3``)
- :py:obj:`pydantic.types.FutureDatetime` (``>= 2.0.3``)
- :py:obj:`pydantic.types.NaiveDatetime` (``>= 2.0.3``)
- :py:obj:`pydantic.types.PastDate` (``>= 2.0.3``)
- :py:obj:`pydantic.types.PastDatetime` (``>= 2.0.3``)
- :py:obj:`pydantic.types.condate` (``>= 2.0.3``)

Path types
----------

- :py:obj:`pydantic.types.DirectoryPath` (``>= 2.0.3``)
- :py:obj:`pydantic.types.FilePath` (``>= 2.0.3``)
- :py:obj:`pydantic.types.NewPath` (``>= 2.0.3``)
- :py:obj:`pydantic.types.SocketPath` (``>= 2.10.0``)

Decimal type
------------

- :py:obj:`pydantic.types.condecimal` (``>= 2.0.3``)

URL types
---------

- :py:obj:`pydantic.networks.AnyHttpUrl` (``>= 2.0.3``)
- :py:obj:`pydantic.networks.AnyUrl` (``>= 2.0.3``)
- :py:obj:`pydantic.networks.FileUrl` (``>= 2.0.3``)
- :py:obj:`pydantic.networks.HttpUrl` (``>= 2.0.3``)

Email types
-----------

.. important::

    In order to use email types, you must install Feud with the optional 
    ``email-validator`` dependency (see `here <https://github.com/JoshData/python-email-validator>`__).

    .. code:: console

        $ pip install feud[email]

- :py:obj:`pydantic.networks.EmailStr` (``>= 2.0.3``)
- :py:obj:`pydantic.networks.NameEmail` (``>= 2.0.3``)

Base-64 types
-------------

- :py:obj:`pydantic.types.Base64Bytes` (``>= 2.0.3``)
- :py:obj:`pydantic.types.Base64Str` (``>= 2.0.3``)
- :py:obj:`pydantic.types.Base64UrlBytes` (``>= 2.4.0``)
- :py:obj:`pydantic.types.Base64UrlStr` (``>= 2.4.0``)

Byte types
----------

- :py:obj:`pydantic.types.ByteSize` (``>= 2.0.3``)
- :py:obj:`pydantic.types.SecretBytes` (``>= 2.0.3``)
- :py:obj:`pydantic.types.StrictBytes` (``>= 2.0.3``)
- :py:obj:`pydantic.types.conbytes` (``>= 2.0.3``)

JSON type
---------

- :py:obj:`pydantic.types.Json` (``>= 2.0.3``)
- :py:obj:`pydantic.types.JsonValue` (``>= 2.5.0``)

IP address types
----------------

- :py:obj:`pydantic.networks.IPvAnyAddress` (``>= 2.0.3``)
- :py:obj:`pydantic.networks.IPvAnyInterface` (``>= 2.0.3``)
- :py:obj:`pydantic.networks.IPvAnyNetwork` (``>= 2.0.3``)

Database connection types
-------------------------

- :py:obj:`pydantic.networks.AmqpDsn` (``>= 2.0.3``)
- :py:obj:`pydantic.networks.CockroachDsn` (``>= 2.0.3``)
- :py:obj:`pydantic.networks.KafkaDsn` (``>= 2.0.3``)
- :py:obj:`pydantic.networks.MariaDBDsn` (``>= 2.0.3``)
- :py:obj:`pydantic.networks.MongoDsn` (``>= 2.0.3``)
- :py:obj:`pydantic.networks.MySQLDsn` (``>= 2.0.3``)
- :py:obj:`pydantic.networks.PostgresDsn` (``>= 2.0.3``)
- :py:obj:`pydantic.networks.RedisDsn` (``>= 2.0.3``)

UUID types
----------

- :py:obj:`pydantic.types.UUID1` (``>= 2.0.3``)
- :py:obj:`pydantic.types.UUID3` (``>= 2.0.3``)
- :py:obj:`pydantic.types.UUID4` (``>= 2.0.3``)
- :py:obj:`pydantic.types.UUID5` (``>= 2.0.3``)

Boolean type
------------

- :py:obj:`pydantic.types.StrictBool` (``>= 2.0.3``)

Other types
-----------

- :py:obj:`pydantic.functional_validators.SkipValidation` (``>= 2.0.3``)
