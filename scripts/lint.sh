#!/usr/bin/env bash

set -e
set -x

pdm run ruff dsws_client tests
pdm run black dsws_client tests --check
