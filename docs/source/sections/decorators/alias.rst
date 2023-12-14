Aliasing parameters
===================

.. contents:: Table of Contents
    :class: this-will-duplicate-information-and-it-is-still-useful-here
    :local:
    :backlinks: none
    :depth: 3

In CLIs, it is common for options to have an alias allowing
for quicker short-hand usage. 

For instance, an option named ``--verbose`` may be aliased as ``-v``.

Instead of manually specifying an alias with :py:func:`click.option`, e.g.

.. code:: python

    import feud
    from feud import click

    @click.option("--verbose", "-v", help="Whether to print or not.", type=bool)
    def my_command(*, verbose: bool = False):
        """A command that does some logging."""

    feud.run(my_command)

You can use the :py:func:`.alias` decorator to do this, which also means you 
do not have to manually provide ``help`` or ``type`` to :py:func:`click.option`, 
and can instead rely on type hints and docstrings.

.. code:: python

    import feud

    @feud.alias(verbose="-v")
    def my_command(*, verbose: bool = False):
        """A command that does some logging.
        
        Parameters
        ----------
        verbose:
            Whether to print or not.
        """

    feud.run(my_command)

.. note::

    In the case of boolean flags such as ``--verbose`` in this case, the ``--no-verbose``
    option will also have a corresponding ``--no-v`` alias automatically defined.
   
----

API reference
-------------

.. autofunction:: feud.decorators.alias
