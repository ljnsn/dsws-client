#!/usr/bin/env bash

set -e
set -x

pdm run pytest --cov dsws_client --cov-report xml tests
