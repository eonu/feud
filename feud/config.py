# Copyright (c) 2023 Feud Developers.
# Distributed under the terms of the MIT License (see the LICENSE file).
# SPDX-License-Identifier: MIT
# This source code is part of the Feud project (https://feud.wiki).

"""Configuration for defining commands using :py:func:`.command` or
groups using :py:class:`.Group`.
"""

from __future__ import annotations

import inspect
import typing as t

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

    #: Whether to display environment variable names in command help.
    show_help_envvars: bool = True

    #: Validation settings for
    #: :py:func:`pydantic.validate_call_decorator.validate_call`.
    pydantic_kwargs: dict[str, t.Any] = {}

    #: Styling settings for ``rich-click``.
    #:
    #: See all available options
    #: `here <https://github.com/ewels/rich-click/blob/e6a3add46c591d49079d440917700dfe28cf0cfe/src/rich_click/rich_help_configuration.py#L50>`__
    #: (as of ``rich-click`` v1.7.2).
    rich_click_kwargs: dict[str, t.Any] = {"show_arguments": True}

    def __init__(self: t.Self, **kwargs: t.Any) -> None:
        caller: str | None = None
        frame = inspect.currentframe()
        if frame and frame.f_back:
            caller = frame.f_back.f_code.co_name
        if caller != Config._create.__name__:
            msg = (
                "The feud.Config class should not be instantiated directly, "
                "the feud.config function should be used instead."
            )
            raise RuntimeError(msg)
        super().__init__(**kwargs)

    @classmethod
    def _create(
        cls: type[Config], base: Config | None = None, **kwargs: t.Any
    ) -> Config:
        config_kwargs = base.model_dump(exclude_unset=True) if base else {}
        for field in cls.model_fields:
            value: t.Any | None = kwargs.get(field)
            if value is not None:
                config_kwargs[field] = value
        return cls(**config_kwargs)


def config(
    *,
    negate_flags: bool | None = None,
    show_help_defaults: bool | None = None,
    show_help_datetime_formats: bool | None = None,
    show_help_envvars: bool | None = None,
    pydantic_kwargs: dict[str, t.Any] | None = None,
    rich_click_kwargs: dict[str, t.Any] | None = None,
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

    show_help_envvars:
        Whether to display environment variable names in command help.

    pydantic_kwargs:
        Validation settings for
        :py:func:`pydantic.validate_call_decorator.validate_call`.

    rich_click_kwargs:
        Styling settings for ``rich-click``.

        See all available options
        `here <https://github.com/ewels/rich-click/blob/e6a3add46c591d49079d440917700dfe28cf0cfe/src/rich_click/rich_help_configuration.py#L50>`__
        (as of ``rich-click`` v1.7.2).

    Returns
    -------
    Config
        The reusable configuration.

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
        show_help_envvars=show_help_envvars,
        pydantic_kwargs=pydantic_kwargs,
        rich_click_kwargs=rich_click_kwargs,
    )
