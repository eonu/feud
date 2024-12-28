# Copyright (c) 2023 Feud Developers.
# Distributed under the terms of the MIT License (see the LICENSE file).
# SPDX-License-Identifier: MIT
# This source code is part of the Feud project (https://feud.wiki).

"""Tasks for running tests."""

from __future__ import annotations

from invoke.config import Config
from invoke.tasks import task


@task
def install(c: Config) -> None:
    """Install package with core and test dependencies."""
    c.run(
        "poetry install --sync --only base,main,tests -E extra-types -E email"
    )


@task
def doctest(c: Config) -> None:
    """Run doctests."""
    # skip:
    # - feud/click/context.py
    # - feud/decorators.py
    files: list[str] = [
        "feud/config.py",
        "feud/core/__init__.py",
        "feud/core/command.py",
        "feud/core/group.py",
    ]
    c.run(f"poetry run python -m doctest {' '.join(files)}")


@task
def unit(c: Config, *, cov: bool = False) -> None:
    """Run unit tests."""
    command: str = "poetry run pytest tests/"

    if cov:
        command = f"{command} --cov feud --cov-report xml"

    c.run(command)
