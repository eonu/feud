# Copyright (c) 2023 Feud Developers.
# Distributed under the terms of the MIT License (see the LICENSE file).
# SPDX-License-Identifier: MIT
# This source code is part of the Feud project (https://feud.wiki).

import re

import feud
from feud.version import VERSION, version_info


def test_version() -> None:
    """Check that the version is a valid SemVer version."""
    assert re.match(r"\d+\.\d+\.\d+[a-z0-9]*", VERSION)


def test_version_info() -> None:
    """Check that the version appears in the version info.

    FIXME: Not a thorough check of version_info() details.
    """
    assert VERSION in version_info()


def test_dunder() -> None:
    """Check that VERSION is the same as __version__."""
    assert feud.__version__ == VERSION
