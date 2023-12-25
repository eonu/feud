Groups
======

.. contents:: Table of Contents
    :class: this-will-duplicate-information-and-it-is-still-useful-here
    :local:
    :backlinks: none
    :depth: 3

Groups are a component of CLIs that allow you to group together related :doc:`command`.

In addition to commands, groups may also contain further nested groups by :py:obj:`.register`\ ing subgroups, 
allowing for the construction of complex CLIs with many levels.

Groups and their subgroups or commands can be executed using :py:func:`.run`.

.. seealso::

    The Click API documentation does a great job at clarifying the following command-line terminology:

    - `Commands and groups <https://click.palletsprojects.com/en/8.1.x/commands/>`__
    - `Parameters <https://click.palletsprojects.com/en/8.1.x/parameters/>`__
  
      - `Arguments <https://click.palletsprojects.com/en/8.1.x/arguments/>`__
      - `Options <https://click.palletsprojects.com/en/8.1.x/options/>`__

----

API reference
-------------

.. autoclass:: feud.core.group.Group
    :members:
    :exclude-members: from_dict, from_iter, from_module

.. autofunction:: feud.core.group.compile
    