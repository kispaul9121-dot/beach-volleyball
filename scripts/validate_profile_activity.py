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
    connections = load_yaml(DOCS / "PROFILE_CONNECTIONS.yaml")
    routes = load_yaml(DOCS / "ROUTES.yaml").get("routes", []) or []
    actions = load_yaml(DOCS / "ACTIONS.yaml").get("actions", []) or []
    resolvers = load_yaml(DOCS / "NAVIGATION_RESOLVERS.yaml").get("dynamic_destinations", []) or []
    tokens = load_yaml(DOCS / "DESIGN_TOKENS.yaml")

    for catalog in ("games", "camps"):
        cfg = (contract.get("catalog_boundaries", {}) or {}).get(catalog, {}) or {}
        if cfg.get("mode") != "discovery_only":
            errors.append(f"{catalog} catalog must be discovery_only")
        forbidden = set(cfg.get("forbids", []) or [])
        if not {"participating_tab", "managing_tab"}.issubset(forbidden):
            errors.append(f"{catalog} catalog must forbid participating/managing tabs")

    profile_root = contract.get("profile_root", {}) or {}
    if "activity_switch" in profile_root:
        errors.append("Profile must not restore activity switch")
    if profile_root.get("management_controls_forbidden") is not True:
        errors.append("Profile must forbid embedded management controls")
    if profile_root.get("activity_entry", {}).get("screen") != "profile.activity":
        errors.append("Profile must open unified profile.activity")

    activity = contract.get("activity_screen", {}) or {}
    if activity.get("tabs") != ["upcoming", "past"]:
        errors.append("Unified activity tabs must be upcoming, past")
    if activity.get("management_items_forbidden") is not True:
        errors.append("Unified activity must not include managed items")

    if management.get("center", {}).get("screen") != "management.center":
        errors.append("Missing management.center contract")
    if management.get("catalog_tap", {}).get("resolver") != "dynamic.catalog_entity_entry":
        errors.append("Catalog management resolver differs from contract")

    if connections.get("placement", {}).get("layout") != "single_horizontal_connection_rail":
        errors.append("Profile connections must use one horizontal rail")
    if connections.get("row_ui", {}).get("full_width_stacked_rows_forbidden") is not True:
        errors.append("Profile connections must forbid stacked full-width rows")

    for path in ("/activity", "/manage"):
        if not find(routes, "path", path):
            errors.append(f"Missing route {path}")

    for path in ("/play", "/camps"):
        route = find(routes, "path", path)
        if route and "tab" in set(route.get("accepts_query", []) or []):
            errors.append(f"{path} must not accept personal tab query")

    manage_fallbacks = {
        "/games/:gameId/manage": "type=games",
        "/trainings/:trainingId/manage": "type=trainings",
        "/tournaments/:tournamentId/manage": "type=tournaments",
        "/tours/:tourId/manage": "type=camps",
    }
    for path, token in manage_fallbacks.items():
        route = find(routes, "path", path)
        fallback = str((route or {}).get("back_fallback", ""))
        if not fallback.startswith("/manage?") or token not in fallback:
            errors.append(f"Manage fallback is not management.center for {path}")

    action_ids = {str(item.get("id", "")) for item in actions}
    required = {
        "home.open_activity", "management.open_center", "management.open_entity",
        "management.open_create_menu", "entity.start_join_flow",
    }
    for action_id in sorted(required - action_ids):
        errors.append(f"Missing action {action_id}")
    for obsolete in {
        "home.change_activity_mode", "home.open_managed_entity",
        "games.change_tab", "camps.change_tab",
        "entity.join", "entity.request_to_join", "entity.join_waitlist",
    }:
        if obsolete in action_ids:
            errors.append(f"Obsolete action remains: {obsolete}")

    for action_id in ("games.open_entity", "camps.open_camp"):
        action = find(actions, "id", action_id)
        if not action or action.get("destination") != "dynamic.catalog_entity_entry":
            errors.append(f"{action_id} must use capability-aware resolver")

    resolver = find(resolvers, "id", "dynamic.catalog_entity_entry")
    expected_targets = {
        "game.details", "training.details", "tournament.details", "tour.details",
        "game.manage", "training.manage", "tournament.manage", "tour.manage",
    }
    if not resolver or set(resolver.get("resolves_to", []) or []) != expected_targets:
        errors.append("dynamic.catalog_entity_entry targets differ from contract")

    if games.get("bottom_tab", {}).get("mode") != "discovery_only":
        errors.append("GAMES_CATALOG bottom tab must be discovery_only")
    if games.get("catalog_open_policy", {}).get("resolver") != "dynamic.catalog_entity_entry":
        errors.append("GAMES_CATALOG must declare capability-aware opening")

    join_action = find(actions, "id", "entity.start_join_flow")
    if join_action:
        if join_action.get("destination") != "system.resolve_join_flow":
            errors.append("Join action must use system.resolve_join_flow")
        if join_action.get("success") != "system.profile_activity_feedback":
            errors.append("Join action must trigger profile activity feedback")

    feedback = tokens.get("motion", {}).get("one_shot_feedback", {}).get("profile_activity_confirmation", {})
    if feedback.get("tab_id") != "home" or feedback.get("repetitions") != 1:
        errors.append("Profile feedback must target home exactly once")
    if feedback.get("layout_change_forbidden") is not True:
        errors.append("Profile feedback must not change tab bar layout")

    home_text = (DOCS / "screens/home/main.md").read_text(encoding="utf-8")
    if "Участвую · Управляю" in home_text or "Участвую / Управляю" in home_text:
        errors.append("Profile spec restored activity switch")
    if "Вся моя активность" not in home_text:
        errors.append("Profile spec must expose unified activity")
    if "dynamic.catalog_entity_entry" not in (DOCS / "screens/play/main.md").read_text(encoding="utf-8"):
        errors.append("Games spec must describe capability-aware opening")

    if errors:
        print("Profile and management validation failed:")
        for error in errors:
            print(f"  - {error}")
        return 1
    print("Profile and management validation passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
