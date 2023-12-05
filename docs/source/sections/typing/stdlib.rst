Standard library types
======================

The following Python standard library types can be used as type hints for Feud commands.

.. tip::

    Types listed on this page from the :py:mod:`collections`, :py:mod:`datetime` :py:mod:`decimal`, 
    :py:mod:`enum`, :py:mod:`pathlib` and :py:mod:`uuid` standard library modules are easily accessible
    from the :py:mod:`feud.typing` module.

    It is recommended to import the :py:mod:`feud.typing` module with an alias such as ``t`` for convenient short-hand use, e.g.

    .. code:: python

        from feud import typing as t

        t.Path  # pathlib.Path
        t.datetime  # datetime.datetime
        t.IntEnum  # enum.IntEnum
        t.NamedTuple  # typing.NamedTuple
        t.Union  # typing.Union

.. contents:: Table of Contents
    :class: this-will-duplicate-information-and-it-is-still-useful-here
    :local:
    :backlinks: none
    :depth: 3

----

String type
-----------

The string type permits the user to enter free text as an input value.

:py:obj:`str` should be used to specify free text, 
but it is also the default when no type hint is provided.

.. seealso:: 

    :py:obj:`pydantic.types.constr` can be used to impose restrictions such as minimum/maximum string length.

.. dropdown:: Example
    :animate: fade-in

    - **Arguments**:
        - ``ARG1``: Any text (no type hint).
        - ``ARG2``: Any text.
    - **Options**:
        - ``--opt``: Any text.

    .. tab-set::

        .. tab-item:: Code

            .. code:: python

                # str.py

                import feud

                def command(arg1, arg2: str, *, opt: str = "value"):
                    print(f"{arg1=!r} ({type(arg1)})")
                    print(f"{arg2=!r} ({type(arg2)})")
                    print(f"{opt=!r} ({type(opt)})")

                if __name__ == "__main__":
                    feud.run(command)

        .. tab-item:: Help screen

            .. code:: console

                $ python str.py --help

            .. image:: /_static/images/examples/typing/str/help.png
                :alt: Free text example help screen

        .. tab-item:: Usage

            .. card:: Valid input

                .. code:: console

                    $ python str.py "Hello World!" abc --opt test

                .. code::
                    
                    arg1='Hello World' (<class 'str'>)
                    arg2='abc' (<class 'str'>)
                    opt='test' (<class 'str'>)

            .. card:: Invalid input

                As free text is not validated, any input is accepted.

Literal string type (choices)
-----------------------------

Literal strings can be used to limit the user to a number of string choices.

:py:obj:`typing.Literal` should be used to specify literal string inputs.

.. seealso:: 

    `Enumeration types <#enumeration-types-choices>`__ can also be used to represent choices.

.. dropdown:: Example
    :animate: fade-in

    - **Arguments**:
        - ``ARG``: Either the string ``a`` or ``b``.
    - **Options**:
        - ``--opt``: Either the string ``c``, ``d`` or ``e``. Defaults to ``e``.

    .. tab-set::

        .. tab-item:: Code

            .. code:: python

                # literal.py

                import feud
                from feud import typing as t

                def command(arg: t.Literal["a", "b"], *, opt: t.Literal["c", "d", "e"] = "e"):
                    print(f"{arg=!r} ({type(arg)})")
                    print(f"{opt=!r} ({type(opt)})")

                if __name__ == "__main__":
                    feud.run(command)

        .. tab-item:: Help screen

            .. code:: console

                $ python literal.py --help

            .. image:: /_static/images/examples/typing/literal/help.png
                :alt: Literal example help screen

        .. tab-item:: Usage

            .. card:: Valid input

                .. code:: console

                    $ python literal.py b --opt d

                .. code::
                    
                    arg='b' (<class 'str'>)
                    opt='d' (<class 'str'>)

            .. card:: Invalid input

                .. code:: console

                    $ python literal.py c

                .. image:: /_static/images/examples/typing/literal/error.png
                    :alt: Literal example error

Boolean type
------------

The boolean type can be used to indicate a true/false input.

:py:obj:`bool` should be used to specify boolean inputs.

Common truth values that are accepted include any of the following (*case insensitive*):

- **True**: ``true``, ``t``, ``yes``, ``y``, ``1``
- **False**: ``false``, ``f``, ``no``, ``n``, ``0``

