#!/usr/bin/env bash

set -e
set -x

uv build
uv publish
