# Copyright (c) 2023 Feud Developers.
# Distributed under the terms of the MIT License (see the LICENSE file).
# SPDX-License-Identifier: MIT
# This source code is part of the Feud project (https://feud.wiki).

"""Build powerful CLIs with simple idiomatic Python, driven by type hints.
Not all arguments are bad.
"""

import feud.version

__version__ = feud.version.VERSION

from feud import click as click
from feud import exceptions as exceptions
from feud import typing as typing
from feud.config import *
from feud.core import *
from feud.decorators import *
from feud.exceptions import *
