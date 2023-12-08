# Copyright (c) 2023-2025 Feud Developers.
# Distributed under the terms of the MIT License (see the LICENSE file).
# SPDX-License-Identifier: MIT
# This source code is part of the Feud project (https://feud.wiki).

"""Configuration for defining commands using :py:func:`.command` or
groups using :py:class:`.Group`.
"""

from __future__ import annotations

import inspect
from typing import Any

import pydantic as pyd

__all__ = ["Config", "config"]


class Config(pyd.BaseModel):
    """Class representing a reusable configuration for
    :py:func:`.command` and :py:class:`.Group` objects.

    .. warning::

        This class should **NOT** be instantiated directly ---
        :py:func:`.config` should be used to create a :py:class:`.Config`
        instead.
    """

    #: Whether to automatically add a negated variant for boolean flags.
    negate_flags: bool = True

    #: Whether to display default parameter values in command help.
    show_help_defaults: bool = True

    #: Whether to display datetime parameter formats in command help.
    show_help_datetime_formats: bool = False

    #: Validation settings for
    #: :py:func:`pydantic.validate_call_decorator.validate_call`.
    pydantic_kwargs: dict[str, Any] = {}

    def __init__(self: Config, **kwargs: Any) -> Config:
        caller: str = inspect.currentframe().f_back.f_code.co_name
        if caller != Config._create.__name__:
            msg = (
                "The feud.Config class should not be instantiated directly, "
                "the feud.config function should be used instead."
            )
            raise RuntimeError(msg)
        super().__init__(**kwargs)

    @classmethod
    def _create(
        cls: type[Config], base: Config | None = None, **kwargs: Any
    ) -> Config:
        config_kwargs = base.model_dump(exclude_unset=True) if base else {}
        for field in cls.model_fields:
            value: Any | None = kwargs.get(field)
            if value is not None:
                config_kwargs[field] = value
        return cls(**config_kwargs)


def config(
    *,
    negate_flags: bool | None = None,
    show_help_defaults: bool | None = None,
    show_help_datetime_formats: bool | None = None,
    pydantic_kwargs: dict[str, Any] | None = None,
) -> Config:
    """Create a reusable configuration for :py:func:`.command` or
    :py:class:`.Group` objects.

    See :py:class:`.Config` for the underlying configuration class.

    Parameters
    ----------
    negate_flags:
        Whether to automatically add a negated variant for boolean flags.

    show_help_defaults:
        Whether to display default parameter values in command help.

    show_help_datetime_formats:
        Whether to display datetime parameter formats in command help.

    pydantic_kwargs:
        Validation settings for
        :py:func:`pydantic.validate_call_decorator.validate_call`.

    Returns
    -------
    The reusable :py:class:`.Config`.

    Examples
    --------
    Providing a configuration to :py:func:`.command`.

    >>> import feud
    >>> config = feud.config(show_help_defaults=False)
    >>> @feud.command(config=config)
    ... def func(*, opt1: int, opt2: bool = True):
    ...     pass
    >>> all(not param.show_default for param in func.params)
    True

    Providing a configuration to :py:class:`.Group`.

    Note that the configuration is internally forwarded to the commands
    defined within the group.

    >>> import feud
    >>> config = feud.config(show_help_defaults=False)
    >>> class CLI(feud.Group, config=config):
    ...     def func(*, opt1: int, opt2: bool = True):
    ...         pass
    >>> all(not param.show_default for param in CLI.func.params)
    True
    """
    return Config._create(  # noqa: SLF001
        negate_flags=negate_flags,
        show_help_defaults=show_help_defaults,
        show_help_datetime_formats=show_help_datetime_formats,
        pydantic_kwargs=pydantic_kwargs,
    )
