# Copyright (c) 2023 Feud Developers.
# Distributed under the terms of the MIT License (see the LICENSE file).
# SPDX-License-Identifier: MIT
# This source code is part of the Feud project (https://feud.wiki).

"""Package exceptions."""

__all__ = ["CompilationError", "RegistrationError"]


class CompilationError(Exception):
    """An exception indicating an issue that would prevent a
    :py:class:`click.Command` command from being generated as expected.
    """


class RegistrationError(Exception):
    """An exception relating to the registering or deregistering of
    :py:class:`.Group` classes.
    """
