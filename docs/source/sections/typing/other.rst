Other types
===========

.. contents:: Table of Contents
    :class: this-will-duplicate-information-and-it-is-still-useful-here
    :local:
    :backlinks: none
    :depth: 3

Feud provides the following additional types for common CLI needs.

.. tip::

    All of the types listed on this page are easily accessible from the :py:mod:`feud.typing` module.

    It is recommended to import the :py:mod:`feud.typing` module with an alias such as ``t`` for convenient short-hand use, e.g.

    .. code:: python

        from feud import typing as t

        t.Counter  # feud.typing.custom.Counter
        t.concounter  # feud.typing.custom.concounter

----

Counting types
--------------

.. autodata:: feud.typing.custom.Counter
    :annotation:

.. autofunction:: feud.typing.custom.concounter
