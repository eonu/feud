Commands
========

.. contents:: Table of Contents
    :class: this-will-duplicate-information-and-it-is-still-useful-here
    :local:
    :backlinks: none
    :depth: 3

Commands are the core component of a CLI, running a user-defined function that
may be parameterized with arguments or options.

Commands may be included within :doc:`group`, which usually contain a set of related commands.

Commands may be executed using :py:func:`.run`.

.. seealso::

    The Click API documentation does a great job at clarifying the following command-line terminology:

    - `Commands and groups <https://click.palletsprojects.com/en/8.1.x/commands/>`__
    - `Parameters <https://click.palletsprojects.com/en/8.1.x/parameters/>`__
  
      - `Arguments <https://click.palletsprojects.com/en/8.1.x/arguments/>`__
      - `Options <https://click.palletsprojects.com/en/8.1.x/options/>`__

----

Understanding function signatures
---------------------------------

To understand how Feud converts a function into a :py:class:`click.Command`,
consider the following function.

.. tip::

    When called with :py:func:`.run`, a function does not need to be manually decorated with :py:func:`.command`.

.. code:: python

    # func.py

    import feud

    def func(arg1: int, arg2: str, *, opt1: float, opt2: int = 0):
        ...

    if __name__ == "__main__":
        feud.run(func)

This function signature consists of:

- two *positional* parameters ``arg1`` and ``arg2``,
- two *keyword-only* parameters ``opt1`` and ``opt2``.

.. note::

    The ``*`` operator in Python is used to indicate where positional parameters end and keyword-only parameters begin.

When calling ``func`` in Python:

- values for the positional parameters can be provided without specifying the parameter name,
- values for the keyword-only parameters must be provided by specifying the parameter name.

.. code:: python

    func(1, "hello", opt1=2.0, opt2=3)

where ``arg1`` takes the value ``1``, and ``arg2`` takes the value ``"hello"``.

Similarly, when building a :py:class:`click.Command`, Feud treats:

- positional parameters as *arguments* (specified **without providing** a parameter name),
- keyword-only parameters as *options* (specified **by providing** a parameter name).

.. code:: console

    $ python func.py 1 hello --opt1 2.0 --opt2 3

Note that ``--opt1`` is a required option as it has no default specified, whereas ``--opt2`` is not required.

.. tip::

    Feud does **not** support command-line *arguments* with default values. 
    
    In such a scenario, it is recommended to configure the parameter as a command-line *option* 
    (by specifying it as a keyword-only parameter instead of a positional parameter),
    since an argument with a default value is optional after all.
  
API reference
-------------

.. autofunction:: feud.core.command
    