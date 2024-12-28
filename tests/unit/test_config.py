# Copyright (c) 2023 Feud Developers.
# Distributed under the terms of the MIT License (see the LICENSE file).
# SPDX-License-Identifier: MIT
# This source code is part of the Feud project (https://feud.wiki).

import pytest

from feud.config import Config


def test_create_no_base_no_kwargs() -> None:
    """No keyword arguments set."""
    config = Config._create()  # noqa: SLF001
    assert config.negate_flags is True
    assert config.show_help_defaults is True
    assert config.show_help_datetime_formats is False
    assert config.show_help_envvars is True
    assert config.pydantic_kwargs == {}
    assert config.rich_click_kwargs == {"show_arguments": True}


def test_create_no_base_none_kwargs() -> None:
    """Keyword arguments set to None."""
    config = Config._create(  # noqa: SLF001
        negate_flags=None,
        show_help_defaults=None,
        show_help_datetime_formats=None,
        show_help_envvars=None,
        pydantic_kwargs=None,
    )
    assert config.negate_flags is True
    assert config.show_help_defaults is True
    assert config.show_help_datetime_formats is False
    assert config.show_help_envvars is True
    assert config.pydantic_kwargs == {}
    assert config.rich_click_kwargs == {"show_arguments": True}


def test_create_no_base_with_kwargs_default() -> None:
    """Keyword arguments set to default values."""
    config = Config._create(  # noqa: SLF001
        negate_flags=True,
        show_help_defaults=True,
    )
    assert config.negate_flags is True
    assert config.show_help_defaults is True


def test_create_no_base_with_kwargs_non_default() -> None:
    """Keyword arguments set to non-default values."""
    config = Config._create(  # noqa: SLF001
        negate_flags=False,
        show_help_defaults=False,
    )
    assert config.negate_flags is False
    assert config.show_help_defaults is False


def test_create_base_with_no_base_kwargs_no_override_kwargs() -> None:
    """Base configuration with no base keyword arguments set
    and no override keyword arguments set.
    """
    base = Config._create()  # noqa: SLF001
    config = Config._create(base=base)  # noqa: SLF001
    assert config == base


def test_create_base_with_no_base_kwargs_override_kwargs() -> None:
    """Base configuration with no base keyword arguments set
    and with override keyword arguments set.
    """
    base = Config._create()  # noqa: SLF001
    config = Config._create(  # noqa: SLF001
        base=base,
        negate_flags=False,
        show_help_defaults=False,
    )
    assert config.negate_flags is False
    assert config.show_help_defaults is False


def test_create_base_with_base_kwargs_default_no_override_kwargs() -> None:
    """Base configuration with base keyword arguments set to default values
    and no override keyword arguments set.
    """
    base = Config._create(  # noqa: SLF001
        negate_flags=True,
        show_help_defaults=True,
    )
    config = Config._create(base=base)  # noqa: SLF001
    assert config == base


def test_create_base_with_base_kwargs_default_override_kwargs() -> None:
    """Base configuration with base keyword arguments set to default values
    and override keyword arguments set.
    """
    base = Config._create(  # noqa: SLF001
        negate_flags=True,
        show_help_defaults=True,
    )
    config = Config._create(  # noqa: SLF001
        base=base,
        negate_flags=False,
        show_help_defaults=False,
    )
    assert config.negate_flags is False
    assert config.show_help_defaults is False


def test_create_base_with_base_kwargs_non_default_no_override_kwargs() -> None:
    """Base configuration with base keyword arguments set to non-default values
    and no override keyword arguments set.
    """
    base = Config._create(  # noqa: SLF001
        negate_flags=False,
        show_help_defaults=False,
    )
    config = Config._create(base=base)  # noqa: SLF001
    assert config == base


def test_create_base_with_base_kwargs_non_default_override_kwargs() -> None:
    """Base configuration with base keyword arguments set to non-default values
    and override keyword arguments set.
    """
    base = Config._create(  # noqa: SLF001
        negate_flags=False,
        show_help_defaults=False,
    )
    config = Config._create(  # noqa: SLF001
        base=base,
        negate_flags=False,
        show_help_defaults=False,
    )
    assert config.negate_flags is False
    assert config.show_help_defaults is False


# test instantiate
def test_init_create() -> None:
    """Should not be able to instantiate feud.Config."""
    with pytest.raises(RuntimeError):
        Config()
