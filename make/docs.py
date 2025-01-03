# Copyright (c) 2023 Feud Developers.
# Distributed under the terms of the MIT License (see the LICENSE file).
# SPDX-License-Identifier: MIT
# This source code is part of the Feud project (https://feud.wiki).

"""Tasks for generating Sphinx documentation."""

from invoke.config import Config
from invoke.tasks import task


@task
def install(c: Config) -> None:
    """Install package with core and docs dependencies."""
    c.run("poetry install --sync --only base,main,docs")


@task
def build(c: Config, *, watch: bool = True) -> None:
    """Build package Sphinx documentation."""
    if watch:
        command = (
            "poetry run sphinx-autobuild "
            "docs/source/ docs/build/html/ "
            "--watch docs/source/ --watch feud/ "
            "--ignore feud/_internal/"
        )
    else:
        command = "cd docs && make html"
    c.run(command)
