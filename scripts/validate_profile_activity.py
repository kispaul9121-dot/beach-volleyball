#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        value = yaml.safe_load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a mapping")
    return value


def find(items: list[dict[str, Any]], key: str, value: str) -> dict[str, Any] | None:
    return next((item for item in items if str(item.get(key, "")) == value), None)


def main() -> int:
    errors: list[str] = []

    contract = load_yaml(DOCS / "PROFILE_ACTIVITY.yaml")
    games = load_yaml(DOCS / "GAMES_CATALOG.yaml")
    routes = load_yaml(DOCS / "ROUTES.yaml").get("routes", []) or []
    actions = load_yaml(DOCS / "ACTIONS.yaml").get("actions", []) or []
    tokens = load_yaml(DOCS / "DESIGN_TOKENS.yaml")

    for catalog in ("games", "camps"):
        cfg = (contract.get("catalog_boundaries", {}) or {}).get(catalog, {}) or {}
        if cfg.get("mode") != "discovery_only":
            errors.append(f"{catalog} catalog must be discovery_only")
        forbidden = set(cfg.get("forbids", []) or [])
        if not {"participating_tab", "managing_tab"}.issubset(forbidden):
            errors.append(f"{catalog} catalog must forbid participating/managing tabs")

    activity = contract.get("profile_root", {}).get("activity_switch", {}) or {}
    if activity.get("values") != ["participating", "managing"]:
        errors.append("Profile activity switch must be participating, managing")
    if activity.get("labels") != {"participating": "Участвую", "managing": "Управляю"}:
        errors.append("Profile activity labels must be Участвую / Управляю")

    expected_lists = {
        "games": (["upcoming", "past"], ["active", "completed"]),
        "trainings": (["booked", "past"], ["active", "completed"]),
        "tournaments": (["registered", "past"], ["active", "completed"]),
        "camps": (["booked", "past"], ["active", "completed"]),
    }
    full_lists = contract.get("full_lists", {}) or {}
    for name, (participating, managing) in expected_lists.items():
        item = full_lists.get(name, {}) or {}
        if item.get("participating_tabs") != participating:
            errors.append(f"{name} participating tabs differ from contract")
        if item.get("managing_tabs") != managing:
            errors.append(f"{name} managing tabs differ from contract")

    if games.get("bottom_tab", {}).get("mode") != "discovery_only":
        errors.append("GAMES_CATALOG bottom tab must be discovery_only")
    if "primary_tabs" in (games.get("bottom_tab", {}) or {}):
        errors.append("GAMES_CATALOG must not restore primary tabs")

    for path in ("/play", "/camps"):
        route = find(routes, "path", path)
        if not route:
            errors.append(f"Missing route {path}")
            continue
        if "tab" in set(route.get("accepts_query", []) or []):
            errors.append(f"{path} must not accept personal tab query")

    action_ids = {str(item.get("id", "")) for item in actions}
    if "entity.start_join_flow" not in action_ids:
        errors.append("Missing generic entity.start_join_flow action")
    for obsolete in ("entity.join", "entity.request_to_join", "entity.join_waitlist"):
        if obsolete in action_ids:
            errors.append(f"Obsolete exposed join action remains: {obsolete}")

    join_action = find(actions, "id", "entity.start_join_flow")
    if join_action:
        if join_action.get("destination") != "system.resolve_join_flow":
            errors.append("Join action must use system.resolve_join_flow")
        if join_action.get("success") != "system.profile_activity_feedback":
            errors.append("Join action must trigger profile activity feedback")

    feedback = (
        tokens.get("motion", {})
        .get("one_shot_feedback", {})
        .get("profile_activity_confirmation", {})
    )
    if feedback.get("tab_id") != "home":
        errors.append("Profile feedback must target home tab")
    if feedback.get("repetitions") != 1:
        errors.append("Profile feedback must run exactly once")
    duration = int(feedback.get("duration_ms", 0) or 0)
    if duration < 600 or duration > 1000:
        errors.append("Profile feedback duration must be 600-1000 ms")
    if feedback.get("layout_change_forbidden") is not True:
        errors.append("Profile feedback must not change tab bar layout")

    play_text = (DOCS / "screens/play/main.md").read_text(encoding="utf-8")
    camps_text = (DOCS / "screens/camps/main.md").read_text(encoding="utf-8")
    home_text = (DOCS / "screens/home/main.md").read_text(encoding="utf-8")
    settings_text = (DOCS / "screens/profile/main.md").read_text(encoding="utf-8")

    for name, text in (("Игры", play_text), ("Кэмпы", camps_text)):
        if "Все · Участвую · Управляю" in text:
            errors.append(f"{name} spec restored personal catalog tabs")
    if "Участвую · Управляю" not in home_text:
        errors.append("Profile spec must contain activity switch")
    if "личные архивы" in settings_text.lower() and "не дублируются" not in settings_text.lower():
        errors.append("Settings must not own personal activity archives")

    if errors:
        print("Profile activity validation failed:")
        for error in errors:
            print(f"  - {error}")
        return 1

    print("Profile activity validation passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
