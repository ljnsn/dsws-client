#!/usr/bin/env bash

set -e
set -x

pdm run ruff check dsws_client tests
pdm run ruff format --check dsws_client tests
pdm run mypy dsws_client tests
