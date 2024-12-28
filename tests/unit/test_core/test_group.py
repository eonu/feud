# Copyright (c) 2023 Feud Developers.
# Distributed under the terms of the MIT License (see the LICENSE file).
# SPDX-License-Identifier: MIT
# This source code is part of the Feud project (https://feud.wiki).

import typing as t
from collections import OrderedDict
from operator import itemgetter
from pathlib import Path

import pytest

import feud
from feud import click
from feud.core.group import Section


def assert_help(
    __obj: t.Union[
        feud.Group,
        click.Group,
        click.Command,
        t.Callable,
    ],
    /,
    *,
    capsys: pytest.CaptureFixture,
    expected: str,
) -> None:
    with pytest.raises(SystemExit):
        feud.run(__obj, ["--help"])
    out, _ = capsys.readouterr()
    assert out.strip() == expected.strip()


def test_undecorated_commands() -> None:
    class Test(feud.Group):
        def f(*, arg1: int) -> None:
            pass

        def g(*, arg1: int, arg2: bool) -> None:
            pass

    assert isinstance(Test.f, click.Command)
    assert len(Test.f.params) == 1

    assert isinstance(Test.g, click.Command)
    assert len(Test.g.params) == 2


def test_decorated_commands() -> None:
    class Test(feud.Group):
        @feud.command
        def f(*, arg1: int) -> None:
            pass

        @feud.command
        def g(*, arg1: int, arg2: bool) -> None:
            pass

    assert isinstance(Test.f, click.Command)
    assert len(Test.f.params) == 1

    assert isinstance(Test.g, click.Command)
    assert len(Test.g.params) == 2


def test_compile() -> None:
    class Test(feud.Group):
        def f(*, arg1: int) -> None:
            pass

        def g(*, arg1: int, arg2: bool) -> None:
            pass

    group = Test.compile()
    assert isinstance(group, click.Group)

    assert len(group.commands) == 2
    assert list(group.commands.keys()) == ["f", "g"]


def test_run_group() -> None:
    class Test(feud.Group):
        def f(*, arg1: int) -> int:
            return arg1

    assert feud.run(Test, ["f", "--arg1", "2"], standalone_mode=False) == 2
    assert feud.run(Test.f, ["--arg1", "2"], standalone_mode=False) == 2


def test_call_group() -> None:
    class Test(feud.Group):
        def f(*, arg1: int) -> int:
            return arg1

    assert Test(["f", "--arg1", "2"], standalone_mode=False) == 2


def test_help_docstring(capsys: pytest.CaptureFixture) -> None:
    class Test(
        feud.Group,
        epilog="Visit https://www.com for more information.",
    ):
        """Useful commands."""

        def f(*, arg1: int) -> None:
            """Do something."""

        def g(*, arg1: int) -> None:
            """Perform something."""

    assert_help(
        Test,
        capsys=capsys,
        expected="""
Usage: pytest [OPTIONS] COMMAND [ARGS]...

  Useful commands.

Options:
  --help  Show this message and exit.

Commands:
  f  Do something.
  g  Perform something.

  Visit https://www.com for more information.
        """,
    )


def test_help_click_kwarg(capsys: pytest.CaptureFixture) -> None:
    class Test(
        feud.Group,
        help="Useful commands.",
        epilog="Visit https://www.com for more information.",
    ):
        def f(*, arg1: int) -> None:
            """Do something."""

        def g(*, arg1: int) -> None:
            """Perform something."""

    assert_help(
        Test,
        capsys=capsys,
        expected="""
Usage: pytest [OPTIONS] COMMAND [ARGS]...

  Useful commands.

Options:
  --help  Show this message and exit.

Commands:
  f  Do something.
  g  Perform something.

  Visit https://www.com for more information.
        """,
    )


def test_config_kwarg_propagation() -> None:
    class Test(feud.Group, show_help_defaults=False):
        def f(*, arg1: int = 1) -> None:
            pass

        def g(*, arg1: int = 2, arg2: bool = False) -> None:
            pass

    group = Test.compile()
    for command in group.commands.values():
        for param in command.params:
            assert param.show_default is False

    class Test(feud.Group, show_help_defaults=True):
        def f(*, arg1: int = 1) -> None:
            pass

        def g(*, arg1: int = 2, arg2: bool = False) -> None:
            pass

    group = Test.compile()
    for command in group.commands.values():
        for param in command.params:
            assert param.show_default is True


def test_config_propagation() -> None:
    class Test(feud.Group, config=feud.config(show_help_defaults=False)):
        def f(*, arg1: int = 1) -> None:
            pass

        def g(*, arg1: int = 2, arg2: bool = False) -> None:
            pass

    group = Test.compile()
    for command in group.commands.values():
        for param in command.params:
            assert param.show_default is False

    class Test(feud.Group, config=feud.config(show_help_defaults=True)):
        def f(*, arg1: int = 1) -> None:
            pass

        def g(*, arg1: int = 2, arg2: bool = False) -> None:
            pass

    group = Test.compile()
    for command in group.commands.values():
        for param in command.params:
            assert param.show_default is True


