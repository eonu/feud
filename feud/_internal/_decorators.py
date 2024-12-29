# Copyright (c) 2023 Feud Developers.
# Distributed under the terms of the MIT License (see the LICENSE file).
# SPDX-License-Identifier: MIT
# This source code is part of the Feud project (https://feud.wiki).

from __future__ import annotations

import functools as ft
import inspect
import re
import typing as t

import pydantic as pyd
import pydantic_core as pydc

from feud import click

AnyCallableT = t.TypeVar("AnyCallableT", bound=t.Callable[..., t.Any])


def validate_call(
    func: t.Callable,
    /,
    *,
    name: str,
    param_renames: dict[str, str],
    meta_vars: dict[str, str],
    sensitive_vars: dict[str, bool],
    positional: list[str],
    var_positional: str | None,
    pydantic_kwargs: dict[str, t.Any],
) -> t.Callable[[AnyCallableT], AnyCallableT]:
    @ft.wraps(func)
    def wrapper(*args: t.Any, **kwargs: t.Any) -> t.Callable:
        try:
            # move positional arguments
            for arg in positional:
                pos_arg = kwargs.pop(arg, inspect._empty)  # noqa: SLF001
                if pos_arg is not inspect._empty:  # noqa: SLF001
                    args += (pos_arg,)

            # move *args to positional arguments
            if var_positional is not None:
                var_pos_args = kwargs.pop(
                    var_positional,
                    inspect._empty,  # noqa: SLF001
                )
                if var_pos_args is not inspect._empty:  # noqa: SLF001
                    args += var_pos_args

            # apply renaming for any options
            inv_mapping = {v: k for k, v in param_renames.items()}
            true_kwargs = {inv_mapping.get(k, k): v for k, v in kwargs.items()}

            # create Pydantic configuration
            config = pyd.ConfigDict(
                **pydantic_kwargs,  # type: ignore[typeddict-item]
            )

            # validate the function call
            return pyd.validate_call(  # type: ignore[call-overload]
                func,
                config=config,
            )(
                *args,
                **true_kwargs,
            )
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

    return wrapper  # type: ignore[return-value]
