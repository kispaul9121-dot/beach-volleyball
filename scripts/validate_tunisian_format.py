#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"


def load_yaml(name: str) -> dict[str, Any]:
    value = yaml.safe_load((DOCS / name).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"docs/{name} must contain a mapping")
    return value


def main() -> int:
    errors: list[str] = []
    ladder = load_yaml("GAME_TUNISIAN_LADDER.yaml")
    matches = load_yaml("GAME_MATCH_TABLE.yaml")
    formats = load_yaml("GAME_FORMATS.yaml")
    game_mvp = load_yaml("GAME_MVP.yaml")
    catalog = load_yaml("GAMES_CATALOG.yaml")
    competitions = load_yaml("COMPETITION_FORMATS.yaml")
    visual = load_yaml("TOURNAMENT_VISUAL_MAP.yaml")

    fmt = ladder.get("format", {}) or {}
    if fmt.get("technical_id") != "rotation_five":
        errors.append("Tunisian ladder technical id must remain rotation_five")
    if fmt.get("product_label") != "Тунисская лестница":
        errors.append("Product label must be Тунисская лестница")
    if fmt.get("entity_type") != "game":
        errors.append("Tunisian ladder must be a game, not a tournament")
    if fmt.get("event_duration") != "one_off_single_date":
        errors.append("Tunisian ladder must be one-off and single-date")
    if fmt.get("season_mode_forbidden") is not True:
        errors.append("Tunisian ladder must forbid season mode")

    config = ladder.get("configuration", {}) or {}
    court_count = config.get("court_count", {}) or {}
    if court_count.get("allowed_values") != [1, 2, 3]:
        errors.append("Tunisian ladder must support exactly one, two or three courts")
    participant_count = config.get("participant_count", {}) or {}
    if participant_count.get("derived_formula") != "court_count_times_5":
        errors.append("Participant count must be derived as court_count × 5")
    if participant_count.get("supported_values") != [5, 10, 15]:
        errors.append("Supported participant counts must be 5, 10 and 15")
    if participant_count.get("editable_independently") is not False:
        errors.append("Tunisian participant count must not be independently editable")

    planned = config.get("planned_match_count_per_court", {}) or {}
    if planned.get("entered_by_organizer") is not True or planned.get("default") != 15:
        errors.append("Matches per court must be organizer-defined and default to 15")
    cycle_count = config.get("cycle_count", {}) or {}
    if cycle_count.get("entered_by_organizer") is not True or cycle_count.get("default") != 1:
        errors.append("Cycle count must be organizer-defined and default to one")
    if cycle_count.get("all_cycles_must_fit_single_event_time_window") is not True:
        errors.append("All cycles must fit one event time window")

    movement = ladder.get("movement_after_cycle", {}) or {}
    if movement.get("enabled") is not True:
        errors.append("Court movement must be enabled when applicable")
    if movement.get("simultaneous_across_boundaries") is not True:
        errors.append("Court movements must be simultaneous")
    if movement.get("organizer_confirmation_required") is not True:
        errors.append("Organizer must confirm court movement")
    if movement.get("final_cycle_behavior") != "show_final_positions_without_creating_another_cycle":
        errors.append("Final cycle must not create another cycle")

    rotation = ((matches.get("lineup_modes", {}) or {}).get("rotation_five", {}) or {})
    if rotation.get("entity_type") != "game":
        errors.append("Match table must keep Tunisian ladder inside games")
    if (rotation.get("court_count", {}) or {}).get("allowed") != [1, 2, 3]:
        errors.append("Match table must support one to three courts")
    if (rotation.get("participant_count", {}) or {}).get("supported") != [5, 10, 15]:
        errors.append("Match table must support 5, 10 and 15 participants")
    if rotation.get("season_mode_forbidden") is not True:
        errors.append("Match table must forbid season mode")
    if rotation.get("tournament_entity_forbidden") is not True:
        errors.append("Match table must forbid a Tunisian tournament entity")

    game_format = ((formats.get("formats", {}) or {}).get("rotation_five", {}) or {})
    if game_format.get("entity_type") != "game":
        errors.append("GAME_FORMATS must classify Tunisian ladder as a game")
    capacity = game_format.get("capacity", {}) or {}
    if capacity.get("court_count_allowed") != [1, 2, 3]:
        errors.append("GAME_FORMATS court count differs")
    if capacity.get("supported_participant_counts") != [5, 10, 15]:
        errors.append("GAME_FORMATS participant counts differ")
    if game_format.get("seasonal_mode_forbidden") is not True:
        errors.append("GAME_FORMATS must forbid seasonal mode")
    if game_format.get("tournament_entity_forbidden") is not True:
        errors.append("GAME_FORMATS must forbid Tunisian tournaments")

    step_two = (((game_mvp.get("creation", {}) or {}).get("steps", {}) or {}).get(2, {}) or {})
    mvp_rotation = ((step_two.get("format_capacity_rules", {}) or {}).get("rotation_five", {}) or {})
    if mvp_rotation.get("entity_type") != "game":
        errors.append("Game creation must create Tunisian ladder as a game")
    if (mvp_rotation.get("court_count", {}) or {}).get("allowed") != [1, 2, 3]:
        errors.append("Game creation must expose one to three courts")
    if (mvp_rotation.get("participant_count", {}) or {}).get("supported") != [5, 10, 15]:
        errors.append("Game creation participant counts differ")
    if mvp_rotation.get("season_mode_forbidden") is not True:
        errors.append("Game creation must forbid season mode")

    tournament_modes = (((catalog.get("categories", {}) or {}).get("tournaments", {}) or {}).get("mode_chips", []) or [])
    if "seasonal" in tournament_modes:
        errors.append("Games catalog must not expose Seasonal")
    if set(tournament_modes) != {"all", "classic", "king_of_the_beach"}:
        errors.append("Tournament catalog modes must be All, Classic and King of the Beach")

    competition_formats = competitions.get("formats", {}) or {}
    if "seasonal_tournament" in competition_formats:
        errors.append("Seasonal tournament format must be removed")
    if "seasonal" in (competitions.get("catalog_modes", {}) or {}):
        errors.append("Seasonal tournament catalog mode must be removed")

    visual_formats = visual.get("format_presentations", {}) or {}
    if "seasonal" in visual_formats:
        errors.append("Tournament visual map must not contain seasonal presentation")
    if "tunisian_court_ladder" in visual_formats:
        errors.append("Tournament visual map must not contain Tunisian ladder")

    forbidden_path = DOCS / "TOURNAMENT_COURT_LADDER.yaml"
    if forbidden_path.exists():
        errors.append("Old Tunisian tournament contract must be deleted")
    if (DOCS / "screens/shared/season-details.md").exists():
        errors.append("Season details screen must be deleted")

    game_create_text = (DOCS / "screens/shared/game-create.md").read_text(encoding="utf-8")
    game_manage_text = (DOCS / "screens/shared/game-manage.md").read_text(encoding="utf-8")
    play_text = (DOCS / "screens/play/main.md").read_text(encoding="utf-8")
    if "1 площадка → 5 игроков" not in game_create_text or "3 площадки → 15 игроков" not in game_create_text:
        errors.append("Game creation spec must show all Tunisian court configurations")
    if "Циклов за игру" not in game_create_text:
        errors.append("Game creation spec must expose same-day cycle count")
    if "Подтвердить переходы" not in game_manage_text:
        errors.append("Game management must confirm court movements")
    if "Сезонной категории и сезонного режима нет" not in play_text:
        errors.append("Games catalog spec must explicitly remove seasons")

    if errors:
        print("Tunisian one-off game validation failed:")
        for error in errors:
            print(f"  - {error}")
        return 1

    print("Tunisian one-off game validation passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
