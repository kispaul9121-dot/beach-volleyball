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
    matches = load_yaml("GAME_MATCH_TABLE.yaml")
    formats = load_yaml("GAME_FORMATS.yaml")
    game_mvp = load_yaml("GAME_MVP.yaml")
    tournament = load_yaml("TOURNAMENT_COURT_LADDER.yaml")
    visual = load_yaml("TOURNAMENT_VISUAL_MAP.yaml")

    rotation = ((matches.get("lineup_modes", {}) or {}).get("rotation_five", {}) or {})
    participant_count = rotation.get("participant_count", {}) or {}
    if participant_count.get("exact") != 5:
        errors.append("One-off mixed-pair game must have exactly five participants")

    planned = rotation.get("planned_match_count", {}) or {}
    if planned.get("entered_by_organizer") is not True:
        errors.append("Five-player match count must be entered separately by organizer")
    if planned.get("default") != 15 or planned.get("minimum") != 1:
        errors.append("Five-player match count must default to 15 and allow positive integers")

    unique_cycle = rotation.get("unique_cycle", {}) or {}
    if unique_cycle.get("unique_match_count") != 15:
        errors.append("Five-player game must define fifteen unique match compositions")
    generation = rotation.get("generation", {}) or {}
    if generation.get("when_exactly_fifteen") != "complete_unique_cycle":
        errors.append("Fifteen matches must generate the complete unique cycle")
    if generation.get("when_more_than_fifteen") != "append_new_shuffled_cycles_with_repeats":
        errors.append("More than fifteen matches must be represented as repeated shuffled cycles")

    game_format = ((formats.get("formats", {}) or {}).get("rotation_five", {}) or {})
    capacity = game_format.get("capacity", {}) or {}
    if capacity.get("exact_players") != 5 or capacity.get("publish_blocked_when_not_exactly_five") is not True:
        errors.append("GAME_FORMATS must block non-five-player one-off rotation")
    match_count = game_format.get("match_count", {}) or {}
    if match_count.get("entered_by_organizer") is not True or match_count.get("default") != 15:
        errors.append("GAME_FORMATS must keep participant count and match count independent")

    mvp_rotation = (((game_mvp.get("creation", {}) or {}).get("steps", {}) or {}).get(2, {}) or {}).get("format_capacity_rules", {}) or {}
    mvp_rotation = mvp_rotation.get("rotation_five", {}) or {}
    if mvp_rotation.get("exact_players") != 5:
        errors.append("Game creation must require exactly five players for mixed pairs")
    mvp_matches = ((((game_mvp.get("management", {}) or {}).get("matches", {}) or {}).get("generation", {}) or {}).get("rotation_five", {}) or {})
    if mvp_matches.get("planned_match_count_entered_by_organizer") is not True:
        errors.append("Game MVP must expose a separate planned match count")
    if mvp_matches.get("unique_cycle_match_count") != 15:
        errors.append("Game MVP must preserve the fifteen-match unique cycle")
    if mvp_matches.get("more_than_five_players_forbidden") is not True:
        errors.append("One-off game must forbid more than five participants in this format")

    tournament_format = tournament.get("format", {}) or {}
    if tournament_format.get("id") != "tunisian_court_ladder":
        errors.append("Multi-court tournament id must be tunisian_court_ladder")
    if tournament_format.get("product_label") != "Тунисский формат":
        errors.append("Russian product label must be Тунисский формат")
    if tournament_format.get("minimum_court_count") != 2:
        errors.append("Tunisian tournament must require more than one court")

    configurations = tournament_format.get("supported_mvp_configurations", {}) or {}
    expected = {
        "ten_players": (10, 2),
        "fifteen_players": (15, 3),
    }
    for name, (players, courts) in expected.items():
        config = configurations.get(name, {}) or {}
        if config.get("participant_count") != players or config.get("court_count") != courts:
            errors.append(f"{name} configuration must be {players} players on {courts} courts")
        if config.get("players_per_court") != 5:
            errors.append(f"{name} must keep exactly five players per court")

    one_court = tournament_format.get("one_court_destination", {}) or {}
    if one_court.get("entity_type") != "game" or one_court.get("format") != "rotation_five":
        errors.append("One court with five players must resolve to a one-off game")

    cycle = tournament.get("cycle", {}) or {}
    cycle_matches = cycle.get("planned_match_count_per_court", {}) or {}
    if cycle_matches.get("entered_by_organizer") is not True or cycle_matches.get("default") != 15:
        errors.append("Each Tunisian court cycle must have organizer-defined matches, default 15")

    movement = tournament.get("movement_after_cycle", {}) or {}
    if movement.get("enabled") is not True or movement.get("simultaneous_across_boundaries") is not True:
        errors.append("Court movements must be enabled and simultaneous")
    upward = movement.get("upward", {}) or {}
    downward = movement.get("downward", {}) or {}
    if upward.get("source") != "rank_1_of_lower_court" or upward.get("destination") != "next_higher_court":
        errors.append("Leader of the lower court must move upward")
    if downward.get("source") != "rank_5_of_higher_court" or downward.get("destination") != "next_lower_court":
        errors.append("Last player of the higher court must move downward")

    research = tournament.get("research_note", {}) or {}
    if research.get("official_fivb_or_vfv_standard") is not False:
        errors.append("Tunisian format must be documented as a community, not official, standard")
    if research.get("rule_variation_warning") is None:
        errors.append("Tunisian format must warn that community rules vary")

    visual_format = ((visual.get("format_presentations", {}) or {}).get("tunisian_court_ladder", {}) or {})
    if visual_format.get("primary") != "stacked_court_ladder":
        errors.append("Tournament visual map must include the stacked Tunisian court ladder")

    create_text = (DOCS / "screens/shared/game-create.md").read_text(encoding="utf-8")
    tournament_text = (DOCS / "screens/shared/tournament-details.md").read_text(encoding="utf-8")
    manage_text = (DOCS / "screens/shared/tournament-manage.md").read_text(encoding="utf-8")
    if "Количество игроков: 5" not in create_text or "Количество матчей: 15" not in create_text:
        errors.append("Game creation spec must show separate five-player and match-count fields")
    if "Тунисский формат" not in tournament_text or "10 игроков → 2 площадки по 5" not in tournament_text:
        errors.append("Tournament details must describe the Tunisian format")
    if "Подтвердить переходы" not in manage_text:
        errors.append("Tournament management must explicitly confirm court movements")

    if errors:
        print("Tunisian format validation failed:")
        for error in errors:
            print(f"  - {error}")
        return 1

    print("Tunisian format validation passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
