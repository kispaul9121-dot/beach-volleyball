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
    join = load_yaml(DOCS / "JOIN_FLOW.yaml")
    game_mvp = load_yaml(DOCS / "GAME_MVP.yaml")
    game_matches = load_yaml(DOCS / "GAME_MATCH_TABLE.yaml")
    game_formats = load_yaml(DOCS / "GAME_FORMATS.yaml")
    entity_sections = load_yaml(DOCS / "ENTITY_SECTIONS.yaml")
    routes = load_yaml(DOCS / "ROUTES.yaml").get("routes", []) or []
    screens = load_yaml(DOCS / "SCREENS.yaml").get("screens", []) or []
    actions = load_yaml(DOCS / "ACTIONS.yaml").get("actions", []) or []
    tokens = load_yaml(DOCS / "DESIGN_TOKENS.yaml")

    profile_root = contract.get("profile_root", {}) or {}
    if profile_root.get("management_controls_forbidden") is not True:
        errors.append("Profile must forbid creation and management controls")
    if management.get("principles", [""])[0] != "Profile has no creation or event-management controls":
        errors.append("Management contract must keep Profile clean")

    upcoming = profile_root.get("upcoming_timeline", {}) or {}
    if "invited" in set(upcoming.get("statuses", []) or []):
        errors.append("Unresolved invitations must not appear in Profile participation")
    if "unresolved_invitation" not in set(upcoming.get("excludes", []) or []):
        errors.append("Profile timeline must explicitly exclude unresolved invitations")

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
    if archive.get("product_status") != "approved":
        errors.append("Archive pull-down placement must be approved")
    if archive.get("idle_visibility") != "hidden":
        errors.append("Archive entry must remain hidden while idle")
    if archive.get("permanent_header_button") is not False or archive.get("permanent_tab") is not False:
        errors.append("Archive must not add a permanent button or tab")

    entry = archive.get("entry", {}) or {}
    if entry.get("interaction") != "pull_down_overscroll":
        errors.append("Archive must open through pull-down overscroll")
    thresholds = entry.get("thresholds_dp", {}) or {}
    if thresholds.get("reveal") != 24 or thresholds.get("armed") != 72:
        errors.append("Archive gesture thresholds must remain 24/72 dp")
    if entry.get("release_when_armed") != "open_archive_route_state":
        errors.append("Armed archive gesture must open archive route state")

    conflicts = archive.get("gesture_conflicts", {}) or {}
    if conflicts.get("pull_to_refresh_in_management_mode") != "disabled":
        errors.append("Management pull-to-refresh must be disabled to avoid archive gesture conflict")

    accessibility = archive.get("accessibility", {}) or {}
    if accessibility.get("custom_action_label") != "Открыть архив":
        errors.append("Archive requires an accessibility custom action")
    reduce_motion = accessibility.get("reduce_motion", {}) or {}
    if reduce_motion.get("disable_elastic_stretch") is not True:
        errors.append("Archive gesture must define a Reduce Motion fallback")

    route_states = archive.get("route_states", {}) or {}
    expected_archive_states = {
        "games": ("/play", "mode=archive", "/play?mode=manage"),
        "camps": ("/camps", "mode=archive", "/camps?mode=manage"),
    }
    for name, (route, query, back_destination) in expected_archive_states.items():
        state = route_states.get(name, {}) or {}
        if state.get("route") != route or state.get("query") != query:
            errors.append(f"{name} archive route state differs")
        if state.get("back_destination") != back_destination:
            errors.append(f"{name} archive back destination differs")

    if find(routes, "path", "/manage"):
        errors.append("Standalone /manage route must be removed")
    if find(screens, "id", "management.center"):
        errors.append("Standalone management.center screen must be removed")

    for path in ("/play", "/camps"):
        route = find(routes, "path", path)
        accepted = set((route or {}).get("accepts_query", []) or [])
        if not {"mode", "actorId"}.issubset(accepted):
            errors.append(f"{path} must accept contextual management and archive mode")
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
        "entity.start_join_flow", "entity.open_payment", "entity.open_chat", "players.open_picker",
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
    games_archive = games.get("management_mode", {}).get("archive_entry", {}) or {}
    if games_archive.get("interaction") != "pull_down_overscroll_at_scroll_top":
        errors.append("Games catalog must expose the approved archive gesture")
    if games_archive.get("visible_button_forbidden") is not True:
        errors.append("Games archive must not add a visible button")

    # Approved join policy and own-row payment.
    if join.get("product_status") != "approved":
        errors.append("Join flow must be approved")
    enrollment = (((join.get("organizer_configuration", {}) or {}).get("enrollment_policy", {}) or {}).get("values", {}) or {})
    payment = (((join.get("organizer_configuration", {}) or {}).get("payment_policy", {}) or {}).get("values", {}) or {})
    if set(enrollment) != {"immediate", "approval", "invitation_only"}:
        errors.append("Join enrollment policies differ")
    if set(payment) != {"free", "online", "external"}:
        errors.append("Join payment policies differ")
    payment_surface = join.get("participant_payment_surface", {}) or {}
    own_online = ((payment_surface.get("own_row", {}) or {}).get("online_unpaid", {}) or {})
    if own_online.get("label") != "Оплатить" or own_online.get("permission") != "payment_owner":
        errors.append("Own participant row must expose payment-owner-only Оплатить")
    if "paying_for_another_participant_is_forbidden" not in set(payment_surface.get("rules", []) or []):
        errors.append("Paying for another participant must remain forbidden")

    # Four-step game creation with explicit capacity and venue validation.
    creation = game_mvp.get("creation", {}) or {}
    steps = creation.get("steps", {}) or {}
    if set(steps) != {1, 2, 3, 4}:
        errors.append("Game creation must contain exactly four steps")
    step_two = steps.get(2, {}) or {}
    capacity = step_two.get("participant_capacity", {}) or {}
    if capacity.get("entered_by_organizer") is not True or capacity.get("auto_only_forbidden") is not True:
        errors.append("Game participant capacity must be entered by the organizer")
    if (step_two.get("venue_limit", {}) or {}).get("publish_blocked_when_exceeded") is not True:
        errors.append("Venue player limit must block publication")

    # One-off game management and universal match table.
    game_management = game_mvp.get("management", {}) or {}
    if game_management.get("sections") != ["overview", "participants", "matches", "chat"]:
        errors.append("Game MVP sections must be Overview, Participants, Matches and Chat")
    forbidden_sections = set(game_management.get("forbidden_separate_sections", []) or [])
    if not {"settings", "payments", "tournament_bracket"}.issubset(forbidden_sections):
        errors.append("Game MVP must forbid separate Settings, Payments and tournament bracket")

    matches = game_management.get("matches", {}) or {}
    if matches.get("mandatory_for_every_one_off_game") is not True:
        errors.append("Every one-off game must have a match table")
    if matches.get("tournament_visual_map_forbidden") is not True:
        errors.append("One-off games must not use tournament visual maps")
    participant_permissions = matches.get("participant_permissions", {}) or {}
    if participant_permissions.get("participant_can_enter_score") is not False:
        errors.append("Participants must not enter one-off game scores")
    if participant_permissions.get("participant_can_confirm_result") is not False:
        errors.append("Participants must not confirm one-off game results")
    result_entry = matches.get("result_entry", {}) or {}
    if result_entry.get("permission") != "entity_manager" or result_entry.get("organizer_only_ui") is not True:
        errors.append("One-off game result entry must be organizer-only")
    if result_entry.get("save_directly_without_opponent_confirmation") is not True:
        errors.append("Organizer results must not require opponent confirmation")
    if result_entry.get("participant_conflict_flow_forbidden") is not True:
        errors.append("Participant score conflict flow must remain forbidden")

    if game_matches.get("product_status") != "approved":
        errors.append("One-off match table must be approved")
    result_permissions = game_matches.get("result_permissions", {}) or {}
    participant_result = result_permissions.get("confirmed_participant", {}) or {}
    manager_result = result_permissions.get("organizer_or_authorized_staff", {}) or {}
    if participant_result.get("can_enter") is not False or participant_result.get("can_confirm") is not False:
        errors.append("Match-table participants must remain read-only")
    if manager_result.get("can_enter_any_match") is not True:
        errors.append("Organizer must be able to enter every one-off match result")
    lifecycle = game_matches.get("result_lifecycle", {}) or {}
    if lifecycle.get("participant_confirmation_required") is not False:
        errors.append("One-off results must not require participant confirmation")
    if lifecycle.get("participant_score_conflict_flow_forbidden") is not True:
        errors.append("One-off result contract must forbid participant score conflicts")

    formats = game_formats.get("formats", {}) or {}
    for format_id in ("standard_2x2", "standard_4x4", "rotation_five", "fixed_team_match"):
        view = (formats.get(format_id, {}) or {}).get("one_off_game_view", {}) or {}
        if view.get("primary") != "match_table":
            errors.append(f"{format_id} must use the one-off match table")
        if view.get("score_entry_permission") != "entity_manager":
            errors.append(f"{format_id} score entry must be organizer-only")
        if view.get("participant_score_view") != "read_only":
            errors.append(f"{format_id} participant score view must be read-only")

    game_sections = ((entity_sections.get("entity_types", {}) or {}).get("game", {}) or {})
    if game_sections.get("manager_sections") != ["overview", "participants", "matches", "chat"]:
        errors.append("Entity sections must mirror the game MVP sections")
    score_entry = ((game_sections.get("matches", {}) or {}).get("score_entry", {}) or {})
    if score_entry.get("confirmed_participant") != "read_only":
        errors.append("Entity section must keep participant results read-only")
    if score_entry.get("participant_confirmation_required") is not False:
        errors.append("Entity section must not require participant result confirmation")

    game_chat = game_management.get("chat", {}) or {}
    if game_chat.get("mandatory_in_mvp") is not True:
        errors.append("Game chat must be mandatory in MVP")
    if game_chat.get("also_visible_in_global_chats") is not True:
        errors.append("Game chat must also appear in global Chats")
    if game_chat.get("duplicate_conversation_creation_forbidden") is not True:
        errors.append("Game manage and global Chats must share one conversation")

    home_text = (DOCS / "screens/home/main.md").read_text(encoding="utf-8")
    play_text = (DOCS / "screens/play/main.md").read_text(encoding="utf-8")
    camps_text = (DOCS / "screens/camps/main.md").read_text(encoding="utf-8")
    game_manage_text = (DOCS / "screens/shared/game-manage.md").read_text(encoding="utf-8")
    game_details_text = (DOCS / "screens/shared/game-details.md").read_text(encoding="utf-8")
    if "кнопка `+` отсутствует" not in home_text:
        errors.append("Profile spec must explicitly remove +")
    if "Режим управления" not in play_text or "+ Создать" not in play_text:
        errors.append("Games spec must expose management and creation")
    if "Режим управления" not in camps_text or "+ Создать кэмп" not in camps_text:
        errors.append("Camps spec must expose management and creation")
    for name, text, archive_route in (
        ("Games", play_text, "/play?mode=archive"),
        ("Camps", camps_text, "/camps?mode=archive"),
    ):
        lowered = text.lower()
        if "Активные · Завершённые" in text:
            errors.append(f"{name} spec restored Active/Completed controls")
        if "Потяните ещё, чтобы открыть" not in text or "Отпустите, чтобы открыть" not in text:
            errors.append(f"{name} spec must describe both archive gesture stages")
        if archive_route not in text:
            errors.append(f"{name} spec must declare archive route state")
        if "pull-to-refresh" not in lowered or "отключ" not in lowered:
            errors.append(f"{name} spec must resolve pull-to-refresh conflict")
        if "Открыть архив" not in text:
            errors.append(f"{name} spec must include accessibility archive action")

    if "результаты вводит только организатор" not in game_manage_text.lower():
        errors.append("Game manage spec must explicitly restrict result entry to organizer")
    if "обычный участник не вводит и не подтверждает счёт" not in game_details_text.lower():
        errors.append("Game details spec must explicitly keep participant results read-only")

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
