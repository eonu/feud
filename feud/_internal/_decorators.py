# Copyright (c) 2023-2025 Feud Developers.
# Distributed under the terms of the MIT License (see the LICENSE file).
# SPDX-License-Identifier: MIT
# This source code is part of the Feud project (https://feud.wiki).

from __future__ import annotations

import functools as ft
import re
import typing as t

import pydantic as pyd
import pydantic_core as pydc

try:
    import rich_click as click
except ImportError:
    import click


def validate_call(
    func: t.Callable,
    /,
    *,
    name: str,
    meta_vars: dict[str, str],
    sensitive_vars: dict[str, bool],
    pydantic_kwargs: dict[str, t.Any],
) -> t.Callable:
    @ft.wraps(func)
    def wrapper(*args: t.Any, **kwargs: t.Any) -> t.Callable:
        try:
            config = pyd.ConfigDict(**pydantic_kwargs)
            return pyd.validate_call(func, config=config)(*args, **kwargs)
        except pyd.ValidationError as e:
            msg = re.sub(
                r"validation error(s?) for (.*)\n",
                rf"validation error\1 for command {name!r}\n",
                str(e),
            )
            for param, meta_var in meta_vars.items():
                msg = re.sub(
                    rf"\n({param})(\.(\d+))?", rf"\n{meta_var} [\3]", msg
                )
                msg = re.sub(r"\s\[\].*\n", "\n", msg)
                msg = re.sub(r"\[type=.*, (input_value=.*)", r"[\1", msg)
                msg = re.sub(r"(.*), input_type=.*\]", r"\1]", msg)
                msg = re.sub(
                    r"\n\s+For further information visit.*(\n?)", r"\1", msg
                )
                if sensitive_vars[param]:
                    msg = re.sub(
                        rf"({meta_var}\s*\n\s.*\[input_value=).*(\])",
                        r"\1hidden\2",
                        msg,
                    )
            raise click.UsageError(msg) from None
        except pydc.SchemaError as e:
            msg = re.sub(
                r'^Error building "call" validator:',
                f"Error building command {name!r}",
                str(e),
            )
            raise click.ClickException(msg) from None

    return wrapper