.. tip::

    When used as an option, the presence of a boolean flag is enough to set 
    the value to ``True`` --- that is, to enable the flag the user should simply 
    specify ``--opt`` instead of ``--opt true`` (which will **not** work), for 
    example.

    By default, a negated version of the flag (e.g. ``--no-opt``) is also generated
    to set the value to ``False``. The generation of this negated flag can be 
    disabled by changing the :ref:`Feud configuration parameters <configuration>`.

.. dropdown:: Example
    :animate: fade-in

    - **Arguments**:
        - ``ARG``: Boolean value.
    - **Options**:
        - ``--opt``: Boolean value.

    .. tab-set::

        .. tab-item:: Code

            .. code:: python

                # bool.py

                import feud

                def command(arg: bool, *, opt: bool = True):
                    print(f"{arg=!r} ({type(arg)})")
                    print(f"{opt=!r} ({type(opt)})")

                if __name__ == "__main__":
                    feud.run(command)

        .. tab-item:: Help screen

            .. code:: console

                $ python bool.py --help

            .. image:: /_static/images/examples/typing/bool/help.png
                :alt: Boolean example help screen

        .. tab-item:: Usage

            .. card:: Valid input (1)

                .. code:: bash

                    $ python bool.py false --opt

                .. code::
                    
                    arg=False (<class 'bool'>)
                    opt=True (<class 'bool'>)

            .. card:: Valid input (2)

                .. code:: console

                    $ python bool.py true --no-opt

                .. code::
                    
                    arg=True (<class 'bool'>)
                    opt=False (<class 'bool'>)

            .. card:: Invalid input

                .. code:: bash

                    $ python bool.py maybe

                .. image:: /_static/images/examples/typing/bool/error.png
                    :alt: Boolean example error

Number types
------------

Number types can be used to indicate integers, floats or decimal numbers.

- :py:obj:`int` should be used to specify integer inputs.
- :py:obj:`float` should be used to specify fixed precision-floating point inputs.
- :py:obj:`decimal.Decimal` should be used to specify arbitrary-precision floating point inputs.

.. seealso:: 

    - :py:obj:`pydantic.types.conint` can be used to restrict integers.
    - :py:obj:`pydantic.types.confloat` can be used to restrict floats.
    - :py:obj:`pydantic.types.condecimal` can be used to restrict decimals.

.. dropdown:: Example
    :animate: fade-in

    - **Arguments**:
        - ``ARG``: An integer value.
    - **Options**:
        - ``--opt1``: An integer value.
        - ``--opt2``: A fixed-precision floating point number.
        - ``--opt3``: An arbirary precision floating point number.

    .. tab-set::

        .. tab-item:: Code

            .. code:: python

                # number.py

                import feud
                from feud import typing as t

                def command(arg: int, *, opt1: int, opt2: float, opt3: t.Decimal):
                    print(f"{arg=!r} ({type(arg)})")
                    print(f"{opt1=!r} ({type(opt1)})")
                    print(f"{opt2=!r} ({type(opt2)})")
                    print(f"{opt3=!r} ({type(opt3)})")

                if __name__ == "__main__":
                    feud.run(command)

        .. tab-item:: Help screen

            .. code:: console

                $ python number.py --help

            .. image:: /_static/images/examples/typing/number/help.png
                :alt: Number example help screen

        .. tab-item:: Usage

            .. card:: Valid input

                .. code:: console

                    $ python number.py 0 --opt1 1 --opt2 -2.2 --opt3 3.33

                .. code::
                    
                    arg=0 (<class 'int'>)
                    opt1=1 (<class 'int'>)
                    opt2=-2.2 (<class 'float'>)
                    opt3=Decimal('3.33') (<class 'decimal.Decimal'>)

            .. card:: Invalid input

                .. code:: console

                    $ python number.py abc --opt1 1.1 --opt2 true --opt3 invalid

                .. image:: /_static/images/examples/typing/number/error.png
                    :alt: Number example error

Datetime types
--------------

Datetime types can be used to indicate date or time related inputs.

- :py:obj:`datetime.datetime` can be used to indicate inputs with a date and time component.
- :py:obj:`datetime.date` can be used to indicate date inputs.
- :py:obj:`datetime.time` can be used to indicate time inputs.
- :py:obj:`datetime.timedelta` can be used to indicate time delta inputs.

.. seealso:: 

    - :py:obj:`pydantic.types.condate` can be used to impose restrictions such as minimum/maximum dates.
    - :py:obj:`pydantic.types.PastDate`/:py:obj:`pydantic.types.PastDatetime` can be used to restrict date/datetime inputs to the past.
    - :py:obj:`pydantic.types.FutureDate`/:py:obj:`pydantic.types.FutureDatetime` can be used to restrict date/datetime inputs to the future.

