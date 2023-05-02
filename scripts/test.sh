#!/usr/bin/env bash

set -e
set -x

poetry run pytest --cov dsws_client --cov-report xml tests
