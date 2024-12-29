# Copyright (c) 2023 Feud Developers.
# Distributed under the terms of the MIT License (see the LICENSE file).
# SPDX-License-Identifier: MIT
# This source code is part of the Feud project (https://feud.wiki).

from __future__ import annotations

import collections
import datetime
import decimal
import enum
import fractions
import functools as ft
import inspect
import pathlib
import types
import typing as t
import uuid

import annotated_types as ta
import click
import pydantic as pyd

from feud.config import Config

PATH_TYPES = (
    pathlib.Path,
    pathlib.PosixPath,
    pathlib.PurePath,
    pathlib.PurePosixPath,
    pathlib.PureWindowsPath,
    pathlib.WindowsPath,
)

DATE_TYPES = (
    datetime.date,
    pyd.PastDate,
    pyd.FutureDate,
)

TIME_TYPES = (datetime.time,)

DATETIME_TYPES = (
    datetime.datetime,
    pyd.PastDatetime,
    pyd.FutureDatetime,
    pyd.AwareDatetime,
    pyd.NaiveDatetime,
)

TIMEDELTA_TYPES = (datetime.timedelta,)

BASE_TYPES: dict[type, click.ParamType] = {
    str: click.STRING,
    int: click.INT,
    float: click.FLOAT,
    decimal.Decimal: click.FLOAT,
    fractions.Fraction: click.FLOAT,
    bool: click.BOOL,
    uuid.UUID: click.UUID,
    **{path_type: click.Path() for path_type in PATH_TYPES},
}

EXTRA_TYPES: dict[type, click.ParamType | tuple[click.ParamType, ...]]

try:
    import packaging.version
    import pydantic_extra_types

    version: packaging.version.Version = packaging.version.parse(
        pydantic_extra_types.__version__,
    )

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
        CountryShortName,
    )
    from pydantic_extra_types.mac_address import MacAddress
    from pydantic_extra_types.payment import PaymentCardNumber
    from pydantic_extra_types.phone_numbers import PhoneNumber
    from pydantic_extra_types.routing_number import ABARoutingNumber

    # NOTE: PaymentCardBrand is skipped as it is just an enum
    EXTRA_TYPES = {
        Color: click.STRING,
        Coordinate: (click.FLOAT, click.FLOAT),
        Latitude: click.FLOAT,
        Longitude: click.FLOAT,
        CountryAlpha2: click.STRING,
        CountryAlpha3: click.STRING,
        CountryNumericCode: click.STRING,
        CountryShortName: click.STRING,
        MacAddress: click.STRING,
        PaymentCardNumber: click.STRING,
        PhoneNumber: click.STRING,
        ABARoutingNumber: click.STRING,
    }

    if version >= packaging.version.parse("2.2.0"):
        from pydantic_extra_types.ulid import ULID

        EXTRA_TYPES[ULID] = click.STRING

    if version < packaging.version.parse("2.4.0"):
        from pydantic_extra_types.country import (  # type: ignore[attr-defined]
            CountryOfficialName,
        )

        EXTRA_TYPES[CountryOfficialName] = click.STRING

    if version >= packaging.version.parse("2.4.0"):
        from pydantic_extra_types.isbn import ISBN

        EXTRA_TYPES[ISBN] = click.STRING

    if version >= packaging.version.parse("2.7.0"):
        from pydantic_extra_types.language_code import (
            LanguageAlpha2,
            LanguageName,
        )

        EXTRA_TYPES[LanguageAlpha2] = click.STRING
        EXTRA_TYPES[LanguageName] = click.STRING

    if version >= packaging.version.parse("2.9.0"):
        from pydantic_extra_types.semantic_version import SemanticVersion

        EXTRA_TYPES[SemanticVersion] = click.STRING

    if version >= packaging.version.parse("2.10.0"):
        from pydantic_extra_types.s3 import S3Path

        # NOTE: pathlib.Path isn't ideal for S3 paths
        EXTRA_TYPES[S3Path] = click.STRING

except ImportError:
    EXTRA_TYPES = {}

COLLECTION_TYPES: tuple[type, ...] = (
    tuple,
    list,
    set,
    frozenset,
    collections.deque,
)

DEFAULT_TYPE = None

