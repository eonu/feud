<p align="center">
  <h1 align="center">
    Feud
  </h1>
  <p align="center"><b>Not all arguments are bad.</b></p>
</p>

<img src="https://svgur.com/i/zk4.svg" align="right" width="100px">

<p align="center">
  <em>Build powerful CLIs with simple idiomatic Python, driven by type hints.</em>
</p>

<p align="center">
  <div align="center">
    <a href="https://pypi.org/project/feud">
      <img src="https://img.shields.io/pypi/v/feud?logo=pypi&style=flat-square" alt="PyPI"/>
    </a>
    <a href="https://pypi.org/project/feud">
      <img src="https://img.shields.io/pypi/pyversions/feud?logo=python&style=flat-square" alt="PyPI - Python Version"/>
    </a>
    <a href="https://feud.readthedocs.io/en/latest">
      <img src="https://img.shields.io/readthedocs/feud.svg?logo=read-the-docs&style=flat-square" alt="Read The Docs - Documentation"/>
    </a>
    <a href="https://coveralls.io/github/eonu/feud">
      <img src="https://img.shields.io/coverallsCoverage/github/eonu/feud?logo=coveralls&style=flat-square" alt="Coveralls - Coverage"/>
    </a>
    <a href="https://raw.githubusercontent.com/eonu/feud/master/LICENSE">
      <img src="https://img.shields.io/pypi/l/feud?style=flat-square" alt="PyPI - License"/>
    </a>
  </div>
</p>

<p align="center">
  <sup>
    <a href="#about">About</a> ·
    <a href="#features">Features</a> ·
    <a href="#installation">Installation</a> ·
    <a href="#build-status">Build status</a> ·
    <a href="#documentation">Documentation</a> ·
    <a href="#related-projects">Related projects</a> ·
    <a href="#contributing">Contributing</a> ·
    <a href="#licensing">Licensing</a>
  </sup>
</p>

---

## About

> [!WARNING]  
> _Writing command-line interfaces can get messy!_

It is not uncommon for CLIs to consist of many commands,
subcommands, arguments, options and aliases, on
top of dealing with other aspects such as documentation and input types when
it comes to argument parsing.

Designing such an interface can quickly spiral into chaos without the help of
an intuitive CLI builder.

