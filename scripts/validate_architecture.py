#!/usr/bin/env python3
"""Validate the VolleyPlay architecture documentation.

Run from the repository root:
    python scripts/validate_architecture.py
"""

from __future__ import annotations

import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a YAML mapping")
    return data


def duplicates(values: list[str]) -> list[str]:
    return sorted(value for value, count in Counter(values).items() if count > 1)


def is_virtual_reference(value: str) -> bool:
    return value.startswith(("system.", "dynamic.", "global."))


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []

    screens_doc = load_yaml(DOCS / "SCREENS.yaml")
    routes_doc = load_yaml(DOCS / "ROUTES.yaml")
    actions_doc = load_yaml(DOCS / "ACTIONS.yaml")

    screens = screens_doc.get("screens", [])
    routes = routes_doc.get("routes", [])
    actions = actions_doc.get("actions", [])

    if not isinstance(screens, list):
        errors.append("SCREENS.yaml: screens must be a list")
        screens = []
    if not isinstance(routes, list):
        errors.append("ROUTES.yaml: routes must be a list")
        routes = []
    if not isinstance(actions, list):
        errors.append("ACTIONS.yaml: actions must be a list")
        actions = []

    screen_ids = [str(item.get("id", "")) for item in screens]
    route_paths = [str(item.get("path", "")) for item in routes]
    action_ids = [str(item.get("id", "")) for item in actions]

    for duplicate in duplicates(screen_ids):
        errors.append(f"Duplicate screen id: {duplicate}")
    for duplicate in duplicates(route_paths):
        errors.append(f"Duplicate route path: {duplicate}")
    for duplicate in duplicates(action_ids):
        errors.append(f"Duplicate action id: {duplicate}")

    screen_by_id = {str(item.get("id")): item for item in screens if item.get("id")}
    route_by_screen: dict[str, list[dict[str, Any]]] = defaultdict(list)

    # Screen checks.
    for screen_id, screen in screen_by_id.items():
        route = screen.get("route")
        spec = screen.get("spec")

        if not route:
            errors.append(f"Screen {screen_id} has no route")
        if not spec:
            errors.append(f"Screen {screen_id} has no spec path")
        else:
            spec_path = ROOT / str(spec)
            if not spec_path.is_file():
                errors.append(f"Screen {screen_id} references missing spec: {spec}")

        if route and not str(route).startswith("system://") and screen.get("back_fallback") is None:
            # Root tabs and auth entry are allowed without fallback.
            if screen_id not in {
                "home.main",
                "play.main",
                "chats.main",
                "clubs.main",
                "profile.main",
                "auth.welcome",
            }:
                warnings.append(f"Screen {screen_id} has no back_fallback in SCREENS.yaml")

    # Route checks.
    for route in routes:
        path = str(route.get("path", ""))
        screen_id = str(route.get("screen", ""))
        navigator = str(route.get("navigator", ""))

        if not path:
            errors.append("Route without path")
        if screen_id not in screen_by_id:
            errors.append(f"Route {path} references missing screen: {screen_id}")
        else:
            route_by_screen[screen_id].append(route)
            declared = str(screen_by_id[screen_id].get("route", ""))
            if declared != path:
                errors.append(
                    f"Route mismatch for {screen_id}: SCREENS={declared!r}, ROUTES={path!r}"
                )

        if "/manage" in path and not route.get("permission"):
            errors.append(f"Manage route has no permission: {path}")

        if path.endswith("/create"):
            accepts = set(route.get("accepts_query", []) or [])
            missing = {"actorId", "returnTo"} - accepts
            if missing:
                errors.append(
                    f"Create route {path} is missing query parameters: {sorted(missing)}"
                )

        if navigator not in {"tab", "auth_stack", "onboarding_stack"}:
            if not route.get("back_fallback"):
                errors.append(f"Stack/modal route has no back_fallback: {path}")

    for screen_id, screen in screen_by_id.items():
        if screen_id == "actor.switcher":
            # It is represented by a system:// route.
            pass
        if screen_id not in route_by_screen:
            errors.append(f"Screen has no route entry: {screen_id}")

    # Action checks.
    pseudo_sources = {
        "global.header",
        "dynamic.global_or_section_header",
        "dynamic.entity_details",
        "dynamic.entity_manage",
        "dynamic.create_wizard",
        "dynamic.onboarding_optional_profile",
    }

    for action in actions:
        action_id = str(action.get("id", ""))
        source = str(action.get("source", ""))
        destination = str(action.get("destination", ""))

        if not action_id:
            errors.append("Action without id")
        if not source:
            errors.append(f"Action {action_id} has no source")
        elif source not in screen_by_id and source not in pseudo_sources and not is_virtual_reference(source):
            errors.append(f"Action {action_id} references missing source: {source}")

        if not destination:
            errors.append(f"Action {action_id} has no destination")
        elif destination not in screen_by_id and not is_virtual_reference(destination):
            errors.append(f"Action {action_id} references missing destination: {destination}")

        if action_id.startswith("create.") or ".create" in action_id:
            context = action.get("context", {}) or {}
            # Shared wizard-local actions do not need navigation context.
            if destination in {
                "game.create",
                "training.create",
                "tournament.create",
                "season.create",
                "tour.create",
            }:
                if "actorId" not in context:
                    errors.append(f"Creation navigation {action_id} has no actorId context")

    # Bottom-tab convention.
    expected_tab_screens = {
        "home": "home.main",
        "play": "play.main",
        "chats": "chats.main",
        "clubs": "clubs.main",
        "profile": "profile.main",
    }
    bottom_tabs = screens_doc.get("bottom_tabs", []) or []
    if bottom_tabs != list(expected_tab_screens):
        errors.append(
            "bottom_tabs must be exactly: home, play, chats, clubs, profile"
        )
    for tab_screen in expected_tab_screens.values():
        if tab_screen not in screen_by_id:
            errors.append(f"Missing bottom-tab screen: {tab_screen}")

    print(f"Screens: {len(screens)}")
    print(f"Routes: {len(routes)}")
    print(f"Actions: {len(actions)}")

    if warnings:
        print("\nWarnings:")
        for warning in warnings:
            print(f"  - {warning}")

    if errors:
        print("\nErrors:")
        for error in errors:
            print(f"  - {error}")
        return 1

    print("\nArchitecture validation passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
