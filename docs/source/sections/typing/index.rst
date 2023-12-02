Typing
======

Feud has a rich typing system based on `Pydantic <https://docs.pydantic.dev/latest/>`__,
allowing for CLIs that support Python standard library types, as well as complex types 
such as emails, IP addresses, file/directory paths, database connection strings and more.

All of the below types are made easily accessible through the :py:mod:`feud.typing` module.

.. tip::

    It is recommended to import the :py:mod:`feud.typing` module with an alias such as ``t`` for convenient short-hand use, e.g.

    .. code:: python
    
        from feud import typing as t

----

.. toctree::
   :titlesonly:

   stdlib.rst
   pydantic.rst
   pydantic_extra_types.rst
   other.rst

Usage
-----

Feud relies on type hints to determine the type for command-line argument/option input values.

.. dropdown:: Example
    :animate: fade-in

    Suppose we want a command for serving local files on a HTTP server with:

    - **Arguments**:
        - ``PORT``: Port to start the server on.
    - **Options**:
        - ``--watch/--no-watch``: Whether or not restart the server if source code changes.
        - ``--env``: Envionment mode to launch the server in (either ``dev`` or ``prod``).

    By default we should watch for changes and use the development environment.

    .. tab-set::

        .. tab-item:: Code

            .. code:: python

                # serve.py

                import feud
                from feud import typing as t

                def serve(port: t.PositiveInt, *, watch: bool = True, env: t.Literal["dev", "prod"] = "dev"):
                    """Start a local HTTP server.\f

                    Parameters
                    ----------
                    port:
                        Server port.
                    watch:
                        Watch source code for changes.
                    env:
                        Environment mode.
                    """
                    print(f"{port=!r} ({type(port)})")
                    print(f"{watch=!r} ({type(watch)})")
                    print(f"{env=!r} ({type(env)})")

                if __name__ == "__main__":
                    feud.run(serve)

        .. tab-item:: Help screen

            .. code:: bash

                $ python serve.py --help

            .. image:: /_static/images/help/typing.png
                :alt: serve.py help screen

        .. tab-item:: Usage

            .. card:: Valid input

                .. code:: bash

                    $ python serve.py 8080 --no-watch --env prod

                .. code::
                    
                    port=8080 (<class 'int'>)
                    watch=False (<class 'bool'>)
                    env='prod' (<class 'str'>)

            .. card:: Invalid input

                .. code:: bash

                    $ python serve.py 8080 --env test

                .. image:: /_static/images/examples/typing.png
                    :alt: serve.py error
