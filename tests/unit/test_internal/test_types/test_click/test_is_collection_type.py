# Copyright (c) 2023 Feud Developers.
# Distributed under the terms of the MIT License (see the LICENSE file).
# SPDX-License-Identifier: MIT
# This source code is part of the Feud project (https://feud.wiki).

from __future__ import annotations

import collections
import typing as t

import pytest

from feud._internal import _types


def annotate(hint: t.Any) -> t.Annotated[t.Any, "annotation"]:
    return t.Annotated[hint, "annotation"]


@pytest.fixture(scope="module")
def helpers(helpers: type) -> type:  # type[Helpers]
    def check_is_collection_type(
        *, annotated: bool, hint: t.Any, expected: tuple[bool, t.Any]
    ) -> None:
        if annotated:
            hint = helpers.annotate(hint)
        assert _types.click.is_collection_type(hint) == expected

    helpers.check_is_collection_type = check_is_collection_type

    return helpers


@pytest.mark.parametrize("annotated", [False, True])
@pytest.mark.parametrize(
    ("hint", "expected"),
    [
        (tuple, (True, None)),
        (t.Tuple, (True, None)),
        (t.Tuple[t.Any], (False, None)),
        (t.Tuple[int, str], (False, None)),
        (t.Tuple[t.Any, ...], (True, t.Any)),
        (t.Tuple[annotate(t.Any), ...], (True, annotate(t.Any))),
    ],
)
def test_tuple(
    helpers: type,
    *,
    annotated: bool,
    hint: t.Any,
    expected: tuple[bool, t.Any],
) -> None:
    helpers.check_is_collection_type(
        annotated=annotated,
        hint=hint,
        expected=expected,
    )


@pytest.mark.parametrize("annotated", [False, True])
@pytest.mark.parametrize(
    ("hint", "expected"),
    [
        (list, (True, None)),
        (t.List, (True, None)),
        (t.List[t.Any], (True, t.Any)),
        (t.List[annotate(t.Any)], (True, annotate(t.Any))),
    ],
)
def test_list(
    helpers: type,
    *,
    annotated: bool,
    hint: t.Any,
    expected: tuple[bool, t.Any],
) -> None:
    helpers.check_is_collection_type(
        annotated=annotated,
        hint=hint,
        expected=expected,
    )


@pytest.mark.parametrize("annotated", [False, True])
@pytest.mark.parametrize(
    ("hint", "expected"),
    [
        (set, (True, None)),
        (t.Set, (True, None)),
        (t.Set[t.Any], (True, t.Any)),
        (t.Set[annotate(t.Any)], (True, annotate(t.Any))),
    ],
)
def test_set(
    helpers: type,
    *,
    annotated: bool,
    hint: t.Any,
    expected: tuple[bool, t.Any],
) -> None:
    helpers.check_is_collection_type(
        annotated=annotated,
        hint=hint,
        expected=expected,
    )


@pytest.mark.parametrize("annotated", [False, True])
@pytest.mark.parametrize(
    ("hint", "expected"),
    [
        (frozenset, (True, None)),
        (t.FrozenSet, (True, None)),
        (t.FrozenSet[t.Any], (True, t.Any)),
        (t.FrozenSet[annotate(t.Any)], (True, annotate(t.Any))),
    ],
)
def test_frozenset(
    helpers: type,
    *,
    annotated: bool,
    hint: t.Any,
    expected: tuple[bool, t.Any],
) -> None:
    helpers.check_is_collection_type(
        annotated=annotated,
        hint=hint,
        expected=expected,
    )


@pytest.mark.parametrize("annotated", [False, True])
@pytest.mark.parametrize(
    ("hint", "expected"),
    [
        (collections.deque, (True, None)),
        (t.Deque, (True, None)),
        (t.Deque[t.Any], (True, t.Any)),
        (t.Deque[annotate(t.Any)], (True, annotate(t.Any))),
    ],
)
def test_deque(
    helpers: type,
    *,
    annotated: bool,
    hint: t.Any,
    expected: tuple[bool, t.Any],
) -> None:
    helpers.check_is_collection_type(
        annotated=annotated,
        hint=hint,
        expected=expected,
    )


@pytest.mark.parametrize("annotated", [False, True])
@pytest.mark.parametrize(
    ("hint", "expected"),
    [
        (t.NamedTuple("Point", x=int, y=str), (False, None)),
        (
            t.NamedTuple("Point", x=annotate(int), y=annotate(str)),
            (False, None),
        ),
    ],
)
def test_namedtuple(
    helpers: type,
    *,
    annotated: bool,
    hint: t.Any,
    expected: tuple[bool, t.Any],
) -> None:
    helpers.check_is_collection_type(
        annotated=annotated,
        hint=hint,
        expected=expected,
    )


@pytest.mark.parametrize("annotated", [False, True])
@pytest.mark.parametrize(
    ("hint", "expected"),
    [(t.Any, (False, None))],
)
def test_other(
    helpers: type,
    *,
    annotated: bool,
    hint: t.Any,
    expected: tuple[bool, t.Any],
) -> None:
    helpers.check_is_collection_type(
        annotated=annotated,
        hint=hint,
        expected=expected,
    )
