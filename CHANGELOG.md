# Changelog

All notable changes to this project will be documented in this file.

## [v0.2.0](https://github.com/eonu/feud/releases/tag/v0.2.0) - 2023-12-27

### Features

- add `feud.build` + move `rich_click` styling to `feud.Config` ([#123](https://github.com/eonu/feud/issues/123))

## [v0.1.6](https://github.com/eonu/feud/releases/tag/v0.1.6) - 2023-12-26

### Bug Fixes

- improve docstring parsing ([#121](https://github.com/eonu/feud/issues/121))

## [v0.1.5](https://github.com/eonu/feud/releases/tag/v0.1.5) - 2023-12-26

### Documentation

- restyle `README.md` and related projects ([#117](https://github.com/eonu/feud/issues/117))

### Features

- support argument defaults ([#114](https://github.com/eonu/feud/issues/114))
- show argument help by default + support `rich-click` overrides ([#115](https://github.com/eonu/feud/issues/115))
- expand `feud.run` object support/discovery ([#116](https://github.com/eonu/feud/issues/116))

## [v0.1.4](https://github.com/eonu/feud/releases/tag/v0.1.4) - 2023-12-22

### Bug Fixes

- update `release` task to use `version.py` ([#111](https://github.com/eonu/feud/issues/111))

### Documentation

- add `feud.run` dict/iterable examples to `README.md` ([#107](https://github.com/eonu/feud/issues/107))
- add footer to `.md` files ([#109](https://github.com/eonu/feud/issues/109))

### Features

- support `*args` and `**kwargs` ([#108](https://github.com/eonu/feud/issues/108))

## [v0.1.3](https://github.com/eonu/feud/releases/tag/v0.1.3) - 2023-12-19

### Bug Fixes

- update issues and discussions URLs ([#104](https://github.com/eonu/feud/issues/104))

### Features

- support iterables and `dict` in `feud.run` ([#105](https://github.com/eonu/feud/issues/105))

## [v0.1.2](https://github.com/eonu/feud/releases/tag/v0.1.2) - 2023-12-15

### Bug Fixes

- fix `README.md` typo ([#102](https://github.com/eonu/feud/issues/102))

## [v0.1.2rc1](https://github.com/eonu/feud/releases/tag/v0.1.2rc1) - 2023-12-15

### Bug Fixes

- fix repository issue/PR templates ([#97](https://github.com/eonu/feud/issues/97))

## [v0.1.1](https://github.com/eonu/feud/releases/tag/v0.1.1) - 2023-12-14

### Bug Fixes

- change `feud.config` from package to module ([#86](https://github.com/eonu/feud/issues/86))
- use `==` instead of `is` for `typing.Annotated` comparison ([#88](https://github.com/eonu/feud/issues/88))

### Documentation

- add postponed evaluation `README.md` disclaimer ([#92](https://github.com/eonu/feud/issues/92))
- `click.Option` intersphinx reference ([#93](https://github.com/eonu/feud/issues/93))

### Features

- add `email` extra, issue/PR templates, `version` module ([#84](https://github.com/eonu/feud/issues/84))
- add `typing.Pattern` to `feud.typing` ([#85](https://github.com/eonu/feud/issues/85))
- add metavars for `typing.Union` and literal `|` union types ([#89](https://github.com/eonu/feud/issues/89))
- add `Group.__main__()` support ([#90](https://github.com/eonu/feud/issues/90))
- add `feud.env` decorator for env. variable options ([#91](https://github.com/eonu/feud/issues/91))
- add `feud.rename` decorator ([#94](https://github.com/eonu/feud/issues/94))

### Testing

- add test for inheritance command override ([#87](https://github.com/eonu/feud/issues/87))

## [v0.1.0](https://github.com/eonu/feud/releases/tag/v0.1.0) - 2023-12-05

### Build System

- remove auto-merge `master` -> `dev` workflow ([#80](https://github.com/eonu/feud/issues/80))

### Documentation

- add configuration reference to boolean type ([#81](https://github.com/eonu/feud/issues/81))

## [v0.1.0a9](https://github.com/eonu/feud/releases/tag/v0.1.0a9) - 2023-12-05

### Build System

- dont use `git fetch --unshallow` ([#78](https://github.com/eonu/feud/issues/78))

## [v0.1.0a8](https://github.com/eonu/feud/releases/tag/v0.1.0a8) - 2023-12-05

### Build System

- hide release PRs from `CHANGELOG.md` ([#73](https://github.com/eonu/feud/issues/73))
- use `github-push-action` for auto-merge ([#75](https://github.com/eonu/feud/issues/75))
- use PAT for actions/checkout ([#76](https://github.com/eonu/feud/issues/76))

## [v0.1.0a6](https://github.com/eonu/feud/releases/tag/v0.1.0a6) - 2023-12-04

### Build System

- use `setup-git-credentials` for auto-merge workflow ([#71](https://github.com/eonu/feud/issues/71))

## [v0.1.0a5](https://github.com/eonu/feud/releases/tag/v0.1.0a5) - 2023-12-04

### Build System

- add write permissions to auto-merge workflow ([#69](https://github.com/eonu/feud/issues/69))

## [v0.1.0a4](https://github.com/eonu/feud/releases/tag/v0.1.0a4) - 2023-12-04

### Build System

- add auto-merge master into dev workflow ([#67](https://github.com/eonu/feud/issues/67))

### Documentation

- add `cliff.toml` issue/release number preprocessors ([#66](https://github.com/eonu/feud/issues/66))

## [v0.1.0a3](https://github.com/eonu/feud/releases/tag/v0.1.0a3) - 2023-12-04

### Build System

- use cliff for changelog generation ([#51](https://github.com/eonu/feud/issues/51))
- correctly access changelog entry content ([#53](https://github.com/eonu/feud/issues/53))
- fix `tag-version-commit` workflow ([#55](https://github.com/eonu/feud/issues/55))
- tag in create-release-pr workflow ([#56](https://github.com/eonu/feud/issues/56))
- prefix tag with `v` ([#57](https://github.com/eonu/feud/issues/57))
- use `rickstaa/action-create-tag` to create tags ([#64](https://github.com/eonu/feud/issues/64))

## [v0.1.0a2](https://github.com/eonu/feud/releases/tag/v0.1.0a2) - 2023-12-04

### Bug Fixes

- use `actions/checkout@v4` and fix permissions ([#28](https://github.com/eonu/feud/issues/28))
- add `write-all` permissions to `create-release-pr` workflow ([#29](https://github.com/eonu/feud/issues/29))
- provide version to `auto-changelog` ([#31](https://github.com/eonu/feud/issues/31))
- fix multi-line `create-release-pr` workflow output ([#32](https://github.com/eonu/feud/issues/32))
- fetch tags in `create-release-pr` workflow ([#34](https://github.com/eonu/feud/issues/34))
- use `fetch-depth: 0` for workflow checkout ([#36](https://github.com/eonu/feud/issues/36))
- use temporary file for changelog entry ([#37](https://github.com/eonu/feud/issues/37))
- remove invalid `)` from `create-release-pr` workflow ([#38](https://github.com/eonu/feud/issues/38))
- use EOF for multi-line changelog output ([#40](https://github.com/eonu/feud/issues/40))
- silence `release.install` invoke task ([#42](https://github.com/eonu/feud/issues/42))
- remove `entry.md` from `create-release-pr` workflow ([#44](https://github.com/eonu/feud/issues/44))
- provide start/stop commit to `create-release-pr` workflow ([#46](https://github.com/eonu/feud/issues/46))

### Refactor

- remove `CHANGELOG.md` ([#48](https://github.com/eonu/feud/issues/48))

## [v0.1.0a1](https://github.com/eonu/feud/releases/tag/v0.1.0a1) - 2023-12-03

### Features

- add `semantic-pull-request` action ([#21](https://github.com/eonu/feud/issues/21))
- add `tag-version-commit` workflow ([#22](https://github.com/eonu/feud/issues/22))
- add `poetry-publish` workflow ([#24](https://github.com/eonu/feud/issues/24))
- add `action-automatic-releases` workflow ([#25](https://github.com/eonu/feud/issues/25))
- add `create-release-pr` workflow ([#26](https://github.com/eonu/feud/issues/26))

<!-- generated by git-cliff -->
