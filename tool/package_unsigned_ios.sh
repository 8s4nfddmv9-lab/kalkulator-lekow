#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
APP_PATH="${1:-${ROOT_DIR}/build/ios/iphoneos/Runner.app}"
OUTPUT_DIR="${2:-${ROOT_DIR}/dist}"

if [[ ! -d "${APP_PATH}" ]]; then
  printf 'iOS app bundle not found: %s\n' "${APP_PATH}" >&2
  exit 1
fi

INFO_PLIST="${APP_PATH}/Info.plist"
EXECUTABLE_NAME="$(/usr/libexec/PlistBuddy -c 'Print :CFBundleExecutable' "${INFO_PLIST}")"
EXECUTABLE_PATH="${APP_PATH}/${EXECUTABLE_NAME}"

if [[ ! -f "${EXECUTABLE_PATH}" ]]; then
  printf 'iOS executable not found: %s\n' "${EXECUTABLE_PATH}" >&2
  exit 1
fi

APP_VERSION="$(awk '/^version:/ {print $2; exit}' "${ROOT_DIR}/pubspec.yaml")"
if [[ -z "${APP_VERSION}" ]]; then
  printf 'Could not read application version from pubspec.yaml.\n' >&2
  exit 1
fi

SAFE_VERSION="${APP_VERSION//+/-build-}"
IPA_NAME="Kalkulator-Lekow-${SAFE_VERSION}-unsigned.ipa"
IPA_PATH="${OUTPUT_DIR}/${IPA_NAME}"
PAYLOAD_DIR="${OUTPUT_DIR}/Payload"

rm -rf "${PAYLOAD_DIR}"
mkdir -p "${PAYLOAD_DIR}"
/usr/bin/ditto "${APP_PATH}" "${PAYLOAD_DIR}/Runner.app"

rm -f "${IPA_PATH}" "${IPA_PATH}.sha256"
(
  cd "${OUTPUT_DIR}"
  /usr/bin/zip -qry "${IPA_NAME}" Payload
)
rm -rf "${PAYLOAD_DIR}"

/usr/bin/unzip -tq "${IPA_PATH}" >/dev/null
/usr/bin/shasum -a 256 "${IPA_PATH}" > "${IPA_PATH}.sha256"

BUNDLE_ID="$(/usr/libexec/PlistBuddy -c 'Print :CFBundleIdentifier' "${INFO_PLIST}")"
SHORT_VERSION="$(/usr/libexec/PlistBuddy -c 'Print :CFBundleShortVersionString' "${INFO_PLIST}")"
BUILD_NUMBER="$(/usr/libexec/PlistBuddy -c 'Print :CFBundleVersion' "${INFO_PLIST}")"
ARCHITECTURES="$(/usr/bin/lipo -archs "${EXECUTABLE_PATH}")"
COMMIT_SHA="${GITHUB_SHA:-unknown}"
BUILD_TIME_UTC="$(date -u '+%Y-%m-%dT%H:%M:%SZ')"

cat > "${OUTPUT_DIR}/ios-build-info.txt" <<EOF
artifact=${IPA_NAME}
application_version=${APP_VERSION}
ios_short_version=${SHORT_VERSION}
ios_build_number=${BUILD_NUMBER}
bundle_identifier=${BUNDLE_ID}
architectures=${ARCHITECTURES}
commit=${COMMIT_SHA}
built_at_utc=${BUILD_TIME_UTC}
signing=unsigned; sign locally with a free Apple ID before installation
EOF

printf '%s\n' "${IPA_PATH}"
