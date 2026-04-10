#!/usr/bin/env bash
# Author: Clive Bostock
# Date: 2026-04-10
# Description: Bump the CTkFontAwesome minor version using Poetry and bump2version.

set -euo pipefail

# shellcheck source=utils/common.sh
source "$(dirname "$0")/common.sh"

run_from_project_root "$0"
POETRY_BIN="$(require_poetry)"

if [ "${1:-}" = "dirty" ]; then
  exec "${POETRY_BIN}" run bump2version --allow-dirty --no-commit minor
fi

exec "${POETRY_BIN}" run bump2version minor
