.. _configuration:

Configuration
=============

.. contents:: Table of Contents
    :class: this-will-duplicate-information-and-it-is-still-useful-here
    :local:
    :backlinks: none
    :depth: 3

:doc:`../core/command` are defined by :py:func:`.command`,
which accepts various Feud configuration key-word arguments such as 
``negate_flags`` or ``show_help_defaults`` directly.

Similarly, :doc:`../core/group` can be directly configured with Feud 
configuration key-word arguments provided when subclassing :py:class:`.Group`.

However, in some cases it may be useful to have a reusable configuration 
object that can be provided to other commands or groups. This functionality is 
implemented by :py:func:`.config`, which creates a configuration which can be 
provided to :py:func:`.command` or :py:class:`.Group`.

----

API reference
-------------

.. autofunction:: feud.config.config

.. autopydantic_model:: feud.config.Config
    :model-show-json: False
    :model-show-config-summary: False
    :exclude-members: __init__