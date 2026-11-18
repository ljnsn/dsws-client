## v1.1.4 (2026-11-18)

### 🐛🚑️ Fixes

- switch to httpx2
- require at least python3.10

### build

- **deps**: bump astral-sh/setup-uv from 3 to 4 (#152)
- **deps**: bump codecov/codecov-action from 3 to 5 (#151)

### 💚👷 CI & Build

- add uv extra requirement
- **deps**: bump actions/setup-python from 6 to 7
- **deps**: bump actions/cache from 5 to 6
- **deps**: bump actions/checkout from 6 to 7
- **deps**: bump codecov/codecov-action from 6 to 7
- **deps**: bump codecov/codecov-action from 5 to 6
- fix publish workflow
- add python 3.13 and 3.14 to test matrix
- **deps**: bump actions/checkout from 5 to 6 (#159)
- **deps**: bump actions/cache from 4 to 5 (#160)
- **deps**: bump astral-sh/setup-uv from 5 to 7 (#158)
- **deps**: bump actions/setup-python from 5 to 6 (#157)
- **deps**: bump actions/checkout from 4 to 5 (#156)
- **dependabot**: add message (#154)

### 🔧🔨📦️ Configuration, Scripts, Packages

- switch to uv build backend
- **uv**: move to new `dependency-groups`
- **ruff**: remove and rename deprecated rules
- switch to uv (#149)

### 🙈 Ignore

- ignore local mise

### 🚨 Linting

- sort imports

### 🧑‍💻 Developer Experience

- add copier template (#150)

### 🧹 chore

- bump all deps
- ignore local configs

## v1.1.3 (2024-10-18)

### 🐛🚑️ Fixes

- add ds instrument len

### 📌➕⬇️➖⬆️ Dependencies

- all

### 🔧🔨📦️ Configuration, Scripts, Packages

- **pre-commit**: autoupdate

## v1.1.2 (2024-05-02)

### 🐛🚑️ Fixes

- key of KVPair can be None (#147)

## v1.1.1 (2024-04-30)

### 🐛🚑️ Fixes

- add concurrent_requests arg (#146)

## v1.1.0 (2024-04-30)

### ✨ Features

- add methods to iterate over parsed responses (#145)

## v1.0.0 (2024-04-28)

### 🐛🚑️ Fixes

- **parse**: don't return errors for all dates (#142)
- import from typing for 38
- simplify client

### ♻️  Refactorings

- **client**: drop threaded arg
- **client**: split off prep request
- httpx (#138)
- switch to msgspec (#136)

### ⚡️ Performance

- concurrent fetch all (#139)
- **client**: use itertools instead of loop

### 💚👷 CI & Build

- set corrent env vars for pdm

### 📌➕⬇️ ➖⬆️  Dependencies

- cz-conventional-gitmoji

### 📝💡 Documentation

- **client**: docstring convention (#144)
- **client**: client docstring (#140)

### 🔥⚰️  Clean up

- **config**: client args

### 🔧🔨📦️ Configuration, Scripts, Packages

- **commitizen**: annotate tags
- move commitizen to dev dependencies
- **test**: use coverage (#143)

## v0.2.5 (2024-04-28)

### 🐛🚑️ Fixes

- **scripts**: publish command

## v0.2.4 (2024-04-28)

### 🐛🚑️ Fixes

- move commitizen to dev deps (#137)

### 💚👷 CI & Build

- use different token for dependabot checkout (#116)
- add back tests on 3.12

### 🔧🔨📦️ Configuration, Scripts, Packages

- **ruff**: adapt to 0.2.0

### 🚨 Linting

- conform to new black standard

## v0.2.3 (2024-01-30)

### 🐛🚑️ Fixes

- python312 support

### 📌➕⬇️ ➖⬆️  Dependencies

- **dev**: add pre-commit dev dependency

### 🔧🔨📦️ Configuration, Scripts, Packages

- update lockfile

### 🧑‍💻 Developer Experience

- add .editorconfig

## v0.2.2 (2024-01-24)

### 🐛🚑️ Fixes

- use python 3.11 in deploy workflow

## v0.2.1 (2024-01-23)

### 🐛🚑️ Fixes

- skip completely empty responses

### build

- **deps**: bump actions/cache from 3 to 4
- **deps**: bump actions/setup-python from 4 to 5
- **deps**: bump actions/checkout from 3 to 4

### 🎨🏗️ Style & Architecture

- yaml beautify

### 💚👷 CI & Build

- **pythonpackage**: don't explicitly check cache hit - downloads should still be cached
- **pre-commit**: set ruff extend-fixable
- add macos to matrix

### 📌➕⬇️ ➖⬆️  Dependencies

- bump ruff to latest

### 🚨 Linting

- ignore too many args

## v0.2.0 (2023-05-02)

### ✨ Features

- parse currencies to meta

### ♻️  Refactorings

- rename to parse_response and expose at top level

### ✅🤡🧪 Tests

- add more tests for parsing
- move response fixtures to conftest

## v0.1.1 (2023-05-02)

### 🐛🚑️ Fixes

- make cz-gitmoji a dev dependency

### 💚👷 CI & Build

- **github**: add github actions

### 📌➕⬇️ ➖⬆️  Dependencies

- **deps-dev**: bump ruff from 0.0.263 to 0.0.264
- fix missing black dependency