def test_config_kwarg_override() -> None:
    class Test(feud.Group, show_help_defaults=False):
        @feud.command(show_help_defaults=True)
        def f(*, arg1: int = 1) -> None:
            pass

    group = Test.compile()
    for command in group.commands.values():
        for param in command.params:
            assert param.show_default is True


def test_subgroups_parent_single_child() -> None:
    class Parent(feud.Group):
        """This is the parent group."""

        def f(*, arg: int) -> None:
            """This is a command in the parent group."""
            return arg

    class Child(feud.Group):
        """This is a subgroup."""

        def g(*, arg: int) -> None:
            """This is a command in the subgroup."""
            return arg

    Parent.register(Child)
    assert Parent.subgroups() == [Child]
    assert Child.subgroups() == []

    parent = Parent.compile()
    f, child = itemgetter("f", "child")(parent.commands)

    assert isinstance(f, click.Command)
    assert f.help == "This is a command in the parent group."

    assert isinstance(child, click.Group)
    assert child.help == "This is a subgroup."

    g = child.commands["g"]
    assert isinstance(g, click.Command)
    assert g.help == "This is a command in the subgroup."
    assert parent(["child", "g", "--arg", "1"], standalone_mode=False) == 1


def test_subgroups_parent_multi_children() -> None:
    """Parent subgroup with multiple children.

    Parent
    /      \
    Child1  Child2
    """

    class Parent(feud.Group):
        """This is the parent group."""

        def f(*, arg: int) -> int:
            """This is a command in the parent group."""
            return arg

    class Child1(feud.Group):
        """This is the first subgroup."""

        def g(*, arg: int) -> int:
            """This is a command in the first subgroup."""
            return arg

    class Child2(feud.Group):
        """This is the second subgroup."""

        def h(*, arg: int) -> int:
            """This is a command in the second subgroup."""
            return arg

    Parent.register([Child1, Child2])
    assert Parent.subgroups() == [Child1, Child2]
    assert Child1.subgroups() == []
    assert Child2.subgroups() == []

    parent = Parent.compile()
    f, child1, child2 = itemgetter("f", "child1", "child2")(parent.commands)

    assert isinstance(f, click.Command)
    assert f.help == "This is a command in the parent group."
    assert parent(["f", "--arg", "1"], standalone_mode=False) == 1

    assert isinstance(child1, click.Group)
    assert child1.help == "This is the first subgroup."
    assert isinstance(child1.commands["g"], click.Command)
    assert (
        child1.commands["g"].help == "This is a command in the first subgroup."
    )
    assert parent(["child1", "g", "--arg", "1"], standalone_mode=False) == 1

    assert isinstance(child2, click.Group)
    assert child2.help == "This is the second subgroup."
    assert isinstance(child2.commands["h"], click.Command)
    assert (
        child2.commands["h"].help
        == "This is a command in the second subgroup."
    )
    assert parent(["child2", "h", "--arg", "1"], standalone_mode=False) == 1


