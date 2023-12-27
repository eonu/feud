# Copyright (c) 2023-2025 Feud Developers.
# Distributed under the terms of the MIT License (see the LICENSE file).
# SPDX-License-Identifier: MIT
# This source code is part of the Feud project (https://feud.wiki).

"""Generation of :py:class:`click.Group`s from Python classes,
with automatically generated :py:func:`click.Command`s defined as
methods on the class.
"""

from __future__ import annotations

import copy
import inspect
import types
import typing as t
import warnings
from collections import OrderedDict
from itertools import chain

import feud.exceptions
from feud import click
from feud._internal import _command, _metaclass
from feud.config import Config
from feud.core.command import build_command_state

__all__ = ["Group"]


class Group(metaclass=_metaclass.GroupBase):
    """Representation of a command group, compiling into a
    :py:class:`click.Group`.

    Functions defined in the class body represent commands within the group
    and are automatically decorated with :py:func:`.command`
    (if not already decorated and do not begin with an underscore).

    Groups may be registered as subgroups to another parent group.

    Similarly to providing configuration keyword arguments to
    :py:func:`.command` (directly or with a :py:class:`.Config`),
    group-level configuration can be specified when subclassing
    :py:class:`.Group`.

    >>> import feud
    >>> class CLI(feud.Group, show_help_defaults=False, name="my-cli"):
    ...     def func(*, opt: int):
    ...         pass

    Note that Click-level keyword arguments such as ``name``, which are not
    :ref:`Feud configuration parameters <configuration>`, are passed to
    :py:func:`click.group`.

    Feud configuration parameters defined on a group are automatically
    forwarded to the commands within the group, provided that the function in
    the class body is not manually decorated with
    :py:func:`.command`. In the above example, ``func`` is automatically
    wrapped with ``@feud.command(show_help_defaults=False)``.

    .. warning::

        The following function names should **NOT** be used in a group:

        - :py:func:`~compile`
        - :py:func:`~deregister`
        - :py:func:`~descendants`
        - :py:func:`~register`
        - :py:func:`~subgroups`

        See :py:func:`.rename` if you wish to define a command with one of the
        above names.
    """

    __feud_config__: t.ClassVar[Config]
    __feud_click_kwargs__: t.ClassVar[dict[str, t.Any]]
    __feud_subgroups__: t.ClassVar[list[type[Group]]]
    __feud_commands__: t.ClassVar[list[str]]

    @staticmethod
    def __new__(
        cls: type[Group], args: list[str] | None = None, /, **kwargs: t.Any
    ) -> t.Any:
        """Compile and run the group.

        Parameters
        ----------
        cls:
            :py:class:`.Group` class reference.

        args:
            Command-line arguments provided to
            :py:class:`click.Command`.

        **kwargs:
            Additional keyword arguments provided to
            :py:class:`click.Command`.

        Returns
        -------
        Output of the called :py:class:`click.Command`.

        Examples
        --------
        >>> import feud
        >>> class CLI(feud.Group):
        ...     def func(*, opt: int) -> int:
        ...         return opt
        >>> CLI(["func", "--opt", "3"], standalone_mode=False)
        3

        See Also
        --------
        .run:
            Run a command or group.
        """
        return cls.__compile__()(args, **kwargs)

    @classmethod
    def __compile__(
        cls: type[Group], *, parent: click.Group | None = None
    ) -> click.Group:
        """Compile the group into a :py:class:`click.Group`.

        .. warning::

            This is an internal function that should not be used directly,
            :py:func:`.compile` should be used instead.

        Parameters
        ----------
        parent:
            Parent :py:class:`click.Group` to attach the compiled
            group to as a subgroup.

        Returns
        -------
        The generated :py:class:`click.Group`.

        Examples
        --------
        >>> import feud, click
        >>> class CLI(feud.Group):
        ...     def func(*, opt: int) -> int:
        ...         return opt
        >>> isinstance(CLI.__compile__(), click.Group)
        True
        """
        # check for circular dependencies
        cls._check_descendants()

        # create the group
        click_group: click.Group = get_group(cls)

        # add commands to the group
        for name in cls.__feud_commands__:
            click_group.add_command(getattr(cls, name))

        # compile all subgroups
        for subgroup in cls.__feud_subgroups__:
            subgroup.__compile__(parent=click_group)

        # add the command group to the parent group if there is one
        if parent:
            parent.add_command(click_group)

        return click_group

    @classmethod
    def compile(cls: type[Group]) -> click.Group:  # noqa: A003
        """Compile the group into a :py:class:`click.Group`.

        Returns
        -------
        The generated :py:class:`click.Group`.

        Examples
        --------
        >>> import feud, click
        >>> class CLI(feud.Group):
        ...     def func(*, opt: int) -> int:
        ...         return opt
        >>> isinstance(CLI.compile(), click.Group)
        True
        """
        return cls.__compile__()

    @classmethod
    def subgroups(cls: type[Group]) -> list[type[Group]]:
        """Registered subgroups.

        Returns
        -------
        Registered subgroups.

        Examples
        --------
        >>> import feud
        >>> class A(feud.Group):
        ...     pass
        >>> class B(feud.Group):
        ...     pass
        >>> class C(feud.Group):
        ...     pass
        >>> A.register([B, C])
        >>> A.subgroups()  # doctest: +SKIP
        [<class 'group.B'>, <class 'group.C'>]

        See Also
        --------
        descendants:
            Directed acyclic graph of subgroup descendants.
        """  # noqa: D401
        return list(cls.__feud_subgroups__)

    @classmethod
    def descendants(cls: type[Group]) -> OrderedDict[type[Group], OrderedDict]:
        """Directed acyclic graph of subgroup descendants.

        Returns
        -------
        Subgroup descendants.

        Examples
        --------
        >>> import feud
        >>> class A(feud.Group):
        ...     pass
        >>> class B(feud.Group):
        ...     pass
        >>> class C(feud.Group):
        ...     pass
        >>> A.register(B)
        >>> B.register(C)
        >>> A.descendants()  # doctest: +SKIP
        OrderedDict([
            (
                <class 'group.B'>,
                OrderedDict([
                    (
                        <class 'group.C'>,
                        OrderedDict()
                    )
                ])
            )
        ])

        See Also
        --------
        subgroups:
            Registered subgroups.
        """
        return OrderedDict(
            (group, group.descendants()) for group in cls.__feud_subgroups__
        )

    @classmethod
    def _descendants(cls: type[Group]) -> t.Generator[type[Group]]:
        for group in cls.__feud_subgroups__:
            yield group
            yield from group._descendants()  # noqa: SLF001

    @classmethod
    def _check_descendants(
        cls: type[Group], __target: type[Group] | None = None, /
    ) -> None:
        group: type[Group] = __target or cls
        if cls is __target:
            msg = f"Group {cls.__name__!r} cannot be a subgroup of itself."
            raise feud.RegistrationError(msg)
        if cls in group._descendants():  # noqa: SLF001
            msg = (
                f"Group {cls.__name__!r} is a descendant subgroup of "
                f"{group.__name__!r}, causing a circular dependency."
            )
            raise feud.RegistrationError(msg)

    @classmethod
    def register(
        cls: type[Group],
        sub: type[Group] | list[type[Group]],
        /,
    ) -> None:
        """Register one or more subgroups.

        Parameters
        ----------
        sub:
            The subgroup(s) to register.

        Examples
        --------
        Registering a single subgroup.

        >>> import feud
        >>> class A(feud.Group):
        ...     pass
        >>> class B(feud.Group):
        ...     pass
        >>> A.register(B)
        >>> A.subgroups()
        [<class 'group.B'>]

        Registering multiple subgroups.

        >>> import feud
        >>> class A(feud.Group):
        ...     pass
        >>> class B(feud.Group):
        ...     pass
        >>> class C(feud.Group):
        ...     pass
        >>> A.register([B, C])
        >>> A.subgroups()
        [<class 'group.B'>, <class 'group.C'>]

        See Also
        --------
        deregister:
            Deregister one or more subgroups.
        """
        subgroups: list[type[Group]] = []

        # sub is a list of groups - check each group
        if isinstance(sub, list):
            for group in sub:
                # check if already registered or about to be registered
                if group in cls.__feud_subgroups__ + subgroups:
                    msg = (
                        f"Group {group.__name__!r} is already registered as a "
                        f"subgroup under {cls.__name__!r} and will be ignored."
                    )
                    warnings.warn(msg, RuntimeWarning, stacklevel=1)
                    continue

                # check for circular dependencies
                cls._check_descendants(group)
                subgroups.append(group)

        # sub is a group - check if already registered
        elif sub in cls.__feud_subgroups__:
            msg = (
                f"Group {sub.__name__!r} is already registered as a "
                f"subgroup under {cls.__name__!r} and will be ignored."
            )
            warnings.warn(msg, RuntimeWarning, stacklevel=1)

        # sub is an unregistered group - register it
        else:
            # check for circular dependencies
            cls._check_descendants(sub)
            subgroups.append(sub)

        # update subgroups
        cls.__feud_subgroups__.extend(subgroups)

    @classmethod
    def deregister(
        cls: type[Group],
        sub: type[Group] | list[type[Group]] | None = None,
        /,
    ) -> None:
        """Deregister one or more subgroups.

        Parameters
        ----------
        sub:
            The subgroup(s) to register.

        Examples
        --------
        Deregistering a single subgroup.

        >>> import feud
        >>> class A(feud.Group):
        ...     pass
        >>> class B(feud.Group):
        ...     pass
        >>> A.register(B)
        >>> A.subgroups()
        [<class 'group.B'>]
        >>> A.deregister(B)
        >>> A.subgroups()
        []

        Deregistering multiple subgroups.

        >>> import feud
        >>> class A(feud.Group):
        ...     pass
        >>> class B(feud.Group):
        ...     pass
        >>> class C(feud.Group):
        ...     pass
        >>> A.register([B, C])
        >>> A.subgroups()
        [<class 'group.B'>, <class 'group.C'>]
        >>> A.deregister([B, C])
        >>> A.subgroups()
        []

        See Also
        --------
        register:
            Register one or more subgroups.
        """
        subgroups: list[type[Group]] = []

        if sub:
            # sub is a list of groups - check each group
            if isinstance(sub, list):
                for group in sub:
                    # check if not registered or about to be deregistered
                    if (
                        group not in cls.__feud_subgroups__
                        or group in subgroups
                    ):
                        msg = (
                            f"Group {group.__name__!r} is not a registered "
                            f"subgroup under {cls.__name__!r} and will be "
                            "ignored."
                        )
                        warnings.warn(msg, RuntimeWarning, stacklevel=1)
                        continue
                    subgroups.append(group)
            # sub is a group - check if not registered
            elif sub not in cls.__feud_subgroups__:
                msg = (
                    f"Group {sub.__name__!r} is not a registered subgroup "
                    f"under {cls.__name__!r} and will be ignored."
                )
                warnings.warn(msg, RuntimeWarning, stacklevel=1)
            # sub is a registered group - deregister it
            else:
                subgroups.append(sub)

            # deregister subgroups
            cls.__feud_subgroups__[:] = [
                group
                for group in cls.__feud_subgroups__
                if group not in subgroups
            ]
        else:
            # deregister all subgroups
            cls.__feud_subgroups__ = []

    def __main__() -> None:  # noqa: D105
        pass

    @classmethod
    def from_dict(
        cls: type[Group],
        obj: dict[str, click.Command | type[Group] | t.Callable],
        /,
        **kwargs: t.Any,
    ) -> type[Group]:
        """Create a group from a :py:obj:`dict` of runnable objects.

        Parameters
        ----------
        obj:
            :py:obj:`dict` of runnable function, command or group objects.

        **kwargs:
            Click keywords or Feud configuration to apply:

            - ``name``: :py:obj:`str`
            - ``help``: :py:obj:`str`
            - ``epilog``: :py:obj:`str`
            - ``config``: :py:func:`.config`

        Returns
        -------
        The generated :py:class:`.Group`.
        """
        # split commands and subgroups
        commands: dict[str, click.Command | t.Callable] = obj.copy()
        subgroups: dict[str, type[Group]] = {
            k: commands.pop(k)
            for k, v in obj.items()
            if inspect.isclass(v) and issubclass(v, Group)
        }

        # rename commands (if necessary)
        funcs: list[str] = []
        for name, command in commands.copy().items():
            if isinstance(command, click.Command) and name != command.name:
                # copy command
                commands[name] = copy.copy(command)
                commands[name].name = name
            elif isinstance(command, t.Callable):
                # note commands generated by functions to be renamed later
                if name != command.__name__:
                    funcs.append(name)

        # rename groups
        for name, subgroup in subgroups.copy().items():
            group_name: str = subgroup.__feud_click_kwargs__.get("name")
            if name != group_name:
                # copy (subclass) group
                subgroups[name] = types.new_class(
                    "__feud_group__",
                    bases=(subgroup,),
                    kwds={"name": name},
                    exec_body=(
                        lambda body: body.update(
                            {"__doc__": subgroup.__doc__},  # noqa: B023
                        )
                    ),
                )

        # create group (only with commands)
        group: type[Group] = types.new_class(
            "__feud_group__",
            bases=(feud.Group,),
            kwds={k: v for k, v in kwargs.items() if v is not None},
            exec_body=(lambda body: body.update(commands)),
        )

        # rename commands generated from functions (if necessary)
        for name in funcs:
            command: click.Command = getattr(group, name)
            command.name = name

        # register subgroups (if any)
        if subgroups:
            group.register(list(subgroups.values()))

        return group

    @classmethod
    def from_iter(
        cls: type[Group],
        obj: t.Iterable[click.Command | type[Group] | t.Callable],
        /,
        **kwargs: t.Any,
    ) -> type[Group]:
        """Create a group from an iterable of runnable objects.

        Parameters
        ----------
        obj:
            :py:obj:`dict` of runnable function, command or group objects.

        **kwargs:
            Click keywords or Feud configuration to apply:

            - ``name``: :py:obj:`str`
            - ``help``: :py:obj:`str`
            - ``epilog``: :py:obj:`str`
            - ``config``: :py:func:`.config`

        Returns
        -------
        The generated :py:class:`.Group`.
        """
        # convert to list
        obj: list[click.Command | type[Group] | t.Callable] = list(obj)

        # split commands and subgroups
        commands: list[click.Command | t.Callable] = obj.copy()
        subgroups: list[type[Group]] = [
            commands.pop(i)
            for i, v in enumerate(obj)
            if inspect.isclass(v) and issubclass(v, Group)
        ]

        # function to get the name of a command or function
        def get_name(o: click.Command | t.Callable) -> str:
            return o.name if isinstance(o, click.Command) else o.__name__

        # group members
        members: dict[str, click.Command | t.Callable] = {
            get_name(cmd): cmd for cmd in commands
        }

        # create group (only with commands)
        group: type[Group] = types.new_class(
            "__feud_group__",
            bases=(feud.Group,),
            kwds={k: v for k, v in kwargs.items() if v is not None},
            exec_body=(lambda body: body.update(members)),
        )

        # register subgroups (if any)
        if subgroups:
            group.register(subgroups)

        return group

    @classmethod
    def from_module(
        cls: type[Group],
        obj: types.ModuleType,
        /,
        **kwargs: t.Any,
    ) -> type[Group]:
        """Create a group from a module of runnable function, command or
        group objects.

        Parameters
        ----------
        obj:
            Module of runnable function, command or group objects.

        **kwargs:
            Click keywords or Feud configuration to apply:

            - ``name``: :py:obj:`str`
            - ``help``: :py:obj:`str`
            - ``epilog``: :py:obj:`str`
            - ``config``: :py:func:`.config`

        Returns
        -------
        The generated :py:class:`.Group`.
        """

        def is_command(item: t.Any) -> bool:
            if inspect.isfunction(item):
                return inspect.getmodule(item) == obj
            return isinstance(item, click.Command)

        # function to get the name of a command or function
        def get_name(o: click.Command | t.Callable) -> str:
            return o.name if isinstance(o, click.Command) else o.__name__

        # split function/click.Command/click.Group from feud.Group
        commands: list[t.Callable | click.Command] = []
        groups: list[type[Group]] = []
        for item in obj.__dict__.values():
            if is_command(item):
                commands.append(item)
            elif inspect.isclass(item) and issubclass(item, Group):
                groups.append(item)

        # group members
        members: dict[str, click.Command | t.Callable] = {
            get_name(cmd): cmd for cmd in commands
        }

        # add module docstring
        members["__doc__"] = obj.__doc__

        # set group name as module name if none provided
        kwargs["name"] = kwargs.get("name") or obj.__name__.split(".")[-1]

        # discard non-root groups
        non_root: set[type[Group]] = set(
            chain.from_iterable(
                group._descendants()  # noqa: SLF001
                for group in groups
            )
        )
        subgroups = [group for group in groups if group not in non_root]

        # create group (only with commands)
        group: type[Group] = types.new_class(
            "__feud_group__",
            bases=(feud.Group,),
            kwds={k: v for k, v in kwargs.items() if v is not None},
            exec_body=(lambda body: body.update(members)),
        )

        # register subgroups (if any)
        if subgroups:
            group.register(subgroups)

        return group


def get_group(__cls: type[Group], /) -> click.Group:
    func: callable = __cls.__main__
    if isinstance(func, staticmethod):
        func = func.__func__

    state = _command.CommandState(
        config=__cls.__feud_config__,
        click_kwargs=__cls.__feud_click_kwargs__,
        is_group=True,
        aliases=getattr(func, "__feud_aliases__", {}),
        envs=getattr(func, "__feud_envs__", {}),
        names=getattr(
            func, "__feud_names__", _command.NameDict(command=None, params={})
        ),
        overrides={
            override.name: override
            for override in getattr(func, "__click_params__", [])
        },
    )

    # construct command state from signature
    build_command_state(state, func=func, config=__cls.__feud_config__)

    # generate click.Group and attach original function reference
    command = state.decorate(func)
    command.__func__ = func
    return command
