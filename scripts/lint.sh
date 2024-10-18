#!/usr/bin/env bash

set -e
set -x

ruff check dsws_client tests
ruff format --check dsws_client tests
mypy dsws_client tests
