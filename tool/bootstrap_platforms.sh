
#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TEMP_DIR="$(mktemp -d)"
trap 'rm -rf "${TEMP_DIR}"' EXIT

flutter create \
  --platforms=android,ios \
  --org pl.kalkulatorlekow \
  --project-name kalkulator_lekow \
  --empty \
  "${TEMP_DIR}/generated"

rm -rf "${ROOT_DIR}/android" "${ROOT_DIR}/ios"
cp -R "${TEMP_DIR}/generated/android" "${ROOT_DIR}/android"
cp -R "${TEMP_DIR}/generated/ios" "${ROOT_DIR}/ios"
cp "${TEMP_DIR}/generated/.metadata" "${ROOT_DIR}/.metadata"

printf 'Generated Android and iOS projects with %s\n' "$(flutter --version | head -n 1)"