.. dropdown:: Example
    :animate: fade-in

    - **Arguments**:
        - ``ARG``: A datetime value.
    - **Options**:
        - ``--opt1``: A date value.
        - ``--opt2``: A time value.
        - ``--opt3``: A time delta value.

    .. tab-set::

        .. tab-item:: Code

            .. code:: python

                # date_time.py

                import feud
                from feud import typing as t

                def command(arg: t.datetime, *, opt1: t.date, opt2: t.time, opt3: t.timedelta):
                    print(f"{arg=!r} ({type(arg)})")
                    print(f"{opt1=!r} ({type(opt1)})")
                    print(f"{opt2=!r} ({type(opt2)})")
                    print(f"{opt3=!r} ({type(opt3)})")

                if __name__ == "__main__":
                    feud.run(command)

        .. tab-item:: Help screen

            .. code:: console

                $ python date_time.py --help

            .. image:: /_static/images/examples/typing/datetime/help.png
                :alt: Datetime example help screen

        .. tab-item:: Usage

            .. card:: Valid input

                .. code:: console

                    $ python date_time.py "2012-12-21 00:01:00" \
                        --opt1 2012-12-21 \
                        --opt2 00:01:00 \
                        --opt3 "704 days, 19:21:44.938965"

                .. code::
                    
                    arg=datetime.datetime(2012, 12, 21, 0, 1) (<class 'datetime.datetime'>)
                    opt1=datetime.date(2012, 12, 21) (<class 'datetime.date'>)
                    opt2=datetime.time(0, 1) (<class 'datetime.time'>)
                    opt3=datetime.timedelta(days=704, seconds=69704, microseconds=938965) (<class 'datetime.timedelta'>)

            .. card:: Invalid input

                .. code:: console

                    $ python date_time.py abc --opt1 a --opt2 b --opt3 c

                .. image:: /_static/images/examples/typing/datetime/error.png
                    :alt: Datetime example error

Path type
---------

The path type can be used to indicate a file or directory path input.

:py:obj:`pathlib.Path` should be used to specify path inputs.

.. important::

    :py:obj:`pathlib.Path` does **not** validate whether or not the path already exists.

.. seealso::

    - :py:obj:`pydantic.types.NewPath` can be used to indicate a path that must **not** already exist.
    - :py:obj:`pydantic.types.FilePath` can be used to indicate a path to a file that **must** already exist.
    - :py:obj:`pydantic.types.DirectoryPath` can be used to indicate a path to a directory that **must** already exist.

.. dropdown:: Example
    :animate: fade-in

    - **Arguments**:
        - ``ARG``: Path to a file or directory (may not exist).
    - **Options**:
        - ``--opt``: Path to a file or directory (may not exist). Defaults to ``/usr/local/bin``.

    .. tab-set::

        .. tab-item:: Code

            .. code:: python

                # path.py

                import feud
                from feud import typing as t

                def command(arg: t.Path, *, opt: t.Path = t.Path("/usr/local/bin")):
                    print(f"{arg=!r} ({type(arg)})")
                    print(f"{opt=!r} ({type(opt)})")

                if __name__ == "__main__":
                    feud.run(command)

        .. tab-item:: Help screen

            .. code:: console

                $ python literal.py --help

            .. image:: /_static/images/examples/typing/path/help.png
                :alt: Path example help screen

        .. tab-item:: Usage

            .. card:: Valid input

                .. code:: console

                    $ python path.py /opt/homebrew --opt ~/dev/feud/README.md

                .. code::
                    
                    arg=PosixPath('/opt/homebrew') (<class 'pathlib.PosixPath'>)
                    opt=PosixPath('/Users/eonu/dev/feud/README.md') (<class 'pathlib.PosixPath'>)

            .. card:: Invalid input

                As :py:obj:`python:pathlib.Path` allows any string, any input is accepted.

Sequence types
--------------

Variable length
^^^^^^^^^^^^^^^

Variable length sequence types can be used to accept multiple input values.

- :py:obj:`list`/:py:obj:`typing.List` should be used to specify a list of inputs.
- :py:obj:`set`/:py:obj:`typing.Set` should be used to specify a set of inputs.
- :py:obj:`frozenset`/:py:obj:`typing.FrozenSet` should be used to specify a frozen set of inputs.
- :py:obj:`collections.deque`/:py:obj:`typing.Deque` should be used to specify a deque of inputs.

