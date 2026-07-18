#!/usr/bin/env python3
"""Validate the VolleyPlay navigation graph and immutable bottom menu.

Checks:
- the five global bottom tabs are exact and are the only tab navigator routes;
- screens and routes form a one-to-one mapping;
- stack/modal parents and back fallbacks resolve to registered routes;
- every action has a label, permission and valid source/destination;
- action navigation context is accepted by the destination route;
- player picker navigation always carries entity/draft context and returnTo;
- dynamic sources, destinations and success aliases are explicitly declared;
- destructive actions use a confirmation destination;
- legacy navigation concepts do not return to source-of-truth documents.
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
        value = yaml.safe_load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a mapping")
    return value


def duplicates(values: list[str]) -> list[str]:
    return sorted(value for value, count in Counter(values).items() if value and count > 1)


def route_without_query(value: str) -> str:
    return value.split("?", 1)[0]


def is_system(value: str) -> bool:
    return value.startswith("system.") or value.startswith("system://")


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []

    screens_doc = load_yaml(DOCS / "SCREENS.yaml")
    routes_doc = load_yaml(DOCS / "ROUTES.yaml")
    actions_doc = load_yaml(DOCS / "ACTIONS.yaml")
    resolvers_doc = load_yaml(DOCS / "NAVIGATION_RESOLVERS.yaml")

    screens = screens_doc.get("screens", []) or []
    routes = routes_doc.get("routes", []) or []
    actions = actions_doc.get("actions", []) or []
    if not all(isinstance(value, list) for value in (screens, routes, actions)):
        raise ValueError("screens, routes and actions must be lists")

    screen_ids = [str(item.get("id", "")) for item in screens if isinstance(item, dict)]
    screen_by_id = {str(item.get("id")): item for item in screens if isinstance(item, dict) and item.get("id")}
    route_by_screen: dict[str, list[dict[str, Any]]] = defaultdict(list)
    route_by_path: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for route in routes:
        if not isinstance(route, dict):
            continue
        route_by_screen[str(route.get("screen", ""))].append(route)
        route_by_path[str(route.get("path", ""))].append(route)

    for value in duplicates(screen_ids):
        errors.append(f"Duplicate screen id: {value}")
    for value in duplicates([str(route.get("path", "")) for route in routes if isinstance(route, dict)]):
        errors.append(f"Duplicate route path: {value}")
    for value in duplicates([str(action.get("id", "")) for action in actions if isinstance(action, dict)]):
        errors.append(f"Duplicate action id: {value}")

    # Immutable bottom navigation.
    nav = resolvers_doc.get("bottom_navigation", {}) or {}
    nav_items = nav.get("items", []) or []
    if nav.get("immutable") is not True:
        errors.append("NAVIGATION_RESOLVERS.yaml must mark bottom_navigation immutable=true")

    expected_ids = [str(item.get("id", "")) for item in nav_items]
    if expected_ids != ["home", "play", "chats", "clubs", "profile"]:
        errors.append("Bottom navigation IDs must be exactly home, play, chats, clubs, profile")
    if screens_doc.get("bottom_tabs") != expected_ids:
        errors.append("SCREENS.yaml bottom_tabs differs from immutable navigation contract")

    expected_tab_paths: set[str] = set()
    expected_tab_screens: set[str] = set()
    for item in nav_items:
        tab_id = str(item.get("id", ""))
        title = str(item.get("title", ""))
        screen_id = str(item.get("screen", ""))
        path = str(item.get("route", ""))
        expected_tab_paths.add(path)
        expected_tab_screens.add(screen_id)
        screen = screen_by_id.get(screen_id)
        if not screen:
            errors.append(f"Bottom tab {tab_id} references missing screen {screen_id}")
            continue
        if str(screen.get("title", "")) != title:
            errors.append(f"Bottom tab {tab_id} title mismatch: expected {title!r}")
        if str(screen.get("route", "")) != path:
            errors.append(f"Bottom tab {tab_id} route mismatch: expected {path!r}")
        matches = route_by_screen.get(screen_id, [])
        if len(matches) != 1 or str(matches[0].get("navigator", "")) != "tab":
            errors.append(f"Bottom tab {screen_id} must have exactly one navigator=tab route")

    actual_tab_routes = {
        str(route.get("path", ""))
        for route in routes
        if isinstance(route, dict) and str(route.get("navigator", "")) == "tab"
    }
    if actual_tab_routes != expected_tab_paths:
        errors.append(
            f"Only immutable bottom routes may use navigator=tab; expected {sorted(expected_tab_paths)}, "
            f"found {sorted(actual_tab_routes)}"
        )

    for overlay in screens_doc.get("global_overlays", []) or []:
        overlay_id = str(overlay)
        if overlay_id not in screen_by_id and not is_system(overlay_id):
            errors.append(f"Global overlay is neither a screen nor system overlay: {overlay_id}")

    legacy_phrase = "Главная · События · Чаты · Клубы · Профиль"
    for source in (DOCS / "NAVIGATION_RESOLVERS.yaml", DOCS / "DESIGN_TOKENS.yaml", DOCS / "UI_RULES.md"):
        if legacy_phrase in source.read_text(encoding="utf-8"):
            errors.append("Legacy bottom navigation title contract returned: " + str(source.relative_to(ROOT)))

    # One screen ↔ one route and valid navigation fallbacks.
    all_paths = set(route_by_path)
    for screen_id, screen in screen_by_id.items():
        matches = route_by_screen.get(screen_id, [])
        if len(matches) != 1:
            errors.append(f"Screen {screen_id} must have exactly one route entry; found {len(matches)}")
            continue
        route = matches[0]
        if str(screen.get("route", "")) != str(route.get("path", "")):
            errors.append(f"Screen/route mismatch for {screen_id}")

    for route in routes:
        if not isinstance(route, dict):
            continue
        path = str(route.get("path", ""))
        screen_id = str(route.get("screen", ""))
        if screen_id not in screen_by_id:
            errors.append(f"Route {path} references missing screen {screen_id}")
        navigator = str(route.get("navigator", ""))
        root = navigator in {"tab", "auth_stack", "onboarding_stack"} and not route.get("back_fallback")
        fallback = str(route.get("back_fallback", ""))
        if not root and navigator != "tab" and not fallback:
            errors.append(f"Non-root route has no back_fallback: {path}")
        if fallback and not fallback.startswith("system://"):
            target = route_without_query(fallback)
            if target not in all_paths:
                errors.append(f"back_fallback for {path} does not resolve: {fallback}")
        parent = str(route.get("parent", ""))
        if parent and route_without_query(parent) not in all_paths:
            errors.append(f"parent for {path} does not resolve: {parent}")

    # Resolver declarations.
    dynamic_sources = set(str(value) for value in (resolvers_doc.get("dynamic_sources", []) or []))
    dynamic_destinations: dict[str, list[str]] = {}
    for resolver in resolvers_doc.get("dynamic_destinations", []) or []:
        resolver_id = str(resolver.get("id", ""))
        targets = [str(value) for value in (resolver.get("resolves_to", []) or [])]
        dynamic_destinations[resolver_id] = targets
        if not resolver.get("requires_context"):
            errors.append(f"Dynamic destination {resolver_id} has no requires_context")
        for target in targets:
            if target not in screen_by_id:
                errors.append(f"Dynamic destination {resolver_id} resolves to missing screen {target}")

    success_resolvers: dict[str, list[str]] = {}
    for resolver in resolvers_doc.get("success_resolvers", []) or []:
        resolver_id = str(resolver.get("id", ""))
        targets = [str(value) for value in (resolver.get("resolves_to", []) or [])]
        success_resolvers[resolver_id] = targets
        for target in targets:
            if target not in screen_by_id:
                errors.append(f"Success resolver {resolver_id} resolves to missing screen {target}")

    # Actions and button transitions.
    incoming: dict[str, set[str]] = defaultdict(set)
    destructive_tokens = ("delete", "remove", "cancel", "issue_refund")
    pseudo_sources = {"global.header"} | dynamic_sources

    for action in actions:
        if not isinstance(action, dict):
            errors.append("ACTIONS.yaml contains a non-mapping action")
            continue
        action_id = str(action.get("id", ""))
        label = str(action.get("label", ""))
        source = str(action.get("source", ""))
        destination = str(action.get("destination", ""))
        permission = str(action.get("permission", ""))
        success = str(action.get("success", ""))
        context = action.get("context", {}) or {}

        if not action_id:
            errors.append("Action without id")
        if not label:
            errors.append(f"Action {action_id} has no label")
        if not permission:
            errors.append(f"Action {action_id} has no permission")
        if not isinstance(context, dict):
            errors.append(f"Action {action_id} context must be a mapping")
            context = {}

        if source not in screen_by_id and source not in pseudo_sources and not is_system(source):
            errors.append(f"Action {action_id} has undeclared source {source}")

        if destination in screen_by_id:
            incoming[destination].add(action_id)
            destination_routes = route_by_screen.get(destination, [])
            if len(destination_routes) != 1:
                errors.append(f"Action {action_id} points to screen without one route: {destination}")
            elif context:
                accepted = set(destination_routes[0].get("accepts_query", []) or [])
                unknown = set(context) - accepted
                if unknown:
                    errors.append(
                        f"Action {action_id} passes unsupported route context to {destination}: {sorted(unknown)}"
                    )
        elif destination.startswith("dynamic."):
            if destination not in dynamic_destinations:
                errors.append(f"Action {action_id} uses undeclared dynamic destination {destination}")
            for target in dynamic_destinations.get(destination, []):
                incoming[target].add(action_id)
        elif not is_system(destination):
            errors.append(f"Action {action_id} has invalid destination {destination}")

        if success:
            if success in screen_by_id:
                incoming[success].add(action_id + ":success")
            elif success in success_resolvers:
                for target in success_resolvers[success]:
                    incoming[target].add(action_id + ":success")
            elif not is_system(success):
                errors.append(f"Action {action_id} has invalid success target {success}")

        lowered_id = action_id.lower()
        if any(token in lowered_id for token in destructive_tokens):
            if "confirmation" not in destination and "confirm" not in destination:
                errors.append(f"Destructive action {action_id} must use a confirmation destination")

        if destination in {"game.create", "training.create", "tournament.create", "season.create", "tour.create"}:
            if not {"actorId", "returnTo"}.issubset(context):
                errors.append(f"Creation navigation {action_id} must pass actorId and returnTo")

        if destination == "player.picker":
            required = {"entityType", "actorId", "returnTo"}
            if not required.issubset(context):
                errors.append(f"Player picker action {action_id} is missing {sorted(required - set(context))}")
            if not context.get("entityId") and not context.get("draftId"):
                errors.append(f"Player picker action {action_id} must pass entityId or draftId")

    # Screens without a discoverable entry are warnings: they may still be direct public deep links.
    roots = {"auth.welcome"} | expected_tab_screens
    for screen_id in sorted(screen_by_id):
        if screen_id in roots:
            continue
        if not incoming.get(screen_id):
            warnings.append(f"No registered incoming action/resolver for screen {screen_id}")

    # Block known obsolete concepts from returning to source-of-truth navigation docs.
    legacy_patterns = {
        "Главная · Играть · Чаты · Клубы · Профиль": [DOCS / "UI_RULES.md", DOCS / "APP_MAP.md", ROOT / "AGENTS.md"],
        "## 4. Играть": [DOCS / "APP_MAP.md"],
        "Тренировки и группы": [DOCS / "APP_MAP.md"],
        "Тренировочная группа": [DOCS / "APP_MAP.md"],
        "Открыть оставшиеся места": [DOCS / "APP_MAP.md", DOCS / "ARCHITECTURE_AUDIT.md"],
        "invite_then_public": [DOCS / "PLAYER_DIRECTORY.yaml", DOCS / "DATA_MODEL.md"],
    }
    for phrase, paths in legacy_patterns.items():
        for path in paths:
            if path.is_file() and phrase in path.read_text(encoding="utf-8"):
                errors.append(f"Legacy phrase {phrase!r} remains in {path.relative_to(ROOT)}")

    print(f"Screens: {len(screen_by_id)}")
    print(f"Routes: {len(routes)}")
    print(f"Actions: {len(actions)}")
    print(f"Dynamic destinations: {len(dynamic_destinations)}")
    print(f"Immutable bottom tabs: {len(nav_items)}")

    if warnings:
        print("\nWarnings:")
        for warning in warnings:
            print(f"  - {warning}")

    if errors:
        print("\nErrors:")
        for error in errors:
            print(f"  - {error}")
        return 1

    print("\nNavigation graph validation passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
