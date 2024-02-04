#!/usr/bin/env bash

set -e
set -x

poetry run ruff dsws_client tests
poetry run black dsws_client tests --check
poetry run mypy dsws_client tests
