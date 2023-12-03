# Copyright (c) 2023-2025 Feud Developers.
# Distributed under the terms of the MIT License (see the LICENSE file).
# SPDX-License-Identifier: MIT
# This source code is part of the Feud project (https://feud.wiki).

"""Tasks for bumping the package version and updating CHANGELOG.md."""

import os
import re
from pathlib import Path
from typing import Pattern

from invoke.config import Config
from invoke.tasks import task


@task
def install(c: Config) -> None:
    """Install package with core and release dependencies."""
    c.run("poetry install --sync --only base,release")


def get_changelog_entry(v: str, /) -> str:
    """Get CHANGELOG.md entry with specified version."""
    v: str = re.escape(v)

    pattern: Pattern = rf"(?:^|\n)##\sv{v}[^\n]*\n(.*?)(?=\n##?\s|$)"

    with open("CHANGELOG.md") as f:
        changelog: str = f.read()

    if entry := re.search(pattern, changelog, flags=re.DOTALL):
        return entry.group(1).strip()
    return "No changelog entry found."


@task
def build(c: Config, *, v: str) -> None:
    """Build release."""
    root: Path = Path(os.getcwd())

    # bump Sphinx documentation version - docs/source/conf.py
    conf_path: Path = root / "docs" / "source" / "conf.py"
    with open(conf_path) as f:
        conf: str = f.read()
    with open(conf_path, "w") as f:
        f.write(re.sub(r'release = ".*"', f'release = "{v}"', conf))

    # bump package version - feud/__init__.py)
    init_path: Path = root / "feud" / "__init__.py"
    with open(init_path) as f:
        init: str = f.read()
    with open(init_path, "w") as f:
        f.write(re.sub(r'__version__ = ".*"', f'__version__ = "{v}"', init))

    # bump project version - pyproject.toml
    c.run(f"poetry version -q {v}")

    # auto-generate CHANGELOG.md entry
    c.run(f"poetry run -q auto-changelog -- --tag-prefix v --github -v v{v}")

    # print latest changelog entry
    entry: str = get_changelog_entry(v)
    print(entry)  # noqa: T201
