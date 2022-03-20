#!/usr/bin/env bash

ROOT="$(git rev-parse --show-toplevel)"

poetry plugin add poetry-export-plugin>/dev/null

poetry export --with docs --with dev --without-hashes -f requirements.txt -o "${ROOT}/docs/requirements.txt"
