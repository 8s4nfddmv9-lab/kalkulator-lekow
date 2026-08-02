#!/usr/bin/env bash
set -euo pipefail

FLUTTER_VERSION="${FLUTTER_VERSION:-3.44.8}"
FLUTTER_SHA256="${FLUTTER_SHA256:-672089e001571a9fbb209a495c583580c0c6c73ef98999264ba07fa93ace332d}"
INSTALL_ROOT="${FLUTTER_INSTALL_ROOT:-${HOME}/.cache/kalkulator-lekow/flutter-${FLUTTER_VERSION}}"
ARCHIVE="${RUNNER_TEMP:-/tmp}/flutter_linux_${FLUTTER_VERSION}-stable.tar.xz"
URL="https://storage.googleapis.com/flutter_infra_release/releases/stable/linux/flutter_linux_${FLUTTER_VERSION}-stable.tar.xz"

if [[ ! -x "${INSTALL_ROOT}/bin/flutter" ]]; then
  rm -rf "${INSTALL_ROOT}"
  mkdir -p "$(dirname "${INSTALL_ROOT}")"
  curl --fail --location --retry 3 --output "${ARCHIVE}" "${URL}"
  echo "${FLUTTER_SHA256}  ${ARCHIVE}" | sha256sum --check --strict >&2
  TEMP_DIR="$(mktemp -d)"
  tar -xJf "${ARCHIVE}" -C "${TEMP_DIR}"
  mv "${TEMP_DIR}/flutter" "${INSTALL_ROOT}"
  rm -rf "${TEMP_DIR}" "${ARCHIVE}"
fi

printf '%s\n' "${INSTALL_ROOT}/bin"
