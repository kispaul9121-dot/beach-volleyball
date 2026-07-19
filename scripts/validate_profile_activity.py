#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any
import yaml

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"


def load_yaml(path: Path) -> dict[str, Any]:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a mapping")
    return value


def find(items: list[dict[str, Any]], key: str, value: str) -> dict[str, Any] | None:
    return next((item for item in items if str(item.get(key, "")) == value), None)


def main() -> int:
    errors: list[str] = []
    contract = load_yaml(DOCS / "PROFILE_ACTIVITY.yaml")
    management = load_yaml(DOCS / "MANAGEMENT_CENTER.yaml")
    games = load_yaml(DOCS / "GAMES_CATALOG.yaml")
    routes = load_yaml(DOCS / "ROUTES.yaml").get("routes", []) or []
    screens = load_yaml(DOCS / "SCREENS.yaml").get("screens", []) or []
    actions = load_yaml(DOCS / "ACTIONS.yaml").get("actions", []) or []
    tokens = load_yaml(DOCS / "DESIGN_TOKENS.yaml")

    profile_root = contract.get("profile_root", {}) or {}
    if profile_root.get("management_controls_forbidden") is not True:
        errors.append("Profile must forbid creation and management controls")
    if management.get("principles", [""])[0] != "Profile has no creation or event-management controls":
        errors.append("Management contract must keep Profile clean")

    for section_name in ("games_section", "camps_section"):
        section = management.get(section_name, {}) or {}
        if section.get("mode_control", {}).get("label") != "Режим управления":
            errors.append(f"{section_name} management mode label differs")
        if "management_tabs" in section or "tab_labels" in section:
            errors.append(f"{section_name} must not restore Active/Completed tabs")
        current_list = section.get("current_list", {}) or {}
        if current_list.get("temporal_tabs") != "none":
            errors.append(f"{section_name} must declare no temporal tabs")
        if current_list.get("excludes_completed") is not True:
            errors.append(f"{section_name} must exclude completed entities")

    archive = management.get("archive", {}) or {}
    if archive.get("product_status") != "placement_pending":
        errors.append("Archive placement must remain pending")
    if archive.get("entry_point") is not None or archive.get("route") is not None:
        errors.append("Archive must not expose an entry point or route yet")
    if archive.get("top_level_control_forbidden_until_placement_approved") is not True:
        errors.append("Archive control must remain hidden until placement is approved")

    if find(routes, "path", "/manage"):
        errors.append("Standalone /manage route must be removed")
    if find(screens, "id", "management.center"):
        errors.append("Standalone management.center screen must be removed")

    for path in ("/play", "/camps"):
        route = find(routes, "path", path)
        accepted = set((route or {}).get("accepts_query", []) or [])
        if not {"mode", "actorId"}.issubset(accepted):
            errors.append(f"{path} must accept contextual management queries")
        if "manageTab" in accepted:
            errors.append(f"{path} must not accept obsolete manageTab")

    fallbacks = {
        "/games/:gameId/manage": ("/play?", "category=games"),
        "/trainings/:trainingId/manage": ("/play?", "category=trainings"),
        "/tournaments/:tournamentId/manage": ("/play?", "category=tournaments"),
        "/tours/:tourId/manage": ("/camps?", "mode=manage"),
    }
    for path, (prefix, token) in fallbacks.items():
        route = find(routes, "path", path)
        fallback = str((route or {}).get("back_fallback", ""))
        if not fallback.startswith(prefix) or token not in fallback or "mode=manage" not in fallback:
            errors.append(f"Manage fallback is not contextual for {path}")
        if "manageTab" in fallback:
            errors.append(f"Manage fallback still contains manageTab for {path}")

    action_ids = {str(item.get("id", "")) for item in actions}
    required = {
        "games.change_mode", "games.create_game", "games.create_training", "games.create_tournament",
        "camps.change_mode", "camps.create", "games.open_entity", "camps.open_camp",
    }
    for action_id in sorted(required - action_ids):
        errors.append(f"Missing action {action_id}")
    for obsolete in {
        "global.open_create_menu", "management.open_center", "management.open_entity",
        "games.change_management_tab", "camps.change_management_tab",
    }:
        if obsolete in action_ids:
            errors.append(f"Obsolete management entry remains: {obsolete}")

    for action_id, expected_source in {
        "games.create_game": "play.main",
        "games.create_training": "play.main",
        "games.create_tournament": "play.main",
        "camps.create": "camps.main",
    }.items():
        action = find(actions, "id", action_id)
        if not action or action.get("source") != expected_source:
            errors.append(f"{action_id} must be owned by {expected_source}")
        return_to = str(((action or {}).get("context", {}) or {}).get("returnTo", ""))
        if "manageTab" in return_to:
            errors.append(f"{action_id} returnTo still contains manageTab")

    if games.get("bottom_tab", {}).get("mode") != "discovery_and_contextual_management":
        errors.append("Games catalog must support contextual management")

    home_text = (DOCS / "screens/home/main.md").read_text(encoding="utf-8")
    play_text = (DOCS / "screens/play/main.md").read_text(encoding="utf-8")
    camps_text = (DOCS / "screens/camps/main.md").read_text(encoding="utf-8")
    if "кнопка `+` отсутствует" not in home_text:
        errors.append("Profile spec must explicitly remove +")
    if "Режим управления" not in play_text or "+ Создать" not in play_text:
        errors.append("Games spec must expose management and creation")
    if "Режим управления" not in camps_text or "+ Создать кэмп" not in camps_text:
        errors.append("Camps spec must expose management and creation")
    for name, text in (("Games", play_text), ("Camps", camps_text)):
        if "Активные · Завершённые" in text:
            errors.append(f"{name} spec restored Active/Completed controls")
        if "placement_pending" not in text and "не утвержден" not in text.lower() and "не утверждены" not in text.lower():
            errors.append(f"{name} spec must keep archive placement pending")

    feedback = tokens.get("motion", {}).get("one_shot_feedback", {}).get("profile_activity_confirmation", {})
    if feedback.get("tab_id") != "home" or feedback.get("repetitions") != 1:
        errors.append("Profile participation feedback must remain one-shot")

    if errors:
        print("Contextual management validation failed:")
        for error in errors:
            print(f"  - {error}")
        return 1
    print("Contextual management validation passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
