Using environment variables
===========================

.. contents:: Table of Contents
    :class: this-will-duplicate-information-and-it-is-still-useful-here
    :local:
    :backlinks: none
    :depth: 3

In CLIs, environment variables are often used as an alternative method of 
providing input for options. This is particularly useful for sensitive 
information such as API keys, tokens and passwords.

For example, an option named ``--token`` may be provided by an environment
variable ``SECRET_TOKEN``.

Instead of manually specifying an environment variable with :py:func:`click.option`, e.g.

.. code:: python

    # my_command.py

    import feud
    from feud import click, typing as t

    @click.option(
        "--token", help="A secret token.", type=str, 
        envvar="SECRET_TOKEN", show_envvar=True,
    )
    def my_command(*, token: t.constr(max_length=16)):
        """A command requiring a token no longer than 16 characters."""

    if __name__ == "__main__":
        feud.run(my_command)

You can use the :py:func:`.env` decorator to do this, which also means you 
do not have to manually provide ``help`` or ``type`` to :py:func:`click.option`, 
and can instead rely on type hints and docstrings.

.. code:: python

    # my_command.py

    import feud
    from feud import typing as t

    @feud.env(token="SECRET_TOKEN")
    def my_command(*, token: t.constr(max_length=16)):
        """A command requiring a token no longer than 16 characters.
        
        Parameters
        ----------
        token:
            A secret token.
        """

    if __name__ == "__main__":
        feud.run(my_command)

This can be called with ``SECRET_TOKEN=hello-world python command.py``, for example.
   
----

API reference
-------------

.. autofunction:: feud.decorators.env
