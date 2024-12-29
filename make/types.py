# Copyright (c) 2023 Feud Developers.
# Distributed under the terms of the MIT License (see the LICENSE file).
# SPDX-License-Identifier: MIT
# This source code is part of the Feud project (https://feud.wiki).

"""Tasks for running static type checks."""

from __future__ import annotations

from invoke.config import Config
from invoke.tasks import task


@task
def install(c: Config) -> None:
    """Install package with core and dev dependencies."""
    c.run("poetry install --sync --only base,main,types -E all")


@task
def check(c: Config) -> None:
    """Type check Python package files."""
    c.run("poetry run mypy feud")