PathType = t.Union[*PATH_TYPES]  # type: ignore[valid-type]
ClickType = t.Union[  # type: ignore[valid-type]
    *BASE_TYPES.values(),
    type(DEFAULT_TYPE),
]
AnnotatedArgDict = t.Dict[int, t.Any]


class DateTime(click.DateTime):
    def __init__(
        self: t.Self,
        *args: t.Any,
        datetime_type: type,
        show_default_format: bool,
        **kwargs: t.Any,
    ) -> None:
        self._datetime_type = datetime_type
        self._show_default_format = show_default_format
        self.name = datetime_type.__name__
        super().__init__(*args, **kwargs)

    def get_metavar(
        self: t.Self,
        param: click.Parameter,  # noqa: ARG002
    ) -> str:
        return (
            f"[{'|'.join(self.formats)}]"
            if self._show_default_format
            else self.name.upper()
        )

    def _try_to_convert_date(
        self: t.Self,
        value: t.Any,
        format: str,  # noqa: A002, ARG002
    ) -> t.Any | None:
        try:
            return pyd.TypeAdapter(self._datetime_type).validate_python(value)
        except pyd.ValidationError:
            return None


class Union(click.ParamType):
    def __init__(
        self: t.Self,
        *args: t.Any,
        types: list[click.ParamType],
        **kwargs: t.Any,
    ) -> None:
        self.types = types
        super().__init__(*args, **kwargs)

    @staticmethod
    def _get_metavar(
        click_type: click.ParamType | None,
        param: click.Parameter,
    ) -> str | None:
        if click_type:
            return click_type.get_metavar(param) or click_type.name.upper()
        return None

    def get_metavar(self: t.Self, param: click.Parameter) -> str:
        metavars = [
            metavar
            for click_type in self.types
            if (metavar := self._get_metavar(click_type, param))
        ]
        unique_metavars = list(dict.fromkeys(metavars))
        return " | ".join(unique_metavars)


def get_click_type(
    hint: t.Any,
    *,
    config: Config,
) -> ClickType | None:  # type: ignore[valid-type]
    base_type, base_args, _, _ = get_base_type(hint)
    origin_type = t.get_origin(base_type)

    click_type = resolve_collection(origin_type, args=base_args, config=config)
    if click_type and origin_type in COLLECTION_TYPES:
        return click_type

    click_type = resolve_collection(base_type, args={}, config=config)
    if click_type and is_namedtuple(base_type):
        return click_type

    return resolve_type(hint, config=config)


def resolve_type(
    hint: t.Any,
    *,
    config: Config,
) -> ClickType:  # type: ignore[valid-type]
    base_type, base_args, parent_type, parent_args = get_base_type(hint)
    if t.get_origin(parent_type) is t.Annotated:
        click_type = resolve_annotated(base_type, parent_args=parent_args)
        if click_type:
            return click_type
    if t.get_origin(base_type) is t.Literal:
        return click.Choice(list(map(str, base_args.values())))
    if t.get_origin(base_type) in (t.Union, types.UnionType):
        # only try to determine type for
        # t.Optional[t.Any] / t.Union[t.Any, None]
        arg_values = base_args.values()
        if len(base_args) == 2 and type(None) in arg_values:
            non_none = next(arg for arg in arg_values if arg is not type(None))
            return get_click_type(non_none, config=config)
        # t.Union with more than one non-None argument
        base_types = list(
            map(
                ft.partial(get_click_type, config=config),
                base_args.values(),
            )
        )
        return Union(types=base_types)  # type: ignore[arg-type]
    if inspect.isclass(base_type):
        if issubclass(base_type, enum.Enum):
            return click.Choice([str(e.value) for e in base_type])
        if base_type in DATE_TYPES:
            return DateTime(
                formats=["YYYY-MM-DD"],
                datetime_type=datetime.date,
                show_default_format=config.show_help_datetime_formats,
            )
        if base_type in TIME_TYPES:
            return DateTime(
                formats=["HH:MM[:SS[.ffffff]][Z or [±]HH[:]MM]"],
                datetime_type=datetime.time,
                show_default_format=config.show_help_datetime_formats,
            )
        if base_type in DATETIME_TYPES:
            return DateTime(
                formats=["YYYY-MM-DD[T]HH:MM[:SS[.ffffff]][Z or [±]HH[:]MM]"],
                datetime_type=datetime.datetime,
                show_default_format=config.show_help_datetime_formats,
            )
        if base_type in TIMEDELTA_TYPES:
            return DateTime(
                formats=[
                    "[-][DD ][HH:MM]SS[.ffffff]",
                    "[±]P[DD]DT[HH]H[MM]M[SS]S",
                ],
                datetime_type=datetime.timedelta,
                show_default_format=config.show_help_datetime_formats,
            )
        if base_type in EXTRA_TYPES:
            return EXTRA_TYPES[base_type]
    return BASE_TYPES.get(base_type, DEFAULT_TYPE)