.. tip::

    Additional type restrictions can be placed on the items within the sequence, e.g.:

    - :py:obj:`list`\ [:py:obj:`float`] indicates a list of float inputs.
    - :py:obj:`set`\ [:py:obj:`int`] indicates a set of integer inputs.

.. seealso::

    - :py:obj:`pydantic.types.conlist` can be used to impose restrictions such as minimum/maximum list length.
    - :py:obj:`pydantic.types.conset` can be used to impose restrictions such as minimum/maximum set length.
    - :py:obj:`pydantic.types.confrozenset` can be used to impose restrictions such as minimum/maximum frozen set length.

.. dropdown:: Example
    :animate: fade-in

    - **Arguments**:
        - ``FLOATS``: Any number of float values (at least one).
    - **Options**:
        - ``--ints``: Any number of integer values (at least one).

    .. tab-set::

        .. tab-item:: Code

            .. code:: python

                # variable.py

                import feud

                def command(floats: list[float], *, ints: set[int]):
                    print(f"{floats=!r} ({type(floats)})")
                    print(f"{ints=!r} ({type(ints)})")

                if __name__ == "__main__":
                    feud.run(command)

        .. tab-item:: Help screen

            .. code:: console

                $ python variable.py --help

            .. image:: /_static/images/examples/typing/sequence_variable/help.png
                :alt: Variable length sequence example help screen

        .. tab-item:: Usage

            .. card:: Valid input

                .. code:: console

                    $ python variable.py 1.1 2.2 3.3 --ints 0 --ints 1 --ints 0 --ints 2

                .. code::
                    
                    floats=[1.1, 2.2, 3.3] (<class 'list'>)
                    ints={0, 1, 2} (<class 'set'>)

            .. card:: Invalid input

                .. code:: console

                    $ python variable.py string

                .. image:: /_static/images/examples/typing/sequence_variable/error.png
                    :alt: Variable length sequence example error

Fixed length
^^^^^^^^^^^^

Fixed length sequence types can be used to accept a fixed number of input values.

- :py:obj:`tuple`/:py:obj:`typing.Tuple` should be used to specify a tuple of inputs.
- :py:obj:`typing.NamedTuple` should be used to specify a named tuple of inputs.

.. tip::

    When used with ``...`` as the second type argument, :py:obj:`tuple`/:py:obj:`typing.Tuple` 
    may also be used to accept a `variable length input <#variable-length>`__ and convert the items into a tuple, 
    e.g. :py:obj:`tuple`\ [:py:obj:`int`, ``...``] accepts a variable number of integers.

.. dropdown:: Example
    :animate: fade-in

    - **Arguments**:
        - ``NUMBERS``: Pair of numbers consisting of an integer and float.
    - **Options**:
        - ``--location``: Pair of numbers consisting of a latitude & longitude (both floats).

    .. tab-set::

        .. tab-item:: Code

            .. code:: python

                # fixed.py

                import feud
                from feud import typing as t

                class Coordinate(t.NamedTuple):
                    latitude: t.Latitude
                    longitude: t.Longitude

                def command(numbers: tuple[int, float], *, location: Coordinate):
                    print(f"{numbers=!r} ({type(numbers)})")
                    print(f"{location=!r} ({type(location)})")

                if __name__ == "__main__":
                    feud.run(command)

        .. tab-item:: Help screen

            .. code:: console

                $ python fixed.py --help

            .. image:: /_static/images/examples/typing/sequence_fixed/help.png
                :alt: Fixed length sequence example help screen

        .. tab-item:: Usage

            .. card:: Valid input

                .. code:: console

                    $ python fixed.py 1 1.1 --location 65.2 149.0

                .. code::
                    
                    numbers=(1, 1.1) (<class 'tuple'>)
                    location=Coordinate(latitude=65.2, longitude=149.0) (<class '__main__.Coordinate'>)

            .. card:: Invalid input

                .. code:: console

                    $ python fixed.py 1 1.1 --location 100 200

                .. image:: /_static/images/examples/typing/sequence_fixed/error.png
                    :alt: Fixed length sequence example error

Enumeration types (choices)
---------------------------

Enumerate types can be used to limit the user to a number of choices.

- :py:obj:`enum.Enum`/:py:obj:`enum.StrEnum` should be used to limit the user to string choices.
- :py:obj:`enum.IntEnum` should be used to limit the user to integer choices.

