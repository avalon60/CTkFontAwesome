#!/usr/bin/env bash
# Author: Clive Bostock
# Date: 2026-04-10
# Description: Shared helper functions for CTkFontAwesome utility scripts.

set -euo pipefail

realpath_compat() {
  if command -v realpath >/dev/null 2>&1; then
    realpath "$1"
  elif command -v readlink >/dev/null 2>&1; then
    readlink -f "$1"
  else
    cd "$(dirname "$1")" && pwd
  fi
}

script_dir() {
  dirname "$(realpath_compat "$1")"
}

project_root() {
  dirname "$(script_dir "$1")"
}

find_poetry() {
  if command -v poetry >/dev/null 2>&1; then
    echo "poetry"
  elif [ -x "${HOME}/.local/bin/poetry" ]; then
    echo "${HOME}/.local/bin/poetry"
  else
    echo ""
  fi
}

require_poetry() {
  local poetry_bin
  poetry_bin="$(find_poetry)"
  if [ -z "${poetry_bin}" ]; then
    echo "ERROR: Poetry is required for this utility."
    exit 1
  fi
  echo "${poetry_bin}"
}

run_from_project_root() {
  local root
  root="$(project_root "$1")"
  cd "${root}" || {
    echo "ERROR: Failed to switch to project root: ${root}"
    exit 1
  }
}
