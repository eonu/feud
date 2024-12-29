# Copyright (c) 2023 Feud Developers.
# Distributed under the terms of the MIT License (see the LICENSE file).
# SPDX-License-Identifier: MIT
# This source code is part of the Feud project (https://feud.wiki).

from __future__ import annotations

import typing as t

import docstring_parser

from feud import click


def get_description(
    obj: docstring_parser.Docstring | click.Command | t.Callable | str,
    /,
) -> str | None:
    """Retrieve the description section of a docstring.

    Modified from https://github.com/rr-/docstring_parser/pull/83.

        The MIT License (MIT)

        Copyright (c) 2018 Marcin Kurczewski

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
    doc: docstring_parser.Docstring | None = None

    if isinstance(obj, str):
        doc = docstring_parser.parse(obj)
    elif isinstance(obj, click.Command):
        if func := getattr(obj, "__func__", None):
            doc = docstring_parser.parse_from_object(func)
    elif isinstance(obj, docstring_parser.Docstring):
        doc = obj
    elif callable(obj):
        doc = docstring_parser.parse_from_object(obj)

    ret = None
    if doc:
        ret = []
        if doc.short_description:
            ret.append(doc.short_description)
            if doc.blank_after_short_description:
                ret.append("")
        if doc.long_description:
            ret.append(doc.long_description)

    if ret is None or ret == []:
        return None

    return "\n".join(ret).strip()
