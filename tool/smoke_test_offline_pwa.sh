#!/usr/bin/env bash
set -euo pipefail

BUILD_DIR="${1:-build/web}"
PORT="${OFFLINE_TEST_PORT:-8765}"
ORIGIN="http://127.0.0.1:${PORT}/"

if [[ ! -f "${BUILD_DIR}/index.html" ]]; then
  echo "Offline smoke test requires a finalized web build: ${BUILD_DIR}" >&2
  exit 1
fi

BROWSER=""
for candidate in google-chrome google-chrome-stable chromium chromium-browser; do
  if command -v "${candidate}" >/dev/null 2>&1; then
    BROWSER="$(command -v "${candidate}")"
    break
  fi
done
if [[ -z "${BROWSER}" ]]; then
  echo "No supported Chromium browser found for the offline smoke test." >&2
  exit 1
fi

PROFILE_DIR="$(mktemp -d)"
ONLINE_DOM="$(mktemp)"
OFFLINE_DOM="$(mktemp)"
SERVER_LOG="$(mktemp)"
SERVER_PID=""

cleanup() {
  if [[ -n "${SERVER_PID}" ]] && kill -0 "${SERVER_PID}" >/dev/null 2>&1; then
    kill "${SERVER_PID}" >/dev/null 2>&1 || true
    wait "${SERVER_PID}" >/dev/null 2>&1 || true
  fi
  rm -rf "${PROFILE_DIR}"
  rm -f "${ONLINE_DOM}" "${OFFLINE_DOM}" "${SERVER_LOG}"
}
trap cleanup EXIT

python3 -m http.server "${PORT}" \
  --bind 127.0.0.1 \
  --directory "${BUILD_DIR}" \
  >"${SERVER_LOG}" 2>&1 &
SERVER_PID="$!"

for _ in $(seq 1 40); do
  if curl --fail --silent --show-error "${ORIGIN}" >/dev/null 2>&1; then
    break
  fi
  sleep 0.25
done
if ! curl --fail --silent --show-error "${ORIGIN}" >/dev/null; then
  cat "${SERVER_LOG}" >&2
  echo "Local PWA server did not start." >&2
  exit 1
fi

CHROME_FLAGS=(
  --headless=new
  --no-sandbox
  --disable-gpu
  --disable-dev-shm-usage
  --no-first-run
  --no-default-browser-check
  --user-data-dir="${PROFILE_DIR}"
)

"${BROWSER}" "${CHROME_FLAGS[@]}" \
  --virtual-time-budget=25000 \
  --dump-dom "${ORIGIN}" >"${ONLINE_DOM}"

if ! grep -q 'data-offline-ready="true"' "${ONLINE_DOM}"; then
  echo "Service worker did not report a complete online cache." >&2
  cat "${ONLINE_DOM}" >&2
  exit 1
fi
if grep -q 'id="boot-status"' "${ONLINE_DOM}"; then
  echo "Flutter did not render its first online frame." >&2
  exit 1
fi

kill "${SERVER_PID}"
wait "${SERVER_PID}" >/dev/null 2>&1 || true
SERVER_PID=""

if curl --fail --silent "${ORIGIN}" >/dev/null 2>&1; then
  echo "The local server is still reachable; offline mode was not tested." >&2
  exit 1
fi

"${BROWSER}" "${CHROME_FLAGS[@]}" \
  --virtual-time-budget=15000 \
  --dump-dom "${ORIGIN}" >"${OFFLINE_DOM}"

if ! grep -q 'data-offline-ready="true"' "${OFFLINE_DOM}"; then
  echo "Installed PWA did not become ready while the server was offline." >&2
  cat "${OFFLINE_DOM}" >&2
  exit 1
fi
if grep -q 'id="boot-status"' "${OFFLINE_DOM}"; then
  echo "Flutter did not render its first offline frame." >&2
  exit 1
fi
if grep -q 'chrome-error://chromewebdata' "${OFFLINE_DOM}"; then
  echo "Chromium displayed its offline error page instead of InfusionCalc." >&2
  exit 1
fi

printf 'Offline PWA smoke test passed with %s.\n' "${BROWSER}"
