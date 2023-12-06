# Copyright (c) 2023-2025 Feud Developers.
# Distributed under the terms of the MIT License (see the LICENSE file).
# SPDX-License-Identifier: MIT
# This source code is part of the Feud project (https://feud.wiki).

"""Version information for Feud."""

__all__ = ["VERSION", "version_info"]

VERSION = "0.1.0"


def version_info() -> str:
    """Return complete version information for Feud and its dependencies."""
    import importlib.metadata as importlib_metadata
    import platform
    import sys
    from pathlib import Path

    # get data about packages that:
    # - are closely related to feud,
    # - use feud,
    # - often conflict with feud.
    package_names = {
        "click",
        "pydantic",
        "docstring-parser",
        "rich-click",
        "rich",
        "email-validator",
        "pydantic-extra-types",
        "phonenumbers",
        "pycountry",
    }
    related_packages = []

    for dist in importlib_metadata.distributions():
        name = dist.metadata["Name"]
        if name in package_names:
            related_packages.append(f"{name}-{dist.version}")

    info = {
        "feud version": VERSION,
        "install path": Path(__file__).resolve().parent,
        "python version": sys.version,
        "platform": platform.platform(),
        "related packages": " ".join(related_packages),
    }
    return "\n".join(
        "{:>30} {}".format(k + ":", str(v).replace("\n", " "))
        for k, v in info.items()
    )