def test_subgroups_nested() -> None:
    r"""Parent subgroup with multiple children.

    Parent
    /      \
        Child1  Child2
    /      \       \
    Child2  Child3  Child4
    \
         Child4
    """

    class Parent(feud.Group):
        """This is the parent group."""

        def f(*, arg: int) -> int:
            """This is a command in the parent group."""
            return arg

    class Child1(feud.Group):
        """This is the first subgroup."""

        def g(*, arg: int) -> int:
            """This is a command in the first subgroup."""
            return arg

    class Child2(feud.Group):
        """This is the second subgroup."""

        def h(*, arg: int) -> int:
            """This is a command in the second subgroup."""
            return arg

    class Child3(feud.Group):
        """This is the third subgroup."""

        def i(*, arg: int) -> int:
            """This is a command in the third subgroup."""
            return arg

    class Child4(feud.Group):
        """This is the fourth subgroup."""

        def j(*, arg: int) -> int:
            """This is a command in the fourth subgroup."""
            return arg

    Parent.register(Child1)
    Parent.register(Child2)
    Child1.register(Child2)
    Child1.register(Child3)
    Child2.register(Child4)

    assert Parent.subgroups() == [Child1, Child2]
    assert Child1.subgroups() == [Child2, Child3]
    assert Child2.subgroups() == [Child4]
    assert Child3.subgroups() == []
    assert Child4.subgroups() == []

    Parent.deregister()
    Child1.deregister()
    Child2.deregister()
    Child3.deregister()
    Child4.deregister()

    Parent.register([Child1, Child2])
    Child1.register([Child2, Child3])
    Child2.register(Child4)

    assert Parent.subgroups() == [Child1, Child2]
    assert Child1.subgroups() == [Child2, Child3]
    assert Child2.subgroups() == [Child4]
    assert Child3.subgroups() == []
    assert Child4.subgroups() == []

    Parent.deregister()
    Child1.deregister()
    Child2.deregister()
    Child3.deregister()
    Child4.deregister()

    Parent.register([Child1, Child2])
    Child1.register([Child2, Child3])
    Child2.register(Child4)

    assert Parent.subgroups() == [Child1, Child2]
    assert Child1.subgroups() == [Child2, Child3]
    assert Child2.subgroups() == [Child4]
    assert Child3.subgroups() == []
    assert Child4.subgroups() == []

    parent = Parent.compile()

    assert len(parent.commands) == 3
    f, child1, child2 = itemgetter("f", "child1", "child2")(parent.commands)
    assert isinstance(f, click.Command)
    assert isinstance(child1, click.Group)
    assert isinstance(child2, click.Group)

    assert f.help == "This is a command in the parent group."
    assert parent(["f", "--arg", "1"], standalone_mode=False) == 1

    assert len(child2.commands) == 2
    h, child4 = itemgetter("h", "child4")(child2.commands)
    assert isinstance(h, click.Command)
    assert isinstance(child4, click.Group)

    assert h.help == "This is a command in the second subgroup."
    assert parent(["child2", "h", "--arg", "1"], standalone_mode=False) == 1

    assert len(child4.commands) == 1
    j = child4.commands["j"]
    assert isinstance(j, click.Command)
    assert j.help == "This is a command in the fourth subgroup."
    assert (
        parent(["child2", "child4", "j", "--arg", "1"], standalone_mode=False)
        == 1
    )

    assert len(child1.commands) == 3
    g, child2, child3 = itemgetter("g", "child2", "child3")(child1.commands)
    assert isinstance(g, click.Command)
    assert isinstance(child2, click.Group)
    assert isinstance(child3, click.Group)

    assert g.help == "This is a command in the first subgroup."
    assert parent(["child1", "g", "--arg", "1"], standalone_mode=False) == 1

    assert len(child2.commands) == 2
    h, child4 = itemgetter("h", "child4")(child2.commands)
    assert isinstance(h, click.Command)
    assert isinstance(child4, click.Group)

    assert h.help == "This is a command in the second subgroup."
    assert parent(["child2", "h", "--arg", "1"], standalone_mode=False) == 1

    assert len(child4.commands) == 1
    j = child4.commands["j"]
    assert isinstance(j, click.Command)
    assert j.help == "This is a command in the fourth subgroup."
    assert (
        parent(["child2", "child4", "j", "--arg", "1"], standalone_mode=False)
        == 1
    )

    assert len(child2.commands) == 2
    h = child2.commands["h"]
    assert isinstance(h, click.Command)
    assert h.help == "This is a command in the second subgroup."
    assert (
        parent(["child1", "child2", "h", "--arg", "1"], standalone_mode=False)
        == 1
    )

    assert len(child3.commands) == 1
    i = child3.commands["i"]
    assert isinstance(i, click.Command)
    assert i.help == "This is a command in the third subgroup."
    assert (
        parent(["child1", "child3", "i", "--arg", "1"], standalone_mode=False)
        == 1
    )


def test_deregister_nested() -> None:
    class Parent(feud.Group):
        """This is the parent group."""

        def f(*, arg: int) -> int:
            """This is a command in the parent group."""
            return arg

    class Child1(feud.Group):
        """This is the first subgroup."""

        def g(*, arg: int) -> int:
            """This is a command in the first subgroup."""
            return arg

    class Child2(feud.Group):
        """This is the second subgroup."""

        def h(*, arg: int) -> int:
            """This is a command in the second subgroup."""
            return arg

    class Child3(feud.Group):
        """This is the third subgroup."""

        def i(*, arg: int) -> int:
            """This is a command in the third subgroup."""
            return arg

    Parent.register([Child1, Child2])
    Child1.register(Child2)
    Child2.register(Child3)

    assert Parent.subgroups() == [Child1, Child2]
    assert Child1.subgroups() == [Child2]
    assert Child2.subgroups() == [Child3]

    parent = Parent.compile()

    assert len(parent.commands) == 3
    f, child1, child2 = itemgetter("f", "child1", "child2")(parent.commands)
    assert isinstance(f, click.Command)
    assert isinstance(child1, click.Group)
    assert isinstance(child2, click.Group)

    assert f.help == "This is a command in the parent group."
    assert parent(["f", "--arg", "1"], standalone_mode=False) == 1

    assert len(child2.commands) == 2
    h, child3 = itemgetter("h", "child3")(child2.commands)
    assert isinstance(h, click.Command)
    assert isinstance(child3, click.Group)

    assert h.help == "This is a command in the second subgroup."
    assert parent(["child2", "h", "--arg", "1"], standalone_mode=False) == 1

    assert len(child3.commands) == 1
    i = child3.commands["i"]
    assert isinstance(i, click.Command)

    assert i.help == "This is a command in the third subgroup."
    assert (
        parent(["child2", "child3", "i", "--arg", "1"], standalone_mode=False)
        == 1
    )

    assert len(child1.commands) == 2
    g, child2 = itemgetter("g", "child2")(child1.commands)
    assert isinstance(g, click.Command)
    assert isinstance(child2, click.Group)

    assert g.help == "This is a command in the first subgroup."
    assert parent(["child1", "g", "--arg", "1"], standalone_mode=False) == 1

    assert len(child2.commands) == 2
    h, child3 = itemgetter("h", "child3")(child2.commands)
    assert isinstance(h, click.Command)
    assert isinstance(child3, click.Group)

    assert h.help == "This is a command in the second subgroup."
    assert (
        parent(["child1", "child2", "h", "--arg", "1"], standalone_mode=False)
        == 1
    )

    Child2.deregister(Child3)

    assert Parent.subgroups() == [Child1, Child2]
    assert Child1.subgroups() == [Child2]
    assert Child2.subgroups() == []

    parent = Parent.compile()

    assert len(parent.commands) == 3
    f, child1, child2 = itemgetter("f", "child1", "child2")(parent.commands)
    assert isinstance(f, click.Command)
    assert isinstance(child1, click.Group)
    assert isinstance(child2, click.Group)

    assert f.help == "This is a command in the parent group."
    assert parent(["f", "--arg", "1"], standalone_mode=False) == 1

    assert len(child2.commands) == 1
    h = child2.commands["h"]
    assert isinstance(h, click.Command)

    assert h.help == "This is a command in the second subgroup."
    assert parent(["child2", "h", "--arg", "1"], standalone_mode=False) == 1

    assert len(child1.commands) == 2
    g, child2 = itemgetter("g", "child2")(child1.commands)
    assert isinstance(g, click.Command)
    assert isinstance(child2, click.Group)

    assert g.help == "This is a command in the first subgroup."
    assert parent(["child1", "g", "--arg", "1"], standalone_mode=False) == 1

    assert len(child2.commands) == 1
    h = child2.commands["h"]
    assert isinstance(child3, click.Group)

    assert h.help == "This is a command in the second subgroup."
    assert (
        parent(["child1", "child2", "h", "--arg", "1"], standalone_mode=False)
        == 1
    )


