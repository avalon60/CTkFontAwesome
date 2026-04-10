#!/usr/bin/env bash
# Author: Clive Bostock
# Date: 2026-04-10
# Description: Build CTkFontAwesome release artefacts and validate the generated wheel and sdist.

set -euo pipefail

# shellcheck source=utils/common.sh
source "$(dirname "$0")/common.sh"

display_usage() {
  cat <<'EOF'
Usage:
  ./utils/package.sh -v <version_tag>
  ./utils/package.sh -V

Examples:
  ./utils/package.sh -v 0.6.0
  ./utils/package.sh -V

Use -V to print the version from pyproject.toml.
Use -v to verify the version and build release artefacts.
EOF
  exit 1
}

pyproject_version() {
  grep '^version = ' pyproject.toml | head -1 | cut -f2 -d "=" | tr -d ' "'
}

package_version() {
  grep '^__version__ = ' ctkfontawesome/__init__.py | head -1 | cut -f2 -d "=" | tr -d ' "'
}

require_archive_member() {
  local archive_path="$1"
  local member_path="$2"
  local archive_type="$3"

  if [ "${archive_type}" = "sdist" ]; then
    tar -tf "${archive_path}" | grep -Fx "${member_path}" >/dev/null
  else
    unzip -Z -1 "${archive_path}" | grep -Fx "${member_path}" >/dev/null
  fi
}

assert_archive_contains_text() {
  local archive_path="$1"
  local member_path="$2"
  local archive_type="$3"
  local expected_text="$4"

  if [ "${archive_type}" = "sdist" ]; then
    tar -xOf "${archive_path}" "${member_path}" | grep -F "${expected_text}" >/dev/null
  else
    unzip -p "${archive_path}" "${member_path}" | grep -F "${expected_text}" >/dev/null
  fi
}

verify_release_contents() {
  local version_tag="$1"
  local sdist_file="$2"
  local wheel_file="$3"
  local sdist_root="ctkfontawesome-${version_tag}"
  local sdist_members=(
    "${sdist_root}/README.md"
    "${sdist_root}/LICENSE"
    "${sdist_root}/ctkfontawesome/__init__.py"
    "${sdist_root}/ctkfontawesome/svgs.py"
  )
  local wheel_members=(
    "ctkfontawesome/__init__.py"
    "ctkfontawesome/browser.py"
    "ctkfontawesome/svgs.py"
  )

  local member
  for member in "${sdist_members[@]}"; do
    require_archive_member "${sdist_file}" "${member}" "sdist" || {
      echo "ERROR: Missing expected member in sdist: ${member}"
      exit 1
    }
  done

  for member in "${wheel_members[@]}"; do
    require_archive_member "${wheel_file}" "${member}" "wheel" || {
      echo "ERROR: Missing expected member in wheel: ${member}"
      exit 1
    }
  done

  assert_archive_contains_text "${sdist_file}" "${sdist_root}/ctkfontawesome/__init__.py" "sdist" "__version__ = \"${version_tag}\"" || {
    echo "ERROR: sdist __init__.py does not contain the expected version ${version_tag}."
    exit 1
  }

  assert_archive_contains_text "${wheel_file}" "ctkfontawesome/__init__.py" "wheel" "__version__ = \"${version_tag}\"" || {
    echo "ERROR: wheel __init__.py does not contain the expected version ${version_tag}."
    exit 1
  }

  assert_archive_contains_text "${wheel_file}" "ctkfontawesome/svgs.py" "wheel" "FA_categories =" || {
    echo "ERROR: wheel svgs.py does not contain category metadata."
    exit 1
  }
}

while getopts "v:V" options; do
  case "${options}" in
    v) VERSION_TAG="${OPTARG}" ;;
    V) SHOW_VERSION=Y ;;
    *) display_usage ;;
  esac
done

run_from_project_root "$0"
POETRY_BIN="$(require_poetry)"

if [ "${SHOW_VERSION:-N}" = "Y" ]; then
  pyproject_version
  exit 0
fi

if [ -z "${VERSION_TAG:-}" ]; then
  display_usage
fi

PYPROJECT_VERSION="$(pyproject_version)"
PACKAGE_VERSION="$(package_version)"

if [ "${VERSION_TAG}" != "${PYPROJECT_VERSION}" ]; then
  echo "ERROR: Version tag ${VERSION_TAG} does not match pyproject.toml (${PYPROJECT_VERSION})."
  exit 1
fi

if [ "${VERSION_TAG}" != "${PACKAGE_VERSION}" ]; then
  echo "ERROR: Version tag ${VERSION_TAG} does not match ctkfontawesome/__init__.py (${PACKAGE_VERSION})."
  exit 1
fi

echo "Project root    : $(pwd)"
echo "Release version : ${VERSION_TAG}"

echo "Checking Poetry metadata..."
"${POETRY_BIN}" check

echo "Building sdist and wheel..."
"${POETRY_BIN}" build

WHEEL_FILE="$(find ./dist -maxdepth 1 -type f -name "ctkfontawesome-${VERSION_TAG}-*.whl" | head -1)"
SDIST_FILE="$(find ./dist -maxdepth 1 -type f -name "ctkfontawesome-${VERSION_TAG}.tar.gz" | head -1)"

if [ -z "${WHEEL_FILE}" ] || [ -z "${SDIST_FILE}" ]; then
  echo "ERROR: Expected build artefacts were not produced in ./dist."
  exit 1
fi

echo "Verifying build contents..."
verify_release_contents "${VERSION_TAG}" "${SDIST_FILE}" "${WHEEL_FILE}"

echo
echo "Built artefacts:"
echo "  Wheel : ${WHEEL_FILE}"
echo "  Sdist : ${SDIST_FILE}"
