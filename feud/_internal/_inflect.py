# Copyright (c) 2023 Feud Developers.
# Distributed under the terms of the MIT License (see the LICENSE file).
# SPDX-License-Identifier: MIT
# This source code is part of the Feud project (https://feud.wiki).

import re
import unicodedata

__all__ = ["sanitize", "optionize", "negate_option", "negate_alias"]


def transliterate(string: str) -> str:
    """Replace non-ASCII characters with an ASCII approximation. If no
    approximation exists, the non-ASCII character is ignored. The string must
    be ``unicode``.

    Example
    -------
    >>> transliterate("älämölö")
    "alamolo"
    >>> transliterate("Ærøskøbing")
    "rskbing"

    Source code from inflection package
    (https://github.com/jpvanhal/inflection).

        Copyright (C) 2012-2020 Janne Vanhala

        Permission is hereby granted, free of charge, to any person obtaining
        a copy of this software and associated documentation files
        (the "Software"), to deal in the Software without restriction,
        including without limitation the rights to use, copy, modify, merge,
        publish, distribute, sublicense, and/or sell copies of the Software,
        and to permit persons to whom the Software is furnished to do so,
        subject to the following conditions:

        The above copyright notice and this permission notice shall be
        included in all copies or substantial portions of the Software.

        THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
        EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
        MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
        NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
        BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
        ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
        CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
        SOFTWARE.
    """
    normalized = unicodedata.normalize("NFKD", string)
    return normalized.encode("ascii", "ignore").decode("ascii")


def parameterize(string: str, separator: str = "-") -> str:
    """Replace special characters in a string so that it may be used as part
    of a 'pretty' URL.

    Example
    -------
    >>> parameterize(u"Donald E. Knuth")
    "donald-e-knuth"

    Source code from inflection package
    (https://github.com/jpvanhal/inflection).

        Copyright (C) 2012-2020 Janne Vanhala

        Permission is hereby granted, free of charge, to any person obtaining
        a copy of this software and associated documentation files
        (the "Software"), to deal in the Software without restriction,
        including without limitation the rights to use, copy, modify, merge,
        publish, distribute, sublicense, and/or sell copies of the Software,
        and to permit persons to whom the Software is furnished to do so,
        subject to the following conditions:

        The above copyright notice and this permission notice shall be
        included in all copies or substantial portions of the Software.

        THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
        EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
        MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
        NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
        BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
        ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
        CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
        SOFTWARE.
    """
    string = transliterate(string)
    # Turn unwanted chars into the separator
    string = re.sub(r"(?i)[^a-z0-9\-_]+", separator, string)
    if separator:
        re_sep = re.escape(separator)
        # No more than one of the separator in a row.
        string = re.sub(r"%s{2,}" % re_sep, separator, string)
        # Remove leading/trailing separator.
        string = re.sub(rf"(?i)^{re_sep}|{re_sep}$", "", string)

    return string.lower()


def sanitize(name: str) -> str:
    """Sanitizes a string for preparation of usage as a command-line option.

    Example
    -------
    >>> sanitize("---a@b_c--")
    "a-b_c"
    """
    name = parameterize(name)
    return re.sub(r"^-*(.*)", r"\1", name)


def optionize(name: str) -> str:
    """Sanitizes a string and converts it into a command-line option.

    Example
    -------
    >>> optionize("opt_name")
    "--opt-name"
    """
    return "--" + sanitize(name)


def negate_option(option: str) -> str:
    """Negates a command-line option (for boolean flags).

    Example
    -------
    >>> negate_option("--opt")
    "--no-opt"
    """
    return "--no" + option.removeprefix("-")


def negate_alias(alias: str) -> str:
    """Negates an alias for a boolean flag.

    Example
    -------
    >>> negate_alias("-a")
    "--no-a"
    """
    return "--no" + alias
