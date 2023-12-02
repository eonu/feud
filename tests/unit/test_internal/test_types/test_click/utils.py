# Copyright (c) 2023-2025 Feud Developers.
# Distributed under the terms of the MIT License (see the LICENSE file).
# SPDX-License-Identifier: MIT
# This source code is part of the Feud project (https://feud.wiki).

import typing as t


def annotate(hint: t.Any) -> t.Annotated[t.Any, "annotation"]:
    return t.Annotated[hint, "annotation"]