def test_inheritance_config_kwargs() -> None:
    class Parent(
        feud.Group,
        negate_flags=False,
        show_help_defaults=False,
    ):
        pass

    class Child(Parent):
        pass

    assert Child.__feud_config__ == feud.config(
        negate_flags=False, show_help_defaults=False
    )

    class Child(Parent, show_help_defaults=True):
        pass

    assert Child.__feud_config__ == feud.config(
        negate_flags=False, show_help_defaults=True
    )


def test_inheritance_config_class() -> None:
    class Parent(
        feud.Group,
        config=feud.config(negate_flags=False, show_help_defaults=False),
    ):
        pass

    class Child(Parent):
        pass

    assert Child.__feud_config__ == feud.config(
        negate_flags=False, show_help_defaults=False
    )

    class Child(Parent, show_help_defaults=True):
        pass

    assert Child.__feud_config__ == feud.config(
        negate_flags=False, show_help_defaults=True
    )

    class Child(
        Parent,
        config=feud.config(show_help_defaults=True),
        show_help_datetime_formats=True,
    ):
        pass

    assert Child.__feud_config__ == feud.config(
        negate_flags=False,
        show_help_defaults=True,
        show_help_datetime_formats=True,
    )


def test_inheritance_ancestor() -> None:
    class Grandparent(feud.Group, name="older", negate_flags=False):
        def f(*, arg: int) -> int:
            return arg

    grandparent = Grandparent.compile()
    assert grandparent.name == "older"
    assert list(grandparent.commands) == ["f"]

    class Parent(Grandparent, name="old", show_help_defaults=False):
        def g(*, arg: int) -> int:
            return arg

    parent = Parent.compile()
    assert parent.name == "old"
    assert list(parent.commands) == ["f", "g"]
    assert all(
        isinstance(command, click.Command)
        for command in parent.commands.values()
    )

    class Child(Parent, name="young", show_help_datetime_formats=True):
        def h(*, arg: int) -> int:
            return arg

    child = Child.compile()
    assert child.name == "young"
    assert list(child.commands) == ["f", "g", "h"]
    assert all(
        isinstance(command, click.Command)
        for command in child.commands.values()
    )
    assert Child.__feud_config__ == feud.config(
        negate_flags=False,
        show_help_defaults=False,
        show_help_datetime_formats=True,
    )


