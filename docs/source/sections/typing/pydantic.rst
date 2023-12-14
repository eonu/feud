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

String types
------------

- :py:obj:`pydantic.types.ImportString`
- :py:obj:`pydantic.types.SecretStr`
- :py:obj:`pydantic.types.StrictStr`
- :py:obj:`pydantic.types.constr`

Integer types
-------------

- :py:obj:`pydantic.types.NegativeInt`
- :py:obj:`pydantic.types.NonNegativeInt`
- :py:obj:`pydantic.types.NonPositiveInt`
- :py:obj:`pydantic.types.PositiveInt`
- :py:obj:`pydantic.types.StrictInt`
- :py:obj:`pydantic.types.conint`

Float types
-----------

- :py:obj:`pydantic.types.FiniteFloat`
- :py:obj:`pydantic.types.NegativeFloat`
- :py:obj:`pydantic.types.NonNegativeFloat`
- :py:obj:`pydantic.types.NonPositiveFloat`
- :py:obj:`pydantic.types.PositiveFloat`
- :py:obj:`pydantic.types.StrictFloat`
- :py:obj:`pydantic.types.confloat`

Sequence types
--------------

- :py:obj:`pydantic.types.confrozenset`
- :py:obj:`pydantic.types.conlist`
- :py:obj:`pydantic.types.conset`

Datetime types
--------------

- :py:obj:`pydantic.types.AwareDatetime`
- :py:obj:`pydantic.types.FutureDate`
- :py:obj:`pydantic.types.FutureDatetime`
- :py:obj:`pydantic.types.NaiveDatetime`
- :py:obj:`pydantic.types.PastDate`
- :py:obj:`pydantic.types.PastDatetime`
- :py:obj:`pydantic.types.condate`

Path types
----------

- :py:obj:`pydantic.types.DirectoryPath`
- :py:obj:`pydantic.types.FilePath`
- :py:obj:`pydantic.types.NewPath`

Decimal type
------------

- :py:obj:`pydantic.types.condecimal`

URL types
---------

- :py:obj:`pydantic.networks.AnyHttpUrl`
- :py:obj:`pydantic.networks.AnyUrl`
- :py:obj:`pydantic.networks.FileUrl`
- :py:obj:`pydantic.networks.HttpUrl`

Email types
-----------

.. important::

    In order to use email types, you must install Feud with the optional 
    ``email-validator`` dependency (see `here <https://github.com/JoshData/python-email-validator>`__).

    .. code:: console

        $ pip install feud[email]

- :py:obj:`pydantic.networks.EmailStr`
- :py:obj:`pydantic.networks.NameEmail`

Base-64 types
-------------

- :py:obj:`pydantic.types.Base64Bytes`
- :py:obj:`pydantic.types.Base64Str`

Byte types
----------

- :py:obj:`pydantic.types.ByteSize`
- :py:obj:`pydantic.types.SecretBytes`
- :py:obj:`pydantic.types.StrictBytes`
- :py:obj:`pydantic.types.conbytes`

JSON type
---------

- :py:obj:`pydantic.types.Json`

IP address types
----------------

- :py:obj:`pydantic.networks.IPvAnyAddress`
- :py:obj:`pydantic.networks.IPvAnyInterface`
- :py:obj:`pydantic.networks.IPvAnyNetwork`

Database connection types
-------------------------

- :py:obj:`pydantic.networks.AmqpDsn`
- :py:obj:`pydantic.networks.CockroachDsn`
- :py:obj:`pydantic.networks.KafkaDsn`
- :py:obj:`pydantic.networks.MariaDBDsn`
- :py:obj:`pydantic.networks.MongoDsn`
- :py:obj:`pydantic.networks.MySQLDsn`
- :py:obj:`pydantic.networks.PostgresDsn`
- :py:obj:`pydantic.networks.RedisDsn`

UUID types
----------

- :py:obj:`pydantic.types.UUID1`
- :py:obj:`pydantic.types.UUID3`
- :py:obj:`pydantic.types.UUID4`
- :py:obj:`pydantic.types.UUID5`

Boolean type
------------

- :py:obj:`pydantic.types.StrictBool`

Other types
-----------

- :py:obj:`pydantic.functional_validators.SkipValidation`
