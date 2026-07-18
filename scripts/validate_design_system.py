#!/usr/bin/env python3
"""Validate the VolleyPlay cross-platform UI design contract."""

from __future__ import annotations

import re
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
        raise ValueError(f"{path} must contain a YAML mapping")
    return value


def nested(value: dict[str, Any], *keys: str) -> Any:
    current: Any = value
    for key in keys:
        if not isinstance(current, dict) or key not in current:
            return None
        current = current[key]
    return current


def main() -> int:
    errors: list[str] = []

    tokens = load_yaml(DOCS / "DESIGN_TOKENS.yaml")
    nav = load_yaml(DOCS / "NAVIGATION_RESOLVERS.yaml")

    expected_tabs = [
        {"id": "home", "title": "Профиль", "route": "/"},
        {"id": "play", "title": "События", "route": "/play"},
        {"id": "chats", "title": "Чаты", "route": "/chats"},
        {"id": "clubs", "title": "Клубы", "route": "/clubs"},
        {"id": "profile", "title": "Настройки", "route": "/profile"},
    ]

    if tokens.get("platforms") != ["ios", "android"]:
        errors.append("DESIGN_TOKENS platforms must be exactly [ios, android]")

    if nested(tokens, "appearance", "required_primary_mode") != "dark":
        errors.append("Dark theme must remain the required primary mode")
    if nested(tokens, "appearance", "hardcoded_color_values_allowed") is not False:
        errors.append("Hard-coded color values must remain forbidden")
    if nested(tokens, "appearance", "palette_approved") is not False:
        errors.append("Color palette must remain pending until explicitly approved")

    target = nested(tokens, "interaction", "minimum_touch_target") or {}
    if target.get("width") != 48 or target.get("height") != 48:
        errors.append("Minimum touch target must be 48x48 on both platforms")

    tab_items = nested(tokens, "navigation", "bottom_tabs", "items")
    if tab_items != expected_tabs:
        errors.append("DESIGN_TOKENS bottom tabs differ from the immutable five-tab contract")

    resolver_items = nested(nav, "bottom_navigation", "items") or []
    resolver_projection = [
        {"id": item.get("id"), "title": item.get("title"), "route": item.get("route")}
        for item in resolver_items
        if isinstance(item, dict)
    ]
    if resolver_projection != expected_tabs:
        errors.append("NAVIGATION_RESOLVERS bottom tabs differ from DESIGN_TOKENS")

    chip = nested(tokens, "chips", "filter_chip") or {}
    if chip.get("overflow_behavior") != "single_row_horizontal_scroll":
        errors.append("Overflowing chips must use one horizontally scrolling row")
    if chip.get("wrap_allowed_by_default") is not False:
        errors.append("Filter chips must not wrap by default")
    if chip.get("minimum_touch_height") != 48:
        errors.append("Filter chip touch height must be 48")

    icons = tokens.get("icons", {}) or {}
    if icons.get("primary_library") != "lucide-react-native":
        errors.append("Lucide React Native must remain the primary product icon library")
    if nested(tokens, "icons", "sizes", "default") != 24:
        errors.append("Default product icon size must be 24")
    if icons.get("default_stroke_width") != 2:
        errors.append("Default product icon stroke width must be 2")

    required_motion = set(nested(tokens, "libraries", "required", "motion") or [])
    expected_motion = {
        "react-native-reanimated",
        "react-native-worklets",
        "react-native-gesture-handler",
    }
    if required_motion != expected_motion:
        errors.append("Motion libraries must be Reanimated, Worklets and Gesture Handler")
    if nested(tokens, "motion", "reduce_motion", "required") is not True:
        errors.append("Reduce Motion support must remain mandatory")

    required_icons = set(nested(tokens, "libraries", "required", "icons") or [])
    if required_icons != {"lucide-react-native", "react-native-svg"}:
        errors.append("Icon dependencies must remain Lucide React Native and react-native-svg")

    required_navigation = set(nested(tokens, "libraries", "required", "navigation") or [])
    expected_navigation = {"expo-router", "react-native-screens", "react-native-safe-area-context"}
    if required_navigation != expected_navigation:
        errors.append("Navigation dependencies differ from the approved Expo baseline")

    required_components = nested(tokens, "component_catalog", "required_components") or []
    if len(required_components) != len(set(required_components)):
        errors.append("Component catalog contains duplicate component names")
    for component in ("AppTabBar", "ScreenHeader", "Button", "FilterChip", "AppIcon"):
        if component not in required_components:
            errors.append(f"Required UI component is missing: {component}")

    widths = nested(tokens, "responsive", "required_test_widths")
    if widths != [320, 360, 390, 430]:
        errors.append("Required phone test widths must remain 320, 360, 390 and 430")
    if nested(tokens, "typography", "minimum_test_scale_percent") != 200:
        errors.append("Text scaling test must remain 200 percent")

    design_system_text = (DOCS / "DESIGN_SYSTEM.md").read_text(encoding="utf-8")
    if re.search(r"#[0-9a-fA-F]{3}(?:[0-9a-fA-F]{3})?\b", design_system_text):
        errors.append("DESIGN_SYSTEM.md contains a hard-coded hex color")

    ui_rules = (DOCS / "UI_RULES.md").read_text(encoding="utf-8")
    agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
    for file_name, content in (("UI_RULES.md", ui_rules), ("AGENTS.md", agents)):
        if "DESIGN_SYSTEM.md" not in content or "DESIGN_TOKENS.yaml" not in content:
            errors.append(f"{file_name} must reference both design system sources")

    print("Design system contract:")
    print(f"  platforms: {tokens.get('platforms')}")
    print(f"  minimum touch target: {target.get('width')}x{target.get('height')}")
    print(f"  bottom tabs: {len(tab_items or [])}")
    print(f"  required components: {len(required_components)}")

    if errors:
        print("\nErrors:")
        for error in errors:
            print(f"  - {error}")
        return 1

    print("\nDesign system validation passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