def test_inheritance_multiple() -> None:
    class Mother(
        feud.Group, negate_flags=False, epilog="Are we one big family?"
    ):
        def f(*, arg: int) -> int:
            return arg

    mother = Mother.compile()
    assert mother.name == "mother"
    assert list(mother.commands) == ["f"]

    class Father(
        feud.Group, show_help_defaults=False, epilog="We are one big family!"
    ):
        def g(*, arg: int) -> int:
            return arg

    father = Father.compile()
    assert father.name == "father"
    assert list(father.commands) == ["g"]

    class Child(Mother, Father, show_help_datetime_formats=True):
        def h(*, arg: int) -> int:
            return arg

    child = Child.compile()
    assert list(child.commands) == ["f", "g", "h"]
    assert Child.__feud_config__ == feud.config(
        negate_flags=False,
        show_help_defaults=False,
        show_help_datetime_formats=True,
    )
    assert Child.__feud_click_kwargs__ == {
        "name": "father",
        "epilog": "We are one big family!",
    }

    class Child(Father, Mother, show_help_datetime_formats=True):
        def h(*, arg: int) -> int:
            return arg

    child = Child.compile()
    assert list(child.commands) == ["g", "f", "h"]
    assert Child.__feud_config__ == feud.config(
        negate_flags=False,
        show_help_defaults=False,
        show_help_datetime_formats=True,
    )
    assert Child.__feud_click_kwargs__ == {
        "name": "mother",
        "epilog": "Are we one big family?",
    }


def test_inheritance_overwrite_command() -> None:
    class Parent(feud.Group):
        def f(*, arg: str = "From the parent!") -> int:
            return arg

    class Child(Parent):
        def f(*, arg: str = "From the child!") -> str:
            return arg

    assert Child.f([], standalone_mode=False) == "From the child!"


def test_register_deregister_compile() -> None:
    class Parent(
        feud.Group,
        negate_flags=False,
        show_help_defaults=False,
        epilog="Visit https://www.com for more information.",
    ):
        """This is the parent group."""

        def f(*, arg: int) -> int:
            """This is a command in the parent group."""
            return arg

    class Subgroup(feud.Group):
        def g(*, arg: int) -> int:
            """This is a command in a subgroup."""
            return arg

    Parent.register(Subgroup)

    class Child(Parent):
        pass

    child = Child.compile()
    assert list(child.commands) == ["f", "subgroup"]

    Child.deregister(Subgroup)

    child = Child.compile()
    assert list(child.commands) == ["f"]

    class Child(Parent):
        pass

    parent = Parent.compile()
    assert list(parent.commands) == ["f", "subgroup"]

    child = Child.compile()
    assert list(child.commands) == ["f", "subgroup"]

    Parent.deregister(Subgroup)

    parent = Parent.compile()
    assert list(parent.commands) == ["f"]

    child = Child.compile()
    assert list(child.commands) == ["f", "subgroup"]


def test_register() -> None:
    class A(feud.Group):
        pass

    class B(feud.Group):
        pass

    class C(feud.Group):
        pass

    # A -> B - should allow
    A.register(B)
    assert A.subgroups() == [B]
    A.deregister()
    assert A.subgroups() == []

    # A -> B and A -> B - should allow but with a warning
    msg = (
        f"Group {B.__name__!r} is already registered as a "
        f"subgroup under {A.__name__!r} and will be ignored."
    )
    with pytest.warns(RuntimeWarning, match=msg):
        A.register([B, B])
    assert A.subgroups() == [B]
    A.deregister()
    assert A.subgroups() == []

    # A -> B and A -> C - should allow
    A.register([B, C])
    assert A.subgroups() == [B, C]
    A.deregister()
    assert A.subgroups() == []

    # A -> B, B -> A - shouldn't allow (circular dependency)
    A.register(B)
    msg = (
        f"Group {B.__name__!r} is a descendant subgroup of {A.__name__!r}, "
        "causing a circular dependency."
    )
    with pytest.raises(feud.RegistrationError, match=msg):
        B.register(A)
    assert A.subgroups() == [B]
    assert B.subgroups() == []
    for group in (A, B):
        group.deregister()
        assert group.subgroups() == []

    # A -> A - shouldn't allow (circular dependency)
    msg = f"Group {A.__name__!r} cannot be a subgroup of itself."
    with pytest.raises(feud.RegistrationError, match=msg):
        A.register(A)
    assert A.subgroups() == []
    A.deregister()
    assert A.subgroups() == []

    # A -> B, B -> C, C -> A - shouldn't allow (circular dependency)
    A.register(B)
    B.register(C)
    msg = (
        f"Group {C.__name__!r} is a descendant subgroup of {A.__name__!r}, "
        "causing a circular dependency."
    )
    with pytest.raises(feud.RegistrationError, match=msg):
        C.register(A)
    assert A.subgroups() == [B]
    assert B.subgroups() == [C]
    assert C.subgroups() == []
    for group in (A, B, C):
        group.deregister()
        assert group.subgroups() == []


