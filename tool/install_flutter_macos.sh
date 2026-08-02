#!/usr/bin/env bash
set -euo pipefail

FLUTTER_VERSION="${FLUTTER_VERSION:-3.44.8}"
INSTALL_ROOT="${FLUTTER_INSTALL_ROOT:-${HOME}/Library/Caches/kalkulator-lekow/flutter-${FLUTTER_VERSION}}"
ARCH="$(uname -m)"

case "${ARCH}" in
  arm64)
    ARCHIVE_NAME="flutter_macos_arm64_${FLUTTER_VERSION}-stable.zip"
    FLUTTER_SHA256="${FLUTTER_SHA256_MACOS_ARM64:-c3d6fe95078f7001d947a31d42527de91d5bfe62e4cf444a1493a2e8f1fb199d}"
    ;;
  x86_64)
    ARCHIVE_NAME="flutter_macos_${FLUTTER_VERSION}-stable.zip"
    FLUTTER_SHA256="${FLUTTER_SHA256_MACOS_X64:-b2f765234217327a5859d046c9f3b167387b61da5408b5866ed448d905877c66}"
    ;;
  *)
    echo "Unsupported macOS architecture: ${ARCH}" >&2
    exit 1
    ;;
esac

ARCHIVE="${RUNNER_TEMP:-/tmp}/${ARCHIVE_NAME}"
URL="https://storage.googleapis.com/flutter_infra_release/releases/stable/macos/${ARCHIVE_NAME}"

if [[ ! -x "${INSTALL_ROOT}/bin/flutter" ]]; then
  rm -rf "${INSTALL_ROOT}"
  mkdir -p "$(dirname "${INSTALL_ROOT}")"
  curl --fail --location --retry 3 --output "${ARCHIVE}" "${URL}"
  echo "${FLUTTER_SHA256}  ${ARCHIVE}" | shasum -a 256 --check >&2
  TEMP_DIR="$(mktemp -d)"
  unzip -q "${ARCHIVE}" -d "${TEMP_DIR}"
  mv "${TEMP_DIR}/flutter" "${INSTALL_ROOT}"
  rm -rf "${TEMP_DIR}" "${ARCHIVE}"
fi

printf '%s\n' "${INSTALL_ROOT}/bin"
