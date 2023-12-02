# Copyright (c) 2023-2025 Feud Developers.
# Distributed under the terms of the MIT License (see the LICENSE file).
# SPDX-License-Identifier: MIT
# This source code is part of the Feud project (https://feud.wiki).

from __future__ import annotations

import collections
import datetime
import decimal
import enum
import functools as ft
import inspect
import pathlib
import types
import typing as t
import uuid

import click
import pydantic as pyd
from annotated_types import Interval

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

BASE_TYPES = {
    str: click.STRING,
    int: click.INT,
    float: click.FLOAT,
    decimal.Decimal: click.FLOAT,
    bool: click.BOOL,
    uuid.UUID: click.UUID,
    **{path_type: click.Path() for path_type in PATH_TYPES},
}

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
        PaymentCardNumber,
    )
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
        CountryOfficialName: click.STRING,
        CountryShortName: click.STRING,
        MacAddress: click.STRING,
        PaymentCardNumber: click.STRING,
        PhoneNumber: click.STRING,
        ABARoutingNumber: click.STRING,
    }
except ImportError:
    EXTRA_TYPES = {}

COLLECTION_TYPES = (
    tuple,
    list,
    set,
    frozenset,
    collections.deque,
)

DEFAULT_TYPE = None

PathType = t.Union[*PATH_TYPES]
ClickType = t.Union[*BASE_TYPES.values(), type(DEFAULT_TYPE)]
AnnotatedArgDict = t.Dict[int, t.Any]


class DateTime(click.DateTime):
    def __init__(
        self: DateTime,
        *args: t.Any,
        datetime_type: type,
        show_default_format: bool,
        **kwargs: t.Any,
    ) -> DateTime:
        self._datetime_type = datetime_type
        self._show_default_format = show_default_format
        self.name = datetime_type.__name__
        super().__init__(*args, **kwargs)

    def get_metavar(
        self: DateTime,
        param: click.Parameter,  # noqa: ARG002
    ) -> str:
        return (
            f"[{'|'.join(self.formats)}]"
            if self._show_default_format
            else self.name.upper()
        )

    def _try_to_convert_date(
        self: DateTime,
        value: t.Any,
        format: str,  # noqa: A002, ARG002
    ) -> t.Any | None:
        try:
            return pyd.TypeAdapter(self._datetime_type).validate_python(value)
        except pyd.ValidationError:
            return None


def get_click_type(hint: t.Any, *, config: Config) -> ClickType | None:
    base_type, base_args, _, _ = get_base_type(hint)
    origin_type = t.get_origin(base_type)

    click_type = resolve_collection(origin_type, args=base_args, config=config)
    if click_type and origin_type in COLLECTION_TYPES:
        return click_type

    click_type = resolve_collection(base_type, args={}, config=config)
    if click_type and is_namedtuple(base_type):
        return click_type

    return resolve_type(hint, config=config)


def resolve_type(hint: t.Any, *, config: Config) -> ClickType:
    base_type, base_args, parent_type, parent_args = get_base_type(hint)
    if t.get_origin(parent_type) is t.Annotated:
        click_type = resolve_annotated(base_type, parent_args=parent_args)
        if click_type:
            return click_type
    if t.get_origin(base_type) is t.Literal:
        return click.Choice(list(map(str, base_args.values())))
    if t.get_origin(base_type) in (t.Union, types.UnionType):
        # only try to determine type for
        # t.Optional[t.Any] / t.Union[t.Any, None]  # noqa: ERA001
        arg_values = base_args.values()
        if len(base_args) == 2 and type(None) in arg_values:
            non_none = next(arg for arg in arg_values if arg is not type(None))
            return get_click_type(non_none, config=config)
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
) -> tuple[t.Any, AnnotatedArgDict, t.Any, AnnotatedArgDict]:
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
                # typing.Tuple[typing.Any, ...]  # noqa: ERA001
                return True, base_args.get(0)
            return False, None
        return True, base_args.get(0)

    return False, None


def resolve_collection(
    hint: t.Any, *, args: AnnotatedArgDict, config: Config
) -> ClickType | None:
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
        # Type[t.Any]  # noqa: ERA001
        return resolve_type(args.get(0), config=config)
    return None


def resolve_annotated(
    base_type: t.Any, *, parent_args: AnnotatedArgDict
) -> ClickType | None:
    arg_list = list(parent_args.values())  # noqa: F841
    two_field_subtype = t.Annotated[*arg_list[:2]]
    # integer types
    if two_field_subtype is pyd.PositiveInt:
        return click.IntRange(min=0, min_open=True)
    if two_field_subtype is pyd.NonNegativeInt:
        return click.IntRange(min=0, min_open=False)
    if two_field_subtype is pyd.NegativeInt:
        return click.IntRange(max=0, max_open=True)
    if two_field_subtype is pyd.NonPositiveInt:
        return click.IntRange(max=0, max_open=False)
    # float types
    if two_field_subtype is pyd.PositiveFloat:
        return click.FloatRange(min=0, min_open=True)
    if two_field_subtype is pyd.NonNegativeFloat:
        return click.FloatRange(min=0, min_open=False)
    if two_field_subtype is pyd.NegativeFloat:
        return click.FloatRange(max=0, max_open=True)
    if two_field_subtype is pyd.NonPositiveFloat:
        return click.FloatRange(max=0, max_open=False)
    # int / float range types
    if is_pyd_conint(base_type, parent_args):
        return get_click_range_type(parent_args, range_type=click.IntRange)
    if is_pyd_confloat(base_type, parent_args):
        return get_click_range_type(parent_args, range_type=click.FloatRange)
    if is_pyd_condecimal(base_type, parent_args):
        return get_click_range_type(parent_args, range_type=click.FloatRange)
    # file / directory types
    if two_field_subtype is pyd.FilePath:
        return click.Path(exists=True, dir_okay=False)
    if two_field_subtype is pyd.DirectoryPath:
        return click.Path(exists=True, file_okay=False)
    if base_type in PATH_TYPES:
        return click.Path()
    return None


def is_pyd_conint(base_type: t.Any, parent_args: AnnotatedArgDict) -> bool:
    return base_type is int and isinstance(parent_args.get(2), Interval)


def is_pyd_confloat(base_type: t.Any, parent_args: AnnotatedArgDict) -> bool:
    return base_type is float and isinstance(parent_args.get(2), Interval)


def is_pyd_condecimal(base_type: t.Any, parent_args: AnnotatedArgDict) -> bool:
    return base_type is decimal.Decimal and isinstance(
        parent_args.get(2), Interval
    )


def is_namedtuple(hint: t.Any) -> bool:
    if hint is None:
        return False
    if not inspect.isclass(hint):
        return False
    return issubclass(hint, tuple) and hasattr(hint, "_fields")


def get_click_range_type(
    args: tuple, *, range_type: type[click.IntRange] | type[click.FloatRange]
) -> click.IntRange | click.FloatRange:
    min_, max_ = None, None
    min_open, max_open = False, False
    interval: Interval = args.get(2)
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
    return range_type(min=min_, max=max_, min_open=min_open, max_open=max_open)