def test_deregister() -> None:
    class A(feud.Group):
        pass

    class B(feud.Group):
        pass

    class C(feud.Group):
        pass

    A.register(B)
    assert A.subgroups() == [B]
    A.deregister(B)
    assert A.subgroups() == []

    msg = (
        f"Group {A.__name__!r} is not a registered subgroup under "
        f"{A.__name__!r} and will be ignored."
    )
    with pytest.warns(RuntimeWarning, match=msg):
        A.deregister(A)
    assert A.subgroups() == []

    msg = (
        f"Group {B.__name__!r} is not a registered subgroup under "
        f"{A.__name__!r} and will be ignored."
    )
    with pytest.warns(RuntimeWarning, match=msg):
        A.deregister(B)
    assert A.subgroups() == []

    A.register([B, C])
    assert A.subgroups() == [B, C]
    A.deregister(B)
    assert A.subgroups() == [C]
    A.deregister(C)
    assert A.subgroups() == []

    A.register([B, C])
    assert A.subgroups() == [B, C]
    A.deregister([B, C])
    assert A.subgroups() == []

    A.register([B, C])
    assert A.subgroups() == [B, C]
    msg = (
        f"Group {A.__name__!r} is not a registered subgroup under "
        f"{A.__name__!r} and will be ignored."
    )
    with pytest.warns(RuntimeWarning, match=msg):
        A.deregister(A)
    assert A.subgroups() == [B, C]
    A.deregister()

    A.register(B)
    msg = (
        f"Group {B.__name__!r} is not a registered subgroup under "
        f"{A.__name__!r} and will be ignored."
    )
    with pytest.warns(RuntimeWarning, match=msg):
        A.deregister([B, B])
    assert A.subgroups() == []


def test_descendants() -> None:
    class A(feud.Group):
        pass

    class B(feud.Group):
        pass

    class C(feud.Group):
        pass

    class D(feud.Group):
        pass

    class E(feud.Group):
        pass

    class F(feud.Group):
        pass

    A.register([B, C, D])
    B.register(D)
    C.register(E)
    E.register(F)

    assert F.descendants() == OrderedDict()
    assert E.descendants() == OrderedDict([(F, F.descendants())])
    assert C.descendants() == OrderedDict([(E, E.descendants())])
    assert D.descendants() == OrderedDict()
    assert B.descendants() == OrderedDict([(D, D.descendants())])
    assert A.descendants() == OrderedDict(
        [
            (B, B.descendants()),
            (C, C.descendants()),
            (D, D.descendants()),
        ]
    )


def test_help_no_docstring(capsys: pytest.CaptureFixture) -> None:
    class Test(feud.Group):
        pass

    assert_help(
        Test,
        capsys=capsys,
        expected="""
Usage: pytest [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.
        """,
    )


def test_help_simple_docstring(capsys: pytest.CaptureFixture) -> None:
    class Test(feud.Group):
        """This is a group."""

    assert_help(
        Test,
        capsys=capsys,
        expected="""
Usage: pytest [OPTIONS] COMMAND [ARGS]...

  This is a group.

Options:
  --help  Show this message and exit.
        """,
    )


def test_help_param_docstring(capsys: pytest.CaptureFixture) -> None:
    class Test(feud.Group):
        """This is a group.

        Parameters
        ----------
        param:
            Help for a parameter.
        """

    assert_help(
        Test,
        capsys=capsys,
        expected="""
Usage: pytest [OPTIONS] COMMAND [ARGS]...

  This is a group.

Options:
  --help  Show this message and exit.
        """,
    )


def test_help_override(capsys: pytest.CaptureFixture) -> None:
    class Test(feud.Group, help="Overridden."):
        """This is a group."""

    assert_help(
        Test,
        capsys=capsys,
        expected="""
Usage: pytest [OPTIONS] COMMAND [ARGS]...

  Overridden.

Options:
  --help  Show this message and exit.
        """,
    )


def test_main_help_no_docstrings(capsys: pytest.CaptureFixture) -> None:
    class Test(feud.Group):
        def __main__() -> None:
            pass

    assert_help(
        Test,
        capsys=capsys,
        expected="""
Usage: pytest [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.
        """,
    )


def test_main_help_class_docstring(capsys: pytest.CaptureFixture) -> None:
    class Test(feud.Group):
        """This is a class-level docstring."""

        def __main__() -> None:
            pass

    assert_help(
        Test,
        capsys=capsys,
        expected="""
Usage: pytest [OPTIONS] COMMAND [ARGS]...

  This is a class-level docstring.

Options:
  --help  Show this message and exit.
        """,
    )


def test_main_help_function_docstring(capsys: pytest.CaptureFixture) -> None:
    class Test(feud.Group):
        def __main__() -> None:
            """This is a function-level docstring."""

    assert_help(
        Test,
        capsys=capsys,
        expected="""
Usage: pytest [OPTIONS] COMMAND [ARGS]...

  This is a function-level docstring.

Options:
  --help  Show this message and exit.
        """,
    )


def test_main_help_both_docstrings(capsys: pytest.CaptureFixture) -> None:
    class Test(feud.Group):
        """This is a class-level docstring."""

        def __main__() -> None:
            """This is a function-level docstring."""

    assert_help(
        Test,
        capsys=capsys,
        expected="""
Usage: pytest [OPTIONS] COMMAND [ARGS]...

  This is a function-level docstring.

Options:
  --help  Show this message and exit.
        """,
    )


