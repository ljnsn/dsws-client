#!/usr/bin/env bash

set -e
set -x

coverage run
coverage report
coverage xml
