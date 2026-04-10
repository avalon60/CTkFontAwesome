#!/usr/bin/env bash
# Author: Clive Bostock
# Date: 2026-04-10
# Description: Install a CTkFontAwesome wheel into a scratch virtualenv and run a small API smoke test.

set -euo pipefail

# shellcheck source=utils/common.sh
source "$(dirname "$0")/common.sh"

usage() {
  cat <<'EOF'
Usage:
  ./utils/test_wheel_install.sh [python-version] [wheel-path]

Examples:
  ./utils/test_wheel_install.sh
  ./utils/test_wheel_install.sh 3.12.0
  ./utils/test_wheel_install.sh 3.12.0 dist/ctkfontawesome-0.6.0-py3-none-any.whl

Behaviour:
  - uses the current python3/python on PATH by default
  - uses pyenv if a Python version is supplied
  - creates a scratch virtualenv under /tmp
  - installs the selected wheel into that virtualenv
  - runs a small CTkFontAwesome smoke test:
      * import ctkfontawesome
      * print version and icon count
      * validate icon_to_svg("facebook")
      * print category metadata counts
  - leaves the scratch environment in place for manual follow-on testing

Wheel selection:
  - if [wheel-path] is supplied, that file is used
  - otherwise the script looks for the newest *.whl in ./dist
EOF
}

if [ "${1:-}" = "-h" ] || [ "${1:-}" = "--help" ]; then
  usage
  exit 0
fi

if [ $# -gt 2 ]; then
  usage
  exit 1
fi

run_from_project_root "$0"

PYTHON_VERSION="${1:-}"
WHEEL_PATH="${2:-}"

if [ -n "${PYTHON_VERSION}" ]; then
  if ! command -v pyenv >/dev/null 2>&1; then
    echo "ERROR: pyenv is not available on PATH."
    exit 1
  fi

  if ! pyenv prefix "${PYTHON_VERSION}" >/dev/null 2>&1; then
    echo "ERROR: Python ${PYTHON_VERSION} is not installed in pyenv."
    echo "Install it with: pyenv install ${PYTHON_VERSION}"
    exit 1
  fi
fi

if [ -z "${PYTHON_VERSION}" ] && [ -z "${WHEEL_PATH}" ] && [ $# -eq 1 ] && [ -f "${1}" ]; then
  WHEEL_PATH="${1}"
  PYTHON_VERSION=""
fi

if [ -z "${WHEEL_PATH}" ]; then
  WHEEL_PATH="$(find ./dist -maxdepth 1 -type f -name '*.whl' -printf '%T@ %p\n' | sort -nr | head -1 | cut -d ' ' -f2-)"
fi

if [ -z "${WHEEL_PATH}" ]; then
  echo "ERROR: No wheel found under ./dist."
  echo "Build one first with: poetry build --format wheel"
  exit 1
fi

if [ ! -f "${WHEEL_PATH}" ]; then
  echo "ERROR: Wheel not found: ${WHEEL_PATH}"
  exit 1
fi

WHEEL_PATH="$(realpath_compat "${WHEEL_PATH}")"
STAMP="$(date +%Y%m%d-%H%M%S)"
SCRATCH_ROOT="/tmp/ctkfontawesome-wheel-test-${PYTHON_VERSION:-default}-${STAMP}"
VENV_DIR="${SCRATCH_ROOT}/venv"

mkdir -p "${SCRATCH_ROOT}"

if [ -n "${PYTHON_VERSION}" ]; then
  export PYENV_VERSION="${PYTHON_VERSION}"
  PYTHON_BIN="pyenv exec python"
  PYTHON_LABEL="pyenv Python: ${PYTHON_VERSION}"
else
  if command -v python3 >/dev/null 2>&1; then
    PYTHON_BIN="python3"
  elif command -v python >/dev/null 2>&1; then
    PYTHON_BIN="python"
  else
    echo "ERROR: Neither python3 nor python is available on PATH."
    exit 1
  fi
  PYTHON_LABEL="$(${PYTHON_BIN} --version 2>&1)"
fi

echo "Using ${PYTHON_LABEL}"
echo "Creating scratch environment: ${VENV_DIR}"
${PYTHON_BIN} -m venv "${VENV_DIR}"

# shellcheck disable=SC1091
source "${VENV_DIR}/bin/activate"

echo "Upgrading pip..."
python -m pip install --upgrade pip

echo "Installing wheel: ${WHEEL_PATH}"
python -m pip install "${WHEEL_PATH}"

echo "Running smoke checks..."
python - <<'PY'
import ctkfontawesome

print("Installed version:", ctkfontawesome.__version__)
print("Icon count:", len(ctkfontawesome.icon_names()))
print("Category count:", len(ctkfontawesome.category_names()))

svg = ctkfontawesome.icon_to_svg("facebook")
if not svg.startswith("<svg "):
    raise SystemExit("ERROR: icon_to_svg('facebook') did not return SVG markup.")

print("facebook categories:", ctkfontawesome.icon_categories("facebook"))
print("code icons sample:", ctkfontawesome.icons_in_category("code")[:5])
PY

echo
echo "Wheel smoke test passed."
echo "Scratch root : ${SCRATCH_ROOT}"
echo "Virtualenv   : ${VENV_DIR}"
echo
echo "Activate it with:"
echo "  source ${VENV_DIR}/bin/activate"
echo
echo "Installed package summary:"
python -m pip show ctkfontawesome || true
