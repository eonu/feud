Grouping command options
========================

.. contents:: Table of Contents
    :class: this-will-duplicate-information-and-it-is-still-useful-here
    :local:
    :backlinks: none
    :depth: 3

In cases when a command has many options, it can be useful to divide these
options into different sections which are displayed on the command help page. 
For instance, basic and advanced options.

The :py:func:`.section` decorator can be used to define these sections for a command.

.. seealso::

    :py:obj:`.Group.__sections__()` can be used to similarly partition commands 
    and subgroups displayed on a :py:class:`.Group` help page.
   
----

API reference
-------------

.. autofunction:: feud.decorators.section
