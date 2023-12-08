# Copyright (c) 2023-2025 Feud Developers.
# Distributed under the terms of the MIT License (see the LICENSE file).
# SPDX-License-Identifier: MIT
# This source code is part of the Feud project (https://feud.wiki).

import typing as t

import pytest

import feud


def test_union(capsys: pytest.CaptureFixture) -> None:
    @feud.command
    def f(
        *,
        opt1: int | float,  # noqa: FA102
        opt2: t.Union[int, float],  # noqa: FA100
        opt3: str | int | None,  # noqa: FA102
        opt4: t.Optional[t.Union[str, int]],  # noqa: FA100
        opt5: t.Union[int, t.Union[float, str]],  # noqa: FA100
        opt6: int | None,  # noqa: FA102
        opt7: str | t.Annotated[str, "annotated"],  # noqa: FA102
    ) -> None:
        pass

    with pytest.raises(SystemExit):
        f(["--help"])

    out, _ = capsys.readouterr()

    assert (
        out.strip()
        == """
Usage: pytest [OPTIONS]

Options:
  --opt1 INTEGER | FLOAT         [required]
  --opt2 INTEGER | FLOAT         [required]
  --opt3 TEXT | INTEGER          [required]
  --opt4 TEXT | INTEGER          [required]
  --opt5 INTEGER | FLOAT | TEXT  [required]
  --opt6 INTEGER                 [required]
  --opt7 TEXT                    [required]
  --help                         Show this message and exit.
    """.strip()
    )
