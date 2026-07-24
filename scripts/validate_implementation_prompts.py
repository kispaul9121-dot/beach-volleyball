#!/usr/bin/env python3
"""Validate the ordered VolleyPlay implementation prompt pack."""

from __future__ import annotations

import hashlib
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
PROMPT_DIR = DOCS / "implementation-prompts"

EXPECTED_FILES = [
    "01-foundation.md",
    "02-auth-actors.md",
    "03-shell-profile-catalog.md",
    "04-games-public-create.md",
    "05-games-management-formats.md",
    "06-games-audit-trainings.md",
    "07-tournaments.md",
    "08-chats-payments.md",
    "09-camps-organizations.md",
    "10-quality-release.md",
]

HEADING = re.compile(r"^## (\d{3}) — (.+)$", re.MULTILINE)


def normalized(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip().casefold()


def main() -> int:
    errors: list[str] = []
    prompts: dict[int, tuple[str, str, str]] = {}

    if not PROMPT_DIR.exists():
        print("Implementation prompt validation failed: directory is missing")
        return 1

    for file_name in EXPECTED_FILES:
        path = PROMPT_DIR / file_name
        if not path.exists():
            errors.append(f"Missing prompt file: {file_name}")
            continue

        text = path.read_text(encoding="utf-8")
        matches = list(HEADING.finditer(text))
        if len(matches) != 8:
            errors.append(f"{file_name} must contain exactly 8 numbered prompts, found {len(matches)}")

        for index, match in enumerate(matches):
            number = int(match.group(1))
            title = match.group(2).strip()
            start = match.end()
            end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
            body = text[start:end].strip()

            if number in prompts:
                errors.append(f"Duplicate prompt number: {number:03d}")
            prompts[number] = (title, body, file_name)

            if "```text" not in body:
                errors.append(f"Prompt {number:03d} must contain a copyable text block")
            if "Commit:" not in body:
                errors.append(f"Prompt {number:03d} must define a logical commit")
            if len(normalized(body)) < 250:
                errors.append(f"Prompt {number:03d} is too small to be executable")

    expected_numbers = set(range(1, 81))
    actual_numbers = set(prompts)
    for missing in sorted(expected_numbers - actual_numbers):
        errors.append(f"Missing prompt number: {missing:03d}")
    for unexpected in sorted(actual_numbers - expected_numbers):
        errors.append(f"Unexpected prompt number: {unexpected:03d}")

    title_owner: dict[str, int] = {}
    body_owner: dict[str, int] = {}
    for number, (title, body, _) in prompts.items():
        title_key = normalized(title)
        previous_title = title_owner.get(title_key)
        if previous_title is not None:
            errors.append(f"Duplicate prompt title: {previous_title:03d} and {number:03d}")
        title_owner[title_key] = number

        body_hash = hashlib.sha256(normalized(body).encode("utf-8")).hexdigest()
        previous_body = body_owner.get(body_hash)
        if previous_body is not None:
            errors.append(f"Duplicate prompt body: {previous_body:03d} and {number:03d}")
        body_owner[body_hash] = number

    runbook = (PROMPT_DIR / "README.md").read_text(encoding="utf-8")
    for required in ("80 непересекающихся промтов", "light-first", "definition_pending", "IMPLEMENTATION_STATUS.yaml"):
        if required not in runbook:
            errors.append(f"Prompt runbook is missing required policy: {required}")
    for file_name in EXPECTED_FILES:
        if file_name not in runbook:
            errors.append(f"Prompt runbook does not reference {file_name}")

    index_text = (DOCS / "PROMPTS.md").read_text(encoding="utf-8")
    if "implementation-prompts/README.md" not in index_text or "80" not in index_text:
        errors.append("docs/PROMPTS.md must point to the 80-prompt runbook")
    if "Тест швейцарской системы" in index_text:
        errors.append("Legacy Swiss implementation prompt must not remain in docs/PROMPTS.md")

    print(f"Implementation prompts found: {len(prompts)}")
    if errors:
        print("\nImplementation prompt validation failed:")
        for error in errors:
            print(f"  - {error}")
        return 1

    print("Implementation prompt validation passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
