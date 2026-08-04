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
BROWSER_LOG="$(mktemp)"
SERVER_PID=""

cleanup() {
  if [[ -n "${SERVER_PID}" ]] && kill -0 "${SERVER_PID}" >/dev/null 2>&1; then
    kill "${SERVER_PID}" >/dev/null 2>&1 || true
    wait "${SERVER_PID}" >/dev/null 2>&1 || true
  fi
  rm -rf "${PROFILE_DIR}"
  rm -f "${ONLINE_DOM}" "${OFFLINE_DOM}" "${SERVER_LOG}" "${BROWSER_LOG}"
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

capture_ready_dom() {
  local output_file="$1"
  local label="$2"
  local attempts="$3"
  local budget_ms="$4"

  for attempt in $(seq 1 "${attempts}"); do
    : >"${BROWSER_LOG}"
    "${BROWSER}" "${CHROME_FLAGS[@]}" \
      --virtual-time-budget="${budget_ms}" \
      --dump-dom "${ORIGIN}" >"${output_file}" 2>"${BROWSER_LOG}" || true

    if grep -q 'data-offline-ready="true"' "${output_file}" && \
      ! grep -q 'id="boot-status"' "${output_file}" && \
      ! grep -q 'chrome-error://chromewebdata' "${output_file}"; then
      return 0
    fi

    echo "${label} readiness attempt ${attempt}/${attempts} did not finish; retrying." >&2
    sleep 1
  done

  echo "${label} did not reach a complete Flutter and service-worker state." >&2
  cat "${BROWSER_LOG}" >&2
  cat "${output_file}" >&2
  return 1
}

# A worker installation may finish only after the first headless page closes.
# Reopening the same persistent profile mirrors closing and reopening a PWA.
capture_ready_dom "${ONLINE_DOM}" "Online PWA" 6 15000

kill "${SERVER_PID}"
wait "${SERVER_PID}" >/dev/null 2>&1 || true
SERVER_PID=""

if curl --fail --silent "${ORIGIN}" >/dev/null 2>&1; then
  echo "The local server is still reachable; offline mode was not tested." >&2
  exit 1
fi

capture_ready_dom "${OFFLINE_DOM}" "Offline PWA" 4 15000

printf 'Offline PWA smoke test passed with %s.\n' "${BROWSER}"