def get_arg_dict(hint: t.Annotated[t.Any, ...]) -> AnnotatedArgDict:
    """Convert the arguments of an annotated type into a dictionary.

    Dictionary is keyed by argument index.
    """
    return dict(enumerate(t.get_args(hint)))


def get_base_type(
    hint: t.Any,
    *,
    parent_args: AnnotatedArgDict | None = None,
    parent_type: t.Any | None = None,
) -> tuple[t.Any, AnnotatedArgDict, t.Any | None, AnnotatedArgDict | None]:
    """Retrieve the inner type and arguments of a type.

    Can be annotated or non-annotated. Also returns outer type and arguments.

    Examples
    --------
    >>> import typing as t
    >>> get_base_type(t.Annotated[t.Tuple[int, ...], "annotation"])
    (
        typing.Tuple[int, ...],
        {0: <class 'int'>, 1: Ellipsis},
        typing.Annotated[typing.Tuple[int, ...], 'annotation'],
        {0: typing.Tuple[int, ...], 1: 'annotation'}
    )
    """
    args = get_arg_dict(hint)
    if t.get_origin(hint) is t.Annotated:
        return get_base_type(args[0], parent_type=hint, parent_args=args)
    return hint, args, parent_type, parent_args


def is_collection_type(hint: t.Any) -> tuple[bool, t.Any | None]:
    """Check for collection types and returns their base type.

    Below is a list of valid collection types.
    Note that fixed size tuples (and typing.NamedTuple) are
    excluded as they have a special meaning in Click.

    - ``tuple``
    - ``typing.Tuple``
    - ``typing.Tuple[typing.Any, ...]``
    - ``list``
    - ``typing.List``
    - ``typing.List[typing.Any]``
    - ``set``
    - ``typing.Set``
    - ``typing.Set[typing.Any]``
    - ``frozenset``
    - ``typing.FrozenSet``
    - ``typing.FrozenSet[t.Any]``
    - ``collections.deque``
    - ``typing.Deque``
    - ``typing.Deque[t.Any]``

    Parameters
    ----------
    hint:
        Any type.

    Examples
    --------
    >>> import feud.typing as t
    >>> from feud._internal import _types
    >>> _types.click.is_collection_type(list)
    (True, None)
    >>> _types.click.is_collection_type(t.Tuple[int, ...])
    (True, int)
    >>> _types.click.is_collection_type(t.Tuple[int, str])
    (False, None)
    >>> _types.click.is_collection_type(str)
    (False, None)
    """
    base_type, base_args, _, _ = get_base_type(hint)

    if base_type in COLLECTION_TYPES:
        return True, None

    origin = t.get_origin(base_type)
    if origin in COLLECTION_TYPES:
        if origin is tuple:
            if len(base_args) == 0:
                # typing.Tuple
                return True, None
            if len(base_args) == 2 and base_args.get(1) is Ellipsis:
                # typing.Tuple[typing.Any, ...]
                return True, base_args.get(0)
            return False, None
        return True, base_args.get(0)

    return False, None


def resolve_collection(
    hint: t.Any,
    *,
    args: AnnotatedArgDict,
    config: Config,
) -> ClickType | None:  # type: ignore[valid-type]
    """Resolve a Click type for the provided collection type.

    See `is_collection_type` for more information about collection types.

    Examples
    --------
    >>> import feud.typing as t
    >>> from feud.config import Config
    >>> from feud._internal import _types
    >>> _types.click.resolve_collection(
    ...     tuple,
    ...     args={0: t.conint(ge=0, le=3), 1: ...},
    ...     config=Config._create()
    ... )
    click.IntRange(min=0, max=3, min_open=False, max_open=False)
    """
    if hint is tuple and len(args):
        # arbitrary size tuple - t.Tuple[t.Any, ...]
        if args.get(1) is Ellipsis:
            return resolve_type(args[0], config=config)
        # fixed size tuple, e.g. t.Tuple[t.Any, t.Any]
        return tuple(
            map(ft.partial(resolve_type, config=config), args.values())
        )
    if is_namedtuple(hint):
        return tuple(
            map(
                ft.partial(resolve_type, config=config),
                hint.__annotations__.values(),
            )
        )
    if hint in (list, set, frozenset, collections.deque):
        # Type[t.Any]
        return resolve_type(args.get(0), config=config)
    return None


