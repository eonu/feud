# Copyright (c) 2023-2025 Feud Developers.
# Distributed under the terms of the MIT License (see the LICENSE file).
# SPDX-License-Identifier: MIT
# This source code is part of the Feud project (https://feud.wiki).

from __future__ import annotations

import pytest

from .utils import annotate


class Helpers:
    annotate = annotate


@pytest.fixture(scope="module")
def helpers() -> type[Helpers]:
    return Helpers