**Feud builds on [Click](https://click.palletsprojects.com/en/8.1.x/) for
argument parsing, along with [Pydantic](https://docs.pydantic.dev/latest/)
for typing, to make CLI building a breeze.**

## Features

### Simplicity

Click is often considered the defacto command-line building utility for Python –
offering far more functionality and better ease-of-use than the standard
library's [`argparse`](https://docs.python.org/3/library/argparse.html).
Despite this, for even the simplest of CLIs, code written using Click can be
somewhat verbose and often requires frequently looking up documentation.

Consider the following example command for serving local files on a HTTP server.

**In red is a typical Click implementation, and in green is the Feud equivalent.**

```diff
- import click
+ import feud
+ from typing import Literal

- @click.command
+ @feud.command
- @click.argument("port", type=int, help="Server port.")
- @click.option("--watch/--no-watch", type=bool, default=True, help="Watch source code for changes.")
- @click.option("--env", type=click.Choice(["dev", "prod"]), default="dev", help="Environment mode.")
- def serve(port, watch, env):
+ def serve(port: int, *, watch: bool = True, env: Literal["dev", "prod"] = "dev"):
-     """Start a local HTTP server."""
+     """Start a local HTTP server.\f
+
+     Parameters
+     ----------
+     port:
+         Server port.
+     watch:
+         Watch source code for changes.
+     env:
+         Environment mode.
+     """
```

Let's take a closer look at the Feud implementation.

<table>
<tr>
<td>

**Example**: Command for running a HTTP web server.

</td>
</tr>
<tr>
<td>

```python
# serve.py

import feud
from typing import Literal

def serve(port: int, *, watch: bool = True, env: Literal["dev", "prod"] = "dev"):
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

if __name__ == "__main__":
    feud.run(serve)
```

</td>
</tr>
<tr>
<td>
<details>
  <summary>
    <b>Click here to view the generated help screen.</b>
  </summary>
<p>

Help screen for the `serve` command.

```console
$ python serve.py --help

 Usage: serve.py [OPTIONS] PORT

 Start a local HTTP server.

╭─ Arguments ────────────────────────────────────────────────────────╮
│ *  PORT    INTEGER  [required]                                     │
╰────────────────────────────────────────────────────────────────────╯
╭─ Options ──────────────────────────────────────────────────────────╮
│ --watch/--no-watch                Watch source code for changes.   │
│                                   [default: watch]                 │
│ --env                 [dev|prod]  Environment mode. [default: dev] │
│ --help                            Show this message and exit.      │
╰────────────────────────────────────────────────────────────────────╯
```

</p>
</details>
</td>
</tr>
<tr>
<td>
<details>
  <summary>
    <b>Click here to see usage examples.</b>
  </summary>
<p>

- `python serve.py 8080`
- `python serve.py 3000 --watch --env dev`
- `python serve.py 4567 --no-watch --env prod`

</p>
</details>
</td>
</tr>
</table>

The core design principle behind Feud is to make it as easy as possible
for even beginner Python developers to quickly create sophisticated CLIs.

The above function is written in idiomatic Python, adhering to language
standards and using basic core language features such as type hints and
docstrings to declare all of the relevant information about the CLI,
but relying on Feud to carry out the heavy lifting of converting these
language elements into a fully-fledged CLI.

#### Grouping commands

While a single command is often all that you need, Feud makes it
straightforward to logically group together related commands into a _group_
represented by a class with commands defined within it.

<table>
<tr>
<td>

**Example**: Commands for creating, deleting and listing blog posts.

</td>
</tr>
<tr>
<td>

```python
# post.py

import feud
from datetime import date

class Post(feud.Group):
    """Manage blog posts."""

    def create(id: int, *, title: str, desc: str | None = None):
        """Create a blog post."""

    def delete(*ids: int):
        """Delete blog posts."""

    def list(*, between: tuple[date, date] | None = None):
        """View all blog posts, optionally filtering by date range."""

if __name__ == "__main__":
    feud.run(Post)
```

</td>
</tr>
<tr>
<td>
<details>
  <summary>
    <b>Click here to view the generated help screen.</b>
  </summary>
<p>

Help screen for the `post` group.

```console
$ python post.py --help

 Usage: post.py [OPTIONS] COMMAND [ARGS]...

 Manage blog posts.

╭─ Options ──────────────────────────────────────────────────────────╮
│ --help      Show this message and exit.                            │
╰────────────────────────────────────────────────────────────────────╯
╭─ Commands ─────────────────────────────────────────────────────────╮
│ create   Create a blog post.                                       │
│ delete   Delete blog posts.                                        │
│ list     View all blog posts, optionally filtering by date range.  │
╰────────────────────────────────────────────────────────────────────╯
```

Help screen for the `list` command within the `post` group.

```console
$ python post.py list --help

 Usage: post.py list [OPTIONS]

 View all blog posts, optionally filtering by date range.

╭─ Options ──────────────────────────────────────────────────────────╮
│ --between    <DATE DATE>...                                        │
│ --help                       Show this message and exit.           │
╰────────────────────────────────────────────────────────────────────╯
```

</p>
</details>
</td>
</tr>
<tr>
<td>
<details>
  <summary>
    <b>Click here to see usage examples.</b>
  </summary>
<p>

- `python post.py create 1 --title "My First Post"`
- `python post.py create 2 --title "My First Detailed Post" --desc "Hi!"`
- `python post.py delete 1 2`
- `python post.py list`
- `python post.py list --between 2020-01-30 2021-01-30`

</p>
</details>
</td>
</tr>
</table>

Alternatively, if you already have some functions defined that you would like
to run as commands, you can simply provide them to `feud.run` and it will
automatically generate and run a group with those commands.

```python
import feud
from datetime import date

def create_post(id: int, *, title: str, desc: str | None = None):
    """Create a blog post."""

def delete_post(*ids: int):
    """Delete blog posts."""

def list_posts(*, between: tuple[date, date] | None = None):
    """View all blog posts, optionally filtering by date range."""

if __name__ == "__main__":
    feud.run([create_post, delete_post, list_posts])
```

You can also use a `dict` to rename the generated commands:

```python
feud.run({"create": create_post, "delete": delete_post, "list": list_posts})
```

As you can see, building a CLI using Feud does not require learning many new
magic methods or a domain-specific language – you can just use the simple
Python you know and ❤️!

#### Registering command sub-groups

Groups can be registered as sub-groups under other groups. This is a common
pattern in CLIs, allowing for interfaces packed with lots of functionality,
but still organized in a sensible way.

<table>
<tr>
<td>

**Example**: CLI with the following structure for running and managing a blog.

- **`blog`**: Group to manage and serve a blog.
  - `serve`: Command to run the blog HTTP server.
  - **`post`**: Sub-group to manage blog posts.
    - `create`: Command to create a blog post.
    - `delete`: Command to delete blog posts.
    - `list`: Command to view all blog posts.

</td>
</tr>
<tr>
<td>

```python
# blog.py

import feud
from datetime import date

class Blog(feud.Group):
    """Manage and serve a blog."""

    def serve(port: int, *, watch: bool = True, env: Literal["dev", "prod"] = "dev"):
        """Start a local HTTP server."""

class Post(feud.Group):
    """Manage blog posts."""

    def create(id: int, *, title: str, desc: str | None = None):
        """Create a blog post."""

    def delete(*ids: int):
        """Delete blog posts."""

    def list(*, between: tuple[date, date] | None = None):
        """View all blog posts, optionally filtering by date range."""

Blog.register(Post)

if __name__ == "__main__":
    feud.run(Blog)
```

</td>
</tr>
<tr>
<td>

<details>
  <summary>
    <b>Click here to view the generated help screen.</b>
  </summary>
<p>

Help screen for the `blog` group.

```console
$ python blog.py --help

 Usage: blog.py [OPTIONS] COMMAND [ARGS]...

 Manage and serve a blog.

╭─ Options ──────────────────────────────────────────────────────────╮
│ --help      Show this message and exit.                            │
╰────────────────────────────────────────────────────────────────────╯
╭─ Commands ─────────────────────────────────────────────────────────╮
│ post         Manage blog posts.                                    │
│ serve        Start a local HTTP server.                            │
╰────────────────────────────────────────────────────────────────────╯
```

Help screen for the `serve` command in the `blog` group.

```console
$ python blog.py serve --help

 Usage: blog.py serve [OPTIONS] PORT

 Start a local HTTP server.

╭─ Arguments ────────────────────────────────────────────────────────╮
│ *  PORT    INTEGER  [required]                                     │
╰────────────────────────────────────────────────────────────────────╯
╭─ Options ──────────────────────────────────────────────────────────╮
│ --watch/--no-watch                [default: watch]                 │
│ --env                 [dev|prod]  [default: dev]                   │
│ --help                            Show this message and exit.      │
╰────────────────────────────────────────────────────────────────────╯
```

Help screen for the `post` sub-group in the `blog` group.

```console
$ python blog.py post --help

 Usage: blog.py post [OPTIONS] COMMAND [ARGS]...

 Manage blog posts.

╭─ Options ──────────────────────────────────────────────────────────╮
│ --help      Show this message and exit.                            │
╰────────────────────────────────────────────────────────────────────╯
╭─ Commands ─────────────────────────────────────────────────────────╮
│ create   Create a blog post.                                       │
│ delete   Delete blog posts.                                        │
│ list     View all blog posts, optionally filtering by date range.  │
╰────────────────────────────────────────────────────────────────────╯
```

Help screen for the `list` command within the `post` sub-group.

```console
$ python blog.py post list --help

 Usage: blog.py post list [OPTIONS]

 View all blog posts, optionally filtering by date range.

╭─ Options ──────────────────────────────────────────────────────────╮
│ --between    <DATE DATE>...                                        │
│ --help                       Show this message and exit.           │
╰────────────────────────────────────────────────────────────────────╯
```

</p>
</details>

</td>
</tr>
<tr>
<td>
<details>
  <summary>
    <b>Click here to see usage examples.</b>
  </summary>
<p>

- `python blog.py serve 8080 --no-watch --env prod`
- `python blog.py post create 1 --title "My First Post!"`
- `python blog.py post list --between 2020-01-30 2021-01-30`

</p>
</details>
</td>
</tr>
</table>

### Powerful typing

Feud is powered by [Pydantic](https://docs.pydantic.dev/latest/) – a
validation library with extensive support for many data types, including:

- simple types such as integers and dates,
- complex types such as emails, IP addresses, file/directory paths, database
  connection strings,
- constrained types (e.g. positive/negative integers or past/future dates).

[`pydantic-extra-types`](https://github.com/pydantic/pydantic-extra-types) is
an optional dependency offering additional types such as:

- country names,
- payment card numbers,
- phone numbers,
- colours,
- latitude/longitude.

Custom annotated types with user-defined validation functions can also be
defined with Pydantic.

<table>
<tr>
<td>

**Example**: Command for generating audio samples from text prompts using
a machine learning model, and storing produced audio files in an output
directory.

</td>
</tr>
<tr>
<td>

```python
# generate.py

import feud
from pydantic import FilePath, DirectoryPath, conlist, constr

def generate(
    prompts: conlist(constr(max_length=12), min_length=1, max_length=5),
    *,
    model: FilePath,
    output: DirectoryPath,
):
    """Generates audio from prompts using a trained model."""

if __name__ == "__main__":
    feud.run(generate)
```

</td>
</tr>
<tr>
<td>
<details>
  <summary>
    <b>Click here to view the generated help screen.</b>
  </summary>
<p>

Help screen for the `generate` command.

```console
$ python generate.py --help

 Usage: generate.py [OPTIONS] [PROMPTS]...

 Generates audio from prompts using a trained model.

╭─ Arguments ────────────────────────────────────────────────────────╮
│ PROMPTS    TEXT                                                    │
╰────────────────────────────────────────────────────────────────────╯
╭─ Options ──────────────────────────────────────────────────────────╮
│ *  --model     FILE       [required]                               │
│ *  --output    DIRECTORY  [required]                               │
│    --help                 Show this message and exit.              │
╰────────────────────────────────────────────────────────────────────╯
```

</p>
</details>
</td>
</tr>
<tr>
<td>
<details>
  <summary>
    <b>Click here to see usage examples.</b>
  </summary>
<p>

If we run the script without prompts, we get an error that at least one prompt
must be provided.

```console
$ python generate.py --model models/real_model.pt --output audio/

 Usage: generate.py [OPTIONS] [PROMPTS]...

 Try 'generate.py --help' for help
╭─ Error ──────────────────────────────────────────────────────────────────────╮
│ 1 validation error for command 'generate'                                    │
│ [PROMPTS]...                                                                 │
│   List should have at least 1 item after validation, not 0 [input_value=()]  │
╰──────────────────────────────────────────────────────────────────────────────╯
```

If we provide a prompt longer than 12 characters, we also get an error.

```console
$ python generate.py "dog barking" "cat meowing" "fish blubbing" --model models/real_model.pt --output audio/

 Usage: generate.py [OPTIONS] [PROMPTS]...

 Try 'generate.py --help' for help
╭─ Error ──────────────────────────────────────────────────────────────────────╮
│ 1 validation error for command 'generate'                                    │
│ [PROMPTS]... [2]                                                             │
│   String should have at most 12 characters [input_value='fish blubbing']     │
╰──────────────────────────────────────────────────────────────────────────────╯
```

`FilePath` indicates that the file must already exist, so we get an error if we
provide a non-existent file.

```console
$ python generate.py "dog barking" "cat meowing" --model models/fake_model.pt

 Usage: generate.py [OPTIONS] [PROMPTS]...

 Try 'generate.py --help' for help
╭─ Error ──────────────────────────────────────────────────────────────────────╮
│ Invalid value for '--model': File 'models/fake_model.pt' does not exist.     │
╰──────────────────────────────────────────────────────────────────────────────╯
```

`DirectoryPath` indicates that the path must be a directory, so we
get an error if we provide a file.

```console
$ python generate.py "dog barking" "cat meowing" --output audio.txt

 Usage: generate.py [OPTIONS] [PROMPTS]...

 Try 'generate.py --help' for help
╭─ Error ──────────────────────────────────────────────────────────────────────╮
│ Invalid value for '--output': Directory 'audio.txt' is a file.               │
╰──────────────────────────────────────────────────────────────────────────────╯
```

</p>
</details>
</td>
</tr>
</table>

### Highly configurable and extensible

> [!IMPORTANT]  
> _Feud is **not** the new Click_ - it is an extension of Click and directly depends it.

While designed to be simpler than Click, this comes with the trade-off that
Feud is also more opinionated than Click and only directly implements a subset
of its functionality.

However, Feud was designed to allow for Click to seamlessly slot in whenever
manual overrides are necessary.

<table>
<tr>
<td>

**Example**: Use [`click.password_option`](https://click.palletsprojects.com/en/8.1.x/api/#click.password_option)
to securely prompt the user for a password, but still validate based on the
type hint (length should be ≥ 10 characters).

</td>
</tr>
<tr>
<td>

```python
# login.py

import feud
from feud import click
from pydantic import constr

@click.password_option("--password", help="The user's password (≥ 10 characters).")
def login(*, username: str, password: constr(min_length=10)):
    """Log in as a user.\f

    Parameters
    ----------
    username:
        The user's username.
    """

if __name__ == "__main__":
    feud.run(login)
```

</td>
</tr>
<tr>
<td>
<details>
  <summary>
    <b>Click here to view the generated help screen.</b>
  </summary>
<p>

Help screen for the `login` command.

```console
$ python login.py --help

 Usage: login.py [OPTIONS]

 Log in as a user.

╭─ Options ──────────────────────────────────────────────────────────╮
│ *  --username    TEXT  The user's username. [required]             │
│    --password    TEXT  The user's password (≥ 10 characters).      │
│    --help              Show this message and exit.                 │
╰────────────────────────────────────────────────────────────────────╯
```

</p>
</details>
</td>
</tr>
<tr>
<td>
<details>
  <summary>
    <b>Click here to see usage examples.</b>
  </summary>
<p>

```console
$ python login.py --username alice

Password: ***
Repeat for confirmation: ***

 Usage: login.py [OPTIONS]

 Try 'login.py --help' for help
╭─ Error ────────────────────────────────────────────────────────────╮
│ 1 validation error for command 'login'                             │
│ --password                                                         │
│   String should have at least 10 characters [input_value=hidden]   │
╰────────────────────────────────────────────────────────────────────╯
```

</p>
</detail>
</td>
</tr>
</table>

## Installation

You can install Feud using `pip`.

The latest stable version of Feud can be installed with the following command.

```console
pip install "feud[all]"
```

This installs Feud with the optional dependencies:

- [`rich-click`](https://github.com/ewels/rich-click) (can install individually with `pip install "feud[rich]"`)<br/>
  _Provides improved formatting for CLIs produced by Feud._
- [`pydantic-extra-types`](https://github.com/pydantic/pydantic-extra-types) (can install individually with `pip install "feud[extra-types]"`)<br/>
  _Provides additional types that can be used as type hints for Feud commands._
- [`email-validator`](https://github.com/JoshData/python-email-validator) (can install individually with `pip install "feud[email]"`)<br/>
  _Provides Pydantic support for email validation._

To install Feud without any optional dependencies, simply run `pip install feud`.

> [!CAUTION]
> Feud **will break** if used with postponed type hint evaluation ([PEP563](https://peps.python.org/pep-0563/)), i.e.:
>
> ```python
> from __future__ import annotations
> ```
>
> This is because Feud relies on type hint evaluation in order to determine the expected input type for command parameters.

### Improved formatting with Rich

Below is a comparison of Feud with and without `rich-click`.

<table>
<tr>
<th>
With Rich-formatted output
</th>
<th>
Without Rich-formatted output
</th>
</tr>
<tr>
<td>
<img src="/docs/source/_static/images/readme/help-rich.png"/>
</td>
<td>
<img src="/docs/source/_static/images/readme/help-no-rich.png"/>
</td>
</tr>
<tr>
<td>
<img src="/docs/source/_static/images/readme/error-rich.png"/>
</td>
<td>
<img src="/docs/source/_static/images/readme/error-no-rich.png"/>
</td>
</tr>
</table>

## Build status

| `master`                                                                                                                                                                                       | `dev`                                                                                                                                                                                            |
| ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| [![CircleCI Build (Master)](https://img.shields.io/circleci/build/github/eonu/feud/master?logo=circleci&style=flat-square)](https://app.circleci.com/pipelines/github/eonu/feud?branch=master) | [![CircleCI Build (Development)](https://img.shields.io/circleci/build/github/eonu/feud/dev?logo=circleci&style=flat-square)](https://app.circleci.com/pipelines/github/eonu/feud?branch=master) |

## Documentation

- [API reference](https://docs.feud.wiki):
  Library documentation for public modules, classes and functions.

<!--
- [Official website](https://feud.wiki):
  High level information about the package.
- [User guide](https://feud.wiki/guide):
  Detailed walkthrough of features, with examples of both simple and complex
  usage patterns.
-->

## Related projects

Feud either relies heavily on, or was inspired by the following
packages. It would be greatly appreciated if you also supported the below
maintainers and the work they have done that Feud has built upon.

### [Click](https://github.com/pallets/click)

<sup>

by [@pallets](https://github.com/pallets)

</sup>

> _Click is a Python package for creating beautiful command line interfaces in a composable way with as little code as necessary._

Feud is essentially a wrapper around Click that takes classes and functions
with type hints and intelligently 'compiles' them into a ready-to-use Click
generated CLI.

### [Rich Click](https://github.com/ewels/rich-click)

<sup>

by [@ewels](https://github.com/ewels)

</sup>

> _Richly rendered command line interfaces in click._

A shim around Click that renders help output nicely using
[Rich](https://github.com/Textualize/rich).

### [Pydantic](https://github.com/pydantic/pydantic)

<sup>

by [@samuelcolvin](https://github.com/samuelcolvin)

</sup>

> _Data validation using Python type hints._

Pydantic is a validation package that makes it easy to declaratively validate
input data based on type hints.

The package offers support for common standard library types (e.g. `int`,
`float`, `str`, `date`/`datetime`), plus more complex types which can also be
used as type hints in Feud commands for input validation.

### [Typer](https://github.com/tiangolo/typer)

<sup>

by [@tiangolo](https://github.com/tiangolo)

</sup>

> _Typer is a library for building CLI applications that users will love using and developers will love creating._

Typer shares a similar ideology to Feud, in that building CLIs should be
simple and not require learning new functions or constantly referring to
library documentation. Typer is also based on Click.

One source of motivation for creating Feud is that at the time of creation,
Pydantic was not yet supported as a type system for Typer. It is worth
noting that Pydantic as an optional dependency is on Typer's [tentative roadmap](https://github.com/tiangolo/typer/issues/678),
so it will be interesting to see how the implementation compares to Feud!

Typer is a more complete library for building CLIs overall, but currently
lacks support for more complex types such as those offered by Pydantic.

## Contributing

All contributions to this repository are greatly appreciated. Contribution guidelines can be found [here](/CONTRIBUTING.md).

> <img src="https://i.postimg.cc/jq3MZSTD/avatar.png" align="left"/>
> <b>We're living in an imperfect world!</b><br/>
> <sup>Feud is in a public beta-test phase, likely with <em>lots</em> of bugs. Please <a href="https://github.com/eonu/feud/issues/new/choose">leave feedback</a> if you come across anything strange!</sup>

## Licensing

Feud is released under the [MIT](https://opensource.org/licenses/MIT) license.

---

<p align="center">
  <b>Feud</b> &copy; 2023-2025, Edwin Onuonga - Released under the <a href="https://opensource.org/licenses/MIT">MIT</a> license.<br/>
  <em>Authored and maintained by Edwin Onuonga.</em>
</p>
