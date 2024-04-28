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