.. important::

    :py:obj:`enum.Enum` values may only be strings.

.. dropdown:: Example
    :animate: fade-in

    - **Arguments**:
        - ``ARG``: Either the number ``1`` or ``2``.
    - **Options**:
        - ``--opt``: Either the string ``a`` or ``b``. Defaults to ``a``.

    .. tab-set::

        .. tab-item:: Code

            .. code:: python

                import feud
                from feud import typing as t

                class Mode(t.Enum):
                    A = "a"
                    B = "b"

                class Version(t.IntEnum):
                    ONE = 1
                    TWO = 2

                def command(arg: Version, *, opt: Mode = Mode.A):
                    print(f"{arg=!r} ({type(arg)})")
                    print(f"{opt=!r} ({type(opt)})")

                if __name__ == "__main__":
                    feud.run(command)

        .. tab-item:: Help screen

            .. code:: console

                $ python literal.py --help

            .. image:: /_static/images/examples/typing/enumeration/help.png
                :alt: Enumeration example help screen

        .. tab-item:: Usage

            .. card:: Valid input

                .. code:: console

                    $ python enumeration.py 1 --opt b

                .. code::
                    
                    arg=<Version.ONE: 1> (<enum 'Version'>)
                    opt=<Mode.B: 'b'> (<enum 'Mode'>)

            .. card:: Invalid input

                .. code:: console

                    $ python enumeration.py 3 --opt c

                .. image:: /_static/images/examples/typing/enumeration/error.png
                    :alt: Enumeration example error

UUID type
---------

The UUID type can be used to indicate a UUID input.

:py:obj:`uuid.UUID` should be used to specify UUID inputs.

.. dropdown:: Example
    :animate: fade-in

    - **Arguments**:
        - ``ARG``: A UUID value.
    - **Options**:
        - ``--opt``: A UUID value. Defaults to a random UUID if none is provided.

    .. tab-set::

        .. tab-item:: Code

            .. code:: python

                # uuids.py

                from uuid import uuid4

                import feud
                from feud import typing as t

                def command(arg: t.UUID, *, opt: t.UUID = uuid4()):
                    print(f"{arg=!r} ({type(arg)})")
                    print(f"{opt=!r} ({type(opt)})")

                if __name__ == "__main__":
                    feud.run(command)

        .. tab-item:: Help screen

            .. code:: console

                $ python uuids.py --help

            .. image:: /_static/images/examples/typing/uuids/help.png
                :alt: UUID example help screen

        .. tab-item:: Usage

            .. card:: Valid input

                .. code:: console

                    $ python uuids.py 2b293576-fe8c-4482-898c-547adf5a4a25

                .. code::
                    
                    arg=UUID('2b293576-fe8c-4482-898c-547adf5a4a25') (<class 'uuid.UUID'>)
                    opt=UUID('8186f015-8ca6-4793-9513-121288f972fd') (<class 'uuid.UUID'>)

            .. card:: Invalid input

                .. code:: console

                    $ python uuids.py 123

                .. image:: /_static/images/examples/typing/uuids/error.png
                    :alt: UUID example error

Unions
------

Unions can be used to allow for an input to match two or more supported Feud types.

:py:obj:`typing.Union` or the ``|`` operator can be used to specify union types.

.. dropdown:: Example
    :animate: fade-in

    - **Arguments**:
        - ``ARG``: A UUID value.
    - **Options**:
        - ``--opt``: A UUID value. Defaults to a random UUID if none is provided.

    .. tab-set::

        .. tab-item:: Code

            .. code:: python

                # union.py

                import feud
                from feud import typing as t

                def command(arg: t.Union[int, float], *, opt: int | float):
                    print(f"{arg=!r} ({type(arg)})")
                    print(f"{opt=!r} ({type(opt)})")

                if __name__ == "__main__":
                    feud.run(command)

        .. tab-item:: Help screen

            .. code:: console

                $ python union.py --help

            .. image:: /_static/images/examples/typing/union/help.png
                :alt: Union example help screen

        .. tab-item:: Usage

            .. card:: Valid input

                .. code:: console

                    $ python union.py 1 --opt 1.1

                .. code::
                    
                    arg=1 (<class 'int'>)
                    opt=1.1 (<class 'float'>)

            .. card:: Invalid input

                .. code:: console

                    $ python union.py a --opt b

                .. image:: /_static/images/examples/typing/union/error.png
                    :alt: Union example error