def resolve_annotated(
    base_type: t.Any,
    *,
    parent_args: AnnotatedArgDict | None,
) -> ClickType | None:  # type: ignore[valid-type]
    if parent_args is None:
        return None

    arg_list = list(parent_args.values())  # noqa: F841
    two_field_subtype = t.Annotated[*arg_list[:2]]  # type: ignore[valid-type]

    # integer types
    if two_field_subtype == pyd.PositiveInt:
        return click.IntRange(min=0, min_open=True)
    if two_field_subtype == pyd.NonNegativeInt:
        return click.IntRange(min=0, min_open=False)
    if two_field_subtype == pyd.NegativeInt:
        return click.IntRange(max=0, max_open=True)
    if two_field_subtype == pyd.NonPositiveInt:
        return click.IntRange(max=0, max_open=False)

    # float types
    if two_field_subtype == pyd.PositiveFloat:
        return click.FloatRange(min=0, min_open=True)
    if two_field_subtype == pyd.NonNegativeFloat:
        return click.FloatRange(min=0, min_open=False)
    if two_field_subtype == pyd.NegativeFloat:
        return click.FloatRange(max=0, max_open=True)
    if two_field_subtype == pyd.NonPositiveFloat:
        return click.FloatRange(max=0, max_open=False)

    # int / float range types
    if is_pyd_conint(base_type, parent_args):
        return get_click_range_type(parent_args, range_type=click.IntRange)
    if is_pyd_confloat(base_type, parent_args):
        return get_click_range_type(parent_args, range_type=click.FloatRange)
    if is_pyd_condecimal(base_type, parent_args):
        return get_click_range_type(parent_args, range_type=click.FloatRange)

    # file / directory types
    if two_field_subtype == pyd.FilePath:
        return click.Path(exists=True, dir_okay=False)
    if two_field_subtype == pyd.DirectoryPath:
        return click.Path(exists=True, file_okay=False)
    if base_type in PATH_TYPES:
        return click.Path()

    return None


def is_pyd_conint(base_type: t.Any, parent_args: AnnotatedArgDict) -> bool:
    return base_type is int and isinstance(parent_args.get(2), ta.Interval)


def is_pyd_confloat(base_type: t.Any, parent_args: AnnotatedArgDict) -> bool:
    return base_type is float and isinstance(parent_args.get(2), ta.Interval)


def is_pyd_condecimal(base_type: t.Any, parent_args: AnnotatedArgDict) -> bool:
    return base_type is decimal.Decimal and isinstance(
        parent_args.get(2), ta.Interval
    )


def is_namedtuple(hint: t.Any) -> bool:
    if hint is None:
        return False
    if not inspect.isclass(hint):
        return False
    return issubclass(hint, tuple) and hasattr(hint, "_fields")


def get_click_range_type(
    args: AnnotatedArgDict,
    *,
    range_type: type[click.IntRange] | type[click.FloatRange],
) -> click.IntRange | click.FloatRange | None:
    min_: ta.SupportsGe | ta.SupportsGt | None = None
    max_: ta.SupportsLe | ta.SupportsLt | None = None

    min_open, max_open = False, False

    interval: ta.Interval | None = args.get(2)
    if interval is None:
        return None
    if interval.gt is not None:
        min_ = interval.gt
        min_open = True
    if interval.ge is not None:
        min_ = interval.ge
        min_open = False
    if interval.lt is not None:
        max_ = interval.lt
        max_open = True
    if interval.le is not None:
        max_ = interval.le
        max_open = False

    return range_type(
        min=min_,  # type: ignore[arg-type]
        max=max_,  # type: ignore[arg-type]
        min_open=min_open,
        max_open=max_open,
    )
