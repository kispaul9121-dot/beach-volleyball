#!/usr/bin/env python3
"""Validate the ordered Codex/iOS VolleyPlay implementation prompt pack."""

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
    "07-chats-payments.md",
    "08-camps-organizations.md",
    "09-backend-integration.md",
    "10-quality-release.md",
]

HEADING = re.compile(r"^## (\d{3}) — (.+)$", re.MULTILINE)
FIRST_SIX = {
    0: "Базовый запуск",
    1: "Профиль",
    2: "Игры",
    3: "Чаты",
    4: "Кэмпы",
    5: "Настройки",
}
AUDIT_NUMBERS = {9, 19, 29, 39, 49, 59, 69, 79, 89, 93, 98}


def normalized(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip().casefold()


def main() -> int:
    errors: list[str] = []
    prompts: dict[int, tuple[str, str, str]] = {}

    if not PROMPT_DIR.exists():
        print("Implementation prompt validation failed: directory is missing")
        return 1

    actual_md = sorted(path.name for path in PROMPT_DIR.glob("*.md") if path.name != "README.md")
    if actual_md != EXPECTED_FILES:
        errors.append(f"Prompt files differ from expected set: {actual_md}")

    for file_name in EXPECTED_FILES:
        path = PROMPT_DIR / file_name
        if not path.exists():
            errors.append(f"Missing prompt file: {file_name}")
            continue

        text = path.read_text(encoding="utf-8")
        matches = list(HEADING.finditer(text))
        if len(matches) != 10:
            errors.append(f"{file_name} must contain exactly 10 numbered prompts, found {len(matches)}")

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
            if "Проверки:" not in body:
                errors.append(f"Prompt {number:03d} must define implementation checks")
            if len(normalized(body)) < 280:
                errors.append(f"Prompt {number:03d} is too small to be executable")

    expected_numbers = set(range(100))
    actual_numbers = set(prompts)
    for missing in sorted(expected_numbers - actual_numbers):
        errors.append(f"Missing prompt number: {missing:03d}")
    for unexpected in sorted(actual_numbers - expected_numbers):
        errors.append(f"Unexpected prompt number: {unexpected:03d}")

    title_owner: dict[str, int] = {}
    body_owner: dict[str, int] = {}
    for number, (title, body, _) in prompts.items():
        title_key = normalized(title)
        if title_key in title_owner:
            errors.append(f"Duplicate prompt title: {title_owner[title_key]:03d} and {number:03d}")
        title_owner[title_key] = number

        body_hash = hashlib.sha256(normalized(body).encode("utf-8")).hexdigest()
        if body_hash in body_owner:
            errors.append(f"Duplicate prompt body: {body_owner[body_hash]:03d} and {number:03d}")
        body_owner[body_hash] = number

    for number, required_title_fragment in FIRST_SIX.items():
        value = prompts.get(number)
        if value is None or required_title_fragment.casefold() not in value[0].casefold():
            errors.append(f"Prompt {number:03d} must be the required base prompt for {required_title_fragment}")

    prompt_zero = prompts.get(0, ("", "", ""))[1]
    for required in ("iOS-плагина", "IMPLEMENTATION_RUNTIME.yaml", "Supabase", "Expo"):
        if required not in prompt_zero:
            errors.append(f"Prompt 000 is missing required bootstrap concept: {required}")

    for number in AUDIT_NUMBERS:
        body = prompts.get(number, ("", "", ""))[1]
        if "Audit-only" not in body:
            errors.append(f"Control prompt {number:03d} must be Audit-only")

    runbook = (PROMPT_DIR / "README.md").read_text(encoding="utf-8")
    required_runbook = (
        "100 последовательных непересекающихся промтов",
        "000–099",
        "iOS-плагин",
        "@`-упоминание",
        "Supabase Postgres",
        "Expo SQLite",
        "definition_pending",
        "IMPLEMENTATION_STATUS.yaml",
    )
    for required in required_runbook:
        if required not in runbook:
            errors.append(f"Prompt runbook is missing required policy: {required}")
    for file_name in EXPECTED_FILES:
        if file_name not in runbook:
            errors.append(f"Prompt runbook does not reference {file_name}")

    index_text = (DOCS / "PROMPTS.md").read_text(encoding="utf-8")
    if "implementation-prompts/README.md" not in index_text or "100" not in index_text:
        errors.append("docs/PROMPTS.md must point to the 100-prompt runbook")
    legacy_markers = ("80 последовательных непересекающихся промтов", "001–080", "001–008")
    if any(marker in index_text for marker in legacy_markers):
        errors.append("docs/PROMPTS.md still references the legacy prompt pack")

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