def test_main_help_both_docstrings_with_override(
    capsys: pytest.CaptureFixture
) -> None:
    class Test(feud.Group, help="Overridden."):
        """This is a class-level docstring."""

        def __main__() -> None:
            """This is a function-level docstring."""

    assert_help(
        Test,
        capsys=capsys,
        expected="""
Usage: pytest [OPTIONS] COMMAND [ARGS]...

  Overridden.

Options:
  --help  Show this message and exit.
        """,
    )


def test_main(capsys: pytest.CaptureFixture) -> None:
    class Test(feud.Group, invoke_without_command=True):
        """This group does something relative to a root directory.

        Parameters
        ----------
        root:
            Root directory
        """

        @staticmethod
        @click.version_option("0.1.0")
        @feud.alias(root="-r")
        def __main__(ctx: click.Context, *, root: Path = Path(".")) -> None:
            ctx.obj = {"root": root}
            return root

        @staticmethod
        def command(ctx: click.Context, path: Path) -> Path:
            """Returns a full path.

            Parameters
            ----------
            path:
                Relative path.
            """
            return ctx.obj["root"] / path

    group = Test.compile()

    assert_help(
        group,
        capsys=capsys,
        expected="""
Usage: pytest [OPTIONS] COMMAND [ARGS]...

  This group does something relative to a root directory.

Options:
  -r, --root PATH  Root directory  [default: .]
  --version        Show the version and exit.
  --help           Show this message and exit.

Commands:
  command  Returns a full path.
        """,
    )

    # check version
    with pytest.raises(SystemExit):
        group(["--version"])
    out, _ = capsys.readouterr()
    assert out.strip() == "pytest, version 0.1.0"

    # test invoke without command
    assert group(["-r", "/usr"], standalone_mode=False) == Path("/usr")

    # test command context
    assert group(
        ["-r", "/usr", "command", "bin/sh"],
        standalone_mode=False,
    ) == Path("/usr/bin/sh")


def test_main_inheritance_no_docstring(capsys: pytest.CaptureFixture) -> None:
    class Test(feud.Group, invoke_without_command=True):
        """This group does something relative to a root directory.

        Parameters
        ----------
        root:
            Root directory
        """

        @staticmethod
        @click.version_option("0.1.0")
        @feud.alias(root="-r")
        def __main__(ctx: click.Context, *, root: Path = Path(".")) -> None:
            ctx.obj = {"root": root}
            return root

        @staticmethod
        def command(ctx: click.Context, path: Path) -> Path:
            """Returns a full path.

            Parameters
            ----------
            path:
                Relative path.
            """
            return ctx.obj["root"] / path

    class Child(Test):
        pass

    group = Child.compile()

    assert_help(
        group,
        capsys=capsys,
        expected="""
Usage: pytest [OPTIONS] COMMAND [ARGS]...

  This group does something relative to a root directory.

Options:
  -r, --root PATH  Root directory  [default: .]
  --version        Show the version and exit.
  --help           Show this message and exit.

Commands:
  command  Returns a full path.
        """,
    )

    # check version
    with pytest.raises(SystemExit):
        group(["--version"])
    out, _ = capsys.readouterr()
    assert out.strip() == "pytest, version 0.1.0"

    # test invoke without command
    assert group(["-r", "/usr"], standalone_mode=False) == Path("/usr")

    # test command context
    assert group(
        ["-r", "/usr", "command", "bin/sh"],
        standalone_mode=False,
    ) == Path("/usr/bin/sh")


def test_main_inheritance_docstring(capsys: pytest.CaptureFixture) -> None:
    class Test(feud.Group, invoke_without_command=True):
        """This group does something relative to a root directory.

        Parameters
        ----------
        root:
            Root directory
        """

        @staticmethod
        @click.version_option("0.1.0")
        @feud.alias(root="-r")
        def __main__(ctx: click.Context, *, root: Path = Path(".")) -> None:
            ctx.obj = {"root": root}
            return root

        @staticmethod
        def command(ctx: click.Context, path: Path) -> Path:
            """Returns a full path.

            Parameters
            ----------
            path:
                Relative path.
            """
            return ctx.obj["root"] / path

    class Child(Test):
        """This is a new docstring.

        Parameters
        ----------
        root:
            Root directory
        """

    group = Child.compile()

    assert_help(
        group,
        capsys=capsys,
        expected="""
Usage: pytest [OPTIONS] COMMAND [ARGS]...

  This is a new docstring.

Options:
  -r, --root PATH  Root directory  [default: .]
  --version        Show the version and exit.
  --help           Show this message and exit.

Commands:
  command  Returns a full path.
        """,
    )

    # check version
    with pytest.raises(SystemExit):
        group(["--version"])
    out, _ = capsys.readouterr()
    assert out.strip() == "pytest, version 0.1.0"

    # test invoke without command
    assert group(["-r", "/usr"], standalone_mode=False) == Path("/usr")

    # test command context
    assert group(
        ["-r", "/usr", "command", "bin/sh"],
        standalone_mode=False,
    ) == Path("/usr/bin/sh")


def test_sections() -> None:
    class CLI(feud.Group):
        def command(*, arg: int) -> int:
            return arg

    class Subgroup(feud.Group):
        pass

    CLI.register(Subgroup)

    sections: list[Section] = CLI.__sections__()
    assert len(sections) == 1
    assert sections[0].items == ["subgroup"]


