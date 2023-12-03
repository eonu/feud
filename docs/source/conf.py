# Copyright (c) 2023-2025 Feud Developers.
# Distributed under the terms of the MIT License (see the LICENSE file).
# SPDX-License-Identifier: MIT
# This source code is part of the Feud project (https://feud.wiki).

"""Configuration file for the Sphinx documentation builder.

For the full list of built-in configuration values, see the documentation:
https://www.sphinx-doc.org/en/master/usage/configuration.html

Project information:
https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
"""

import os
import sys

sys.path.insert(0, os.path.abspath("../.."))

project = "feud"
copyright = "2023-2025, Feud Developers"  # noqa: A001
author = "Edwin Onuonga (eonu)"
release = "0.1.0a2"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.autosummary",
    # "sphinx.ext.mathjax",
    # "sphinx.ext.viewcode",
    "sphinx.ext.intersphinx",
    "numpydoc",
    "sphinx_favicon",
    "sphinx_design",
    "sphinxcontrib.autodoc_pydantic",
]

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "pydantic": ("https://docs.pydantic.dev/latest", None),
    "click": ("http://click.pocoo.org/latest", None),
}

napoleon_numpy_docstring = True
napoleon_use_admonition_for_examples = True
autodoc_members = True
autodoc_member_order = "groupwise"  # bysource, groupwise, alphabetical
autodoc_typehints = "description"
autodoc_class_signature = "separated"
autosummary_generate = True
numpydoc_show_class_members = True

# Set master document
master_doc = "index"

# The suffix(es) of source filenames.
# You can specify multiple suffix as a list of string:
source_suffix = [".rst"]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["source/_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
html_theme = "furo"

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]

# Logos and favicons
html_logo = "_static/images/logo/logo.svg"
favicons = [
    {"href": "images/logo/logo.svg"},
    {"href": "images/favicon/favicon/favicon.ico"},
    {"href": "images/favicon/favicon/favicon-16x16.png"},
    {"href": "images/favicon/favicon/favicon-32x32.png"},
    {
        "rel": "apple-touch-icon",
        "href": "images/logo/favicon/apple-touch-icon-180x180.png",
    },
]


# Custom stylesheets
def setup(app) -> None:  # noqa: ANN001, D103
    app.add_css_file("css/heading.css")
