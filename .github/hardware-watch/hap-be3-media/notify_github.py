#!/usr/bin/env python3
"""Maintain one GitHub tracking issue and alert on stock transitions."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Any
from urllib.error import HTTPError
from urllib.parse import quote
from urllib.request import Request, urlopen

API_VERSION = "2022-11-28"
LABEL = "hardware-watch"
ISSUE_TITLE = "[watch] MikroTik hAP be³ Media — dostępność"
AVAILABLE = "available"
UNAVAILABLE = "unavailable"
UNKNOWN = "unknown"
STATE_RE = re.compile(r"<!-- availability-state: ([a-z]+) -->")
FINGERPRINT_RE = re.compile(r"<!-- availability-fingerprint: ([a-f0-9]*) -->")


def api_request(method: str, path: str, token: str, payload: Any | None = None) -> Any:
    url = f"https://api.github.com{path}"
    data = None if payload is None else json.dumps(payload, ensure_ascii=False).encode("utf-8")
    request = Request(
        url,
        data=data,
        method=method,
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": API_VERSION,
            "User-Agent": "HomeZone-HardwareWatch/1.0",
            "Content-Type": "application/json",
        },
    )
    try:
        with urlopen(request, timeout=30) as response:
            raw = response.read()
            return json.loads(raw.decode("utf-8")) if raw else None
    except HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"GitHub API {method} {path} failed: HTTP {exc.code}: {body[:500]}") from exc


def ensure_label(repo: str, token: str) -> None:
    owner, name = repo.split("/", 1)
    label_path = f"/repos/{owner}/{name}/labels/{quote(LABEL, safe='')}"
    try:
        api_request("GET", label_path, token)
        return
    except RuntimeError as exc:
        if "HTTP 404" not in str(exc):
            raise
    api_request(
        "POST",
        f"/repos/{owner}/{name}/labels",
        token,
        {
            "name": LABEL,
            "color": "1d76db",
            "description": "Automatyczne monitory dostępności sprzętu Home Zone",
        },
    )


def find_tracking_issue(repo: str, token: str) -> dict[str, Any] | None:
    owner, name = repo.split("/", 1)
    issues = api_request(
        "GET",
        f"/repos/{owner}/{name}/issues?state=all&labels={quote(LABEL)}&per_page=100",
        token,
    )
    for issue in issues:
        if "pull_request" not in issue and issue.get("title") == ISSUE_TITLE:
            return issue
    return None


def marker(pattern: re.Pattern[str], body: str, default: str) -> str:
    match = pattern.search(body or "")
    return match.group(1) if match else default


def status_label(observation: str) -> str:
    return {
        AVAILABLE: "✅ DOSTĘPNY",
        UNAVAILABLE: "❌ nadal niedostępny",
        UNKNOWN: "⚠️ wynik częściowo niepewny",
    }.get(observation, observation.upper())


def build_issue_body(
    payload: dict[str, Any],
    markdown: str,
    state_marker: str,
    fingerprint_marker: str,
    owner: str,
    run_url: str,
) -> str:
    summary = payload["summary"]
    observation = payload["observation"]
    report = markdown
    first_newline = report.find("\n")
    if first_newline >= 0:
        report = report[first_newline + 1 :].lstrip()

    return f"""# Monitor zakupu

Monitor dla @{owner}: **MikroTik hAP be³ Media** (`MA53UG+HbeH`).

**Ostatni wynik:** {status_label(observation)}  
**Ostatnia kontrola:** `{payload['completed_at']}`  
**Harmonogram:** codziennie o 09:00 `Europe/Warsaw`  
**Zakres:** {summary['available'] + summary['unavailable'] + summary['preorder'] + summary['unknown']} sklepów w Polsce i Europie

Powiadomienie jest dodawane jako komentarz z oznaczeniem użytkownika, gdy monitor wykryje przejście do dostępności albo zmianę listy dostępnych ofert. Strony z niejednoznacznym lub sprzecznym sygnałem nie wywołują alertu.

[Otwórz ostatnie wykonanie workflow]({run_url})