def test_add_commands_list() -> None:
    class CLI(feud.Group, invoke_without_command=True):
        @staticmethod
        @feud.alias(root="-r")
        def __main__(ctx: click.Context, *, root: Path = Path(".")) -> None:
            ctx.obj = {"root": root}
            return root

        @staticmethod
        def existing(ctx: click.Context, *, path: Path) -> Path:
            return ctx.obj["root"] / path

    def command(ctx: click.Context, *, path: Path) -> Path:
        return ctx.obj["root"] / path

    def _command(ctx: click.Context, *, path: Path) -> Path:
        return ctx.obj["root"] / path

    @feud.rename("renamed")
    def renamed_command(ctx: click.Context, *, path: Path) -> Path:
        return ctx.obj["root"] / path

    @feud.command
    @feud.rename("compiled-command")
    @feud.alias(path="-p")
    def compiled(ctx: click.Context, *, path: Path) -> Path:
        return ctx.obj["root"] / path

    CLI.add_commands([command, _command, renamed_command, compiled])

    cmds = {
        "existing": "existing",
        "command": "command",
        "_command": "_command",
        "renamed_command": "renamed",
        "compiled": "compiled-command",
    }

    # check registered commands
    assert set(CLI.__feud_commands__) == set(cmds)
    assert all(hasattr(CLI, cmd) for cmd in cmds)
    assert set(CLI.commands(name=True)) == set(cmds.values())

    # test various commands
    for cmd in cmds.values():
        assert CLI(
            ["-r", "/usr", cmd, "--path", "local/bin"], standalone_mode=False
        ) == Path("/usr/local/bin")

    # test command with aliased option
    assert CLI(
        ["-r", "/usr", "compiled-command", "-p", "local/bin"],
        standalone_mode=False,
    ) == Path("/usr/local/bin")

    # override existing command
    def existing(ctx: click.Context, *, path: Path) -> Path:
        return ctx.obj["root"] / path / "overwritten"

    CLI.add_commands([existing])

    # check command is registered
    assert CLI.__feud_commands__ == [*list(cmds)[1:], "existing"]
    assert hasattr(CLI, "existing")
    assert set(CLI.commands(name=True)) == set(cmds.values())

    # check command was actually overwritten
    assert CLI(
        ["-r", "/usr", "existing", "--path", "local/bin"],
        standalone_mode=False,
    ) == Path("/usr/local/bin/overwritten")


def test_add_commands_dict() -> None:
    class CLI(feud.Group, invoke_without_command=True):
        @staticmethod
        @feud.alias(root="-r")
        def __main__(ctx: click.Context, *, root: Path = Path(".")) -> None:
            ctx.obj = {"root": root}
            return root

        @staticmethod
        def existing(ctx: click.Context, *, path: Path) -> Path:
            return ctx.obj["root"] / path

    def command(ctx: click.Context, *, path: Path) -> Path:
        return ctx.obj["root"] / path

    def _command(ctx: click.Context, *, path: Path) -> Path:
        return ctx.obj["root"] / path

    @feud.rename("renamed")
    def renamed_command(ctx: click.Context, *, path: Path) -> Path:
        return ctx.obj["root"] / path

    @feud.command
    @feud.rename("compiled-command")
    @feud.alias(path="-p")
    def compiled(ctx: click.Context, *, path: Path) -> Path:
        return ctx.obj["root"] / path

    commands = {
        "a": command,
        "b": _command,
        "c": renamed_command,
        "d": compiled,
    }

    CLI.add_commands(**commands)

    cmds = {
        "existing": "existing",
        "command": "a",
        "_command": "b",
        "renamed_command": "c",
        "compiled": "d",
    }

    # check registered commands
    assert set(CLI.__feud_commands__) == set(cmds)
    assert all(hasattr(CLI, cmd) for cmd in cmds)
    assert set(CLI.commands(name=True)) == set(cmds.values())

    # test various commands
    for cmd in cmds.values():
        assert CLI(
            ["-r", "/usr", cmd, "--path", "local/bin"], standalone_mode=False
        ) == Path("/usr/local/bin")

    # test command with aliased option
    assert CLI(
        ["-r", "/usr", "d", "-p", "local/bin"], standalone_mode=False
    ) == Path("/usr/local/bin")

    # override existing command
    def existing(ctx: click.Context, *, path: Path) -> Path:
        return ctx.obj["root"] / path / "overwritten"

    CLI.add_commands(existing=existing)

    # check command is registered
    assert CLI.__feud_commands__ == [*list(cmds)[1:], "existing"]
    assert hasattr(CLI, "existing")
    assert set(CLI.commands(name=True)) == set(cmds.values())

    # check command was actually overwritten
    assert CLI(
        ["-r", "/usr", "existing", "--path", "local/bin"],
        standalone_mode=False,
    ) == Path("/usr/local/bin/overwritten")
