#!/usr/bin/env bash

set -e
set -x

pdm run coverage run
pdm run coverage report
pdm run coverage xml