{report}
<!-- monitor-key: hap-be3-media -->
<!-- availability-state: {state_marker} -->
<!-- availability-fingerprint: {fingerprint_marker} -->
"""


def available_comment(payload: dict[str, Any], owner: str, run_url: str) -> str:
    rows = []
    for result in payload["results"]:
        if result["status"] != AVAILABLE:
            continue
        price = ""
        if result.get("price"):
            price = f" — **{result['price']} {result.get('currency') or ''}**".rstrip()
        rows.append(f"- [{result['store']}]({result['url']}) ({result['country']}){price}")
    offers = "\n".join(rows) or "- Wykryto sygnał dostępności; szczegóły są w raporcie workflow."
    return f"""@{owner} 🚨 **MikroTik hAP be³ Media jest dostępny.**

{offers}

Sprawdzenie: `{payload['completed_at']}` · [szczegóły workflow]({run_url})

Dostępność może szybko się zmienić; przed zakupem potwierdź stan i termin wysyłki bezpośrednio na stronie sklepu.
"""


def should_notify(previous_state: str, previous_fingerprint: str, payload: dict[str, Any]) -> bool:
    return payload["observation"] == AVAILABLE and (
        previous_state != AVAILABLE or previous_fingerprint != payload.get("fingerprint", "")
    )


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results", type=Path, required=True)
    parser.add_argument("--markdown", type=Path, required=True)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    payload = json.loads(args.results.read_text(encoding="utf-8"))
    markdown = args.markdown.read_text(encoding="utf-8")

    repo = os.environ["GITHUB_REPOSITORY"]
    owner = os.environ.get("GITHUB_REPOSITORY_OWNER") or repo.split("/", 1)[0]
    token = os.environ["GITHUB_TOKEN"]
    server = os.environ.get("GITHUB_SERVER_URL", "https://github.com")
    run_id = os.environ["GITHUB_RUN_ID"]
    run_url = f"{server}/{repo}/actions/runs/{run_id}"
    repo_owner, repo_name = repo.split("/", 1)

    ensure_label(repo, token)
    issue = find_tracking_issue(repo, token)
    previous_state = UNKNOWN
    previous_fingerprint = ""
    if issue:
        previous_state = marker(STATE_RE, issue.get("body") or "", UNKNOWN)
        previous_fingerprint = marker(FINGERPRINT_RE, issue.get("body") or "", "")

    notify = should_notify(previous_state, previous_fingerprint, payload)

    # UNKNOWN is not a definitive transition; retain the last definitive marker.
    if payload["observation"] == UNKNOWN:
        state_marker = previous_state
        fingerprint_marker = previous_fingerprint
    elif payload["observation"] == AVAILABLE:
        state_marker = AVAILABLE
        fingerprint_marker = payload.get("fingerprint", "")
    else:
        state_marker = UNAVAILABLE
        fingerprint_marker = ""

    body = build_issue_body(payload, markdown, state_marker, fingerprint_marker, owner, run_url)
    if issue is None:
        issue = api_request(
            "POST",
            f"/repos/{repo_owner}/{repo_name}/issues",
            token,
            {
                "title": ISSUE_TITLE,
                "body": body,
                "labels": [LABEL],
                "assignees": [owner],
            },
        )
        print(f"created tracking issue #{issue['number']}")
        # Assignment and the body mention are the first notification if stock is already present.
        return 0

    api_request(
        "PATCH",
        f"/repos/{repo_owner}/{repo_name}/issues/{issue['number']}",
        token,
        {
            "body": body,
            "state": "open",
            "labels": [LABEL],
            "assignees": [owner],
        },
    )
    print(f"updated tracking issue #{issue['number']}")

    if notify:
        api_request(
            "POST",
            f"/repos/{repo_owner}/{repo_name}/issues/{issue['number']}/comments",
            token,
            {"body": available_comment(payload, owner, run_url)},
        )
        print(f"posted availability alert in issue #{issue['number']}")
    else:
        print("no availability transition; no alert comment posted")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
