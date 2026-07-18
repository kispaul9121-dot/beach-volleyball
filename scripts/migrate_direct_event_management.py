#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
from typing import Any
import re
import yaml

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"


def load_yaml(path: Path) -> dict[str, Any]:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a mapping")
    return value


def save_yaml(path: Path, value: dict[str, Any]) -> None:
    path.write_text(
        yaml.safe_dump(value, allow_unicode=True, sort_keys=False, width=110),
        encoding="utf-8",
    )


def find(items: list[dict[str, Any]], key: str, value: str) -> dict[str, Any] | None:
    return next((item for item in items if str(item.get(key, "")) == value), None)


def upsert(items: list[dict[str, Any]], key: str, value: str, item: dict[str, Any], after: str | None = None) -> None:
    current = find(items, key, value)
    if current is not None:
        current.clear()
        current.update(item)
        return
    if after:
        for index, existing in enumerate(items):
            if str(existing.get(key, "")) == after:
                items.insert(index + 1, item)
                return
    items.append(item)


def remove_ids(items: list[dict[str, Any]], ids: set[str]) -> list[dict[str, Any]]:
    return [item for item in items if str(item.get("id", "")) not in ids]


def replace_recursively(value: Any, replacements: dict[str, str]) -> Any:
    if isinstance(value, dict):
        return {key: replace_recursively(item, replacements) for key, item in value.items()}
    if isinstance(value, list):
        return [replace_recursively(item, replacements) for item in value]
    if isinstance(value, str):
        result = value
        for old, new in replacements.items():
            result = result.replace(old, new)
        return result
    return value


def append_section(path: Path, marker: str, section: str) -> None:
    text = path.read_text(encoding="utf-8")
    if marker not in text:
        path.write_text(text.rstrip() + "\n\n" + section.strip() + "\n", encoding="utf-8")


# ---------------------------------------------------------------------------
# Source-of-truth contracts
# ---------------------------------------------------------------------------
profile_activity = {
    "version": 2,
    "scope": "profile_activity",
    "source_of_truth_for": [
        "personal participation preview on home.main",
        "unified personal activity list",
        "management outside Profile",
        "post-join Profile tab feedback",
        "discovery-only boundaries for Games and Camps",
    ],
    "catalog_boundaries": {
        "games": {
            "screen": "play.main",
            "route": "/play",
            "mode": "discovery_only",
            "allows": ["browse", "search", "filter", "open_by_capability", "start_join_flow"],
            "forbids": ["participating_tab", "managing_tab", "personal_archive", "management_dashboard"],
        },
        "camps": {
            "screen": "camps.main",
            "route": "/camps",
            "mode": "discovery_only",
            "allows": ["browse", "search", "filter", "open_by_capability", "start_join_flow"],
            "forbids": ["participating_tab", "managing_tab", "personal_archive", "management_dashboard"],
        },
    },
    "profile_root": {
        "screen": "home.main",
        "route": "/",
        "mode": "personal_profile_and_participation",
        "management_controls_forbidden": True,
        "connections_contract": "docs/PROFILE_CONNECTIONS.yaml",
        "upcoming_timeline": {
            "title": "Ближайшее",
            "entity_types": ["game", "training", "tournament", "camp"],
            "ordering": "starts_at_ascending",
            "maximum_preview_items": 4,
            "statuses": ["invited", "requested", "payment_required", "waitlisted", "confirmed"],
            "shows": ["date", "time", "type", "title", "place", "participation_status", "required_action"],
            "excludes": ["draft", "manager_only_task", "staff_operation"],
        },
        "activity_entry": {
            "label": "Вся моя активность",
            "action_id": "home.open_activity",
            "screen": "profile.activity",
            "route": "/activity",
        },
    },
    "activity_screen": {
        "screen": "profile.activity",
        "route": "/activity",
        "purpose": "all personal participation across entity types",
        "tabs": ["upcoming", "past"],
        "tab_labels": {"upcoming": "Предстоящие", "past": "Прошедшие"},
        "type_filters": ["all", "games", "trainings", "tournaments", "camps"],
        "type_labels": {
            "all": "Все",
            "games": "Игры",
            "trainings": "Тренировки",
            "tournaments": "Турниры",
            "camps": "Кэмпы",
        },
        "management_items_forbidden": True,
        "empty_upcoming_action": "Открыть Игры",
        "empty_past_copy": "Завершённые участия появятся здесь",
    },
    "legacy_filtered_activity_screens": {
        "profile.my_games": {"route": "/profile/games", "fixed_type": "games", "tabs": ["upcoming", "past"]},
        "profile.trainings": {"route": "/profile/trainings", "fixed_type": "trainings", "tabs": ["booked", "past"]},
        "profile.competitions": {"route": "/profile/competitions", "fixed_type": "tournaments", "tabs": ["registered", "past"]},
        "profile.trips": {"route": "/profile/trips", "fixed_type": "camps", "tabs": ["booked", "past"]},
    },
    "management": {
        "source_of_truth": "docs/MANAGEMENT_CENTER.yaml",
        "profile_embedding_forbidden": True,
        "center_screen": "management.center",
        "center_route": "/manage",
        "primary_entry": "system.create_menu",
        "catalog_entry": "dynamic.catalog_entity_entry",
    },
    "join_flow": {
        "product_status": "definition_pending",
        "entry_action_id": "entity.start_join_flow",
        "entry_label": "Вступить",
        "resolver": "system.resolve_join_flow",
        "possible_future_outcomes": [
            "free_immediate_confirmation",
            "paid_checkout",
            "organizer_approval",
            "waitlist",
            "invitation_only",
        ],
        "rule": "do_not_expose_a_final_join_mechanism_until_the_product_decision_is_approved",
    },
    "profile_tab_feedback": {
        "trigger": "profile_activity_item_created_or_updated_after_join_flow",
        "bottom_tab_id": "home",
        "duration_ms": 900,
        "repetitions": 1,
        "confirmed": {"semantic_color": "status.success", "badge": "check", "message": "Игра добавлена в Профиль"},
        "pending_or_payment_required": {"semantic_color": "status.info", "badge": "dot", "message": "Статус вступления сохранён в Профиле"},
        "rules": [
            "never_loop",
            "never_move_or_resize_the_tab_bar",
            "do_not_use_color_as_the_only_signal",
            "respect_reduce_motion",
            "feedback_does_not_mean_confirmed_when_status_is_pending",
        ],
        "reduce_motion_fallback": "static_badge_and_accessibility_announcement",
    },
}
save_yaml(DOCS / "PROFILE_ACTIVITY.yaml", profile_activity)

management_contract = {
    "version": 1,
    "scope": "event_management_entry",
    "source_of_truth_for": [
        "capability-aware event opening from catalogs",
        "create and manage menu",
        "management center",
        "return paths from entity management",
    ],
    "principles": [
        "Profile never embeds an Участвую / Управляю switch",
        "a user with current manage permission opens the management screen directly from a catalog card",
        "a user without manage permission opens the public detail screen",
        "server authorization is authoritative; client capability hints are never sufficient",
        "public detail and management remain separate screen modes and routes",
    ],
    "catalog_tap": {
        "action_ids": ["games.open_entity", "camps.open_camp"],
        "resolver": "dynamic.catalog_entity_entry",
        "requires": ["entityType", "entityId", "activeActorId", "canManageHint"],
        "decision": {
            "authorized_manager": "dynamic.entity_manage",
            "other_user": "dynamic.entity_details",
        },
        "permission_check": "server_revalidate_before_manage_screen_data",
        "revoked_permission_fallback": "dynamic.entity_details_with_permission_changed_notice",
    },
    "create_menu": {
        "overlay": "system.create_menu",
        "entry_action": "global.open_create_menu",
        "sections": {
            "create": ["game", "training", "tournament", "camp"],
            "management": ["all_events", "drafts", "requests_and_participants", "payments"],
        },
        "management_destination": "management.center",
    },
    "center": {
        "screen": "management.center",
        "route": "/manage",
        "tabs": ["active", "completed"],
        "tab_labels": {"active": "Активные", "completed": "Завершённые"},
        "type_filters": ["all", "games", "trainings", "tournaments", "camps"],
        "active_includes": ["drafts", "published", "requires_action", "registration_open", "in_progress", "cancelled_not_archived"],
        "card_fields": [
            "actor_profile",
            "type",
            "title",
            "date",
            "publication_status",
            "capacity",
            "requests",
            "unpaid",
            "next_management_action",
        ],
        "card_action": "management.open_entity",
        "create_action": "management.open_create_menu",
    },
    "return_policy": {
        "game": "/manage?tab=active&type=games",
        "training": "/manage?tab=active&type=trainings",
        "tournament": "/manage?tab=active&type=tournaments",
        "camp": "/manage?tab=active&type=camps",
        "restore": ["tab", "type", "filters", "scroll_position"],
    },
}
save_yaml(DOCS / "MANAGEMENT_CENTER.yaml", management_contract)

# Compact connection rail, not three stacked sections.
connections = load_yaml(DOCS / "PROFILE_CONNECTIONS.yaml")
connections.setdefault("placement", {}).update({
    "screen": "home.main",
    "position": "after_profile_header_before_upcoming_timeline",
    "component": "ConnectionRail",
    "layout": "single_horizontal_connection_rail",
    "full_lists_are_not_rendered_on_home": True,
})
connections["naming"] = {
    "section_title": None,
    "accessible_group_label": "Мои связи",
    "forbidden_section_titles": ["Подписки", "Друзья", "Моё окружение"],
    "rationale": [
        "the rail is part of the profile summary rather than a separate content section",
        "trainer relationship is not a subscription",
        "saved player is not mutual friendship",
        "following an organization is not necessarily paid",
    ],
}
connections["row_ui"] = {
    "presentation": "three_compact_cards_in_one_horizontal_rail",
    "card_min_width": 112,
    "card_max_width": 144,
    "minimum_touch_height": 72,
    "leading": "avatar_or_logo_stack",
    "center": "short_title_and_count",
    "trailing": "chevron_optional",
    "horizontal_scroll_when_needed": True,
    "full_width_stacked_rows_forbidden": True,
    "nested_primary_buttons_forbidden": True,
}
rules = connections.get("rules", []) or []
for rule in [
    "render one compact rail rather than three vertical home sections",
    "the rail must not push the upcoming timeline below the first meaningful viewport",
]:
    if rule not in rules:
        rules.append(rule)
connections["rules"] = rules
save_yaml(DOCS / "PROFILE_CONNECTIONS.yaml", connections)

# Games catalog opens by capability.
games = load_yaml(DOCS / "GAMES_CATALOG.yaml")
games.setdefault("bottom_tab", {})["capabilities"] = [
    "browse", "search", "filter", "open_by_capability", "start_join_flow"
]
games["catalog_open_policy"] = {
    "action_id": "games.open_entity",
    "resolver": "dynamic.catalog_entity_entry",
    "manager_result": "dynamic.entity_manage",
    "public_result": "dynamic.entity_details",
    "rules": [
        "canManageHint is only an optimization and must be revalidated by the server",
        "revoked permission falls back to public details with a clear notice",
        "returning from manage restores catalog category, filters and scroll position",
    ],
}
games["personal_activity"] = {
    "home_preview": "home.main",
    "full_list": "profile.activity",
    "management": "management.center",
    "catalog_tabs_forbidden": ["participating", "managing"],
}
save_yaml(DOCS / "GAMES_CATALOG.yaml", games)

# ---------------------------------------------------------------------------
# Screens
# ---------------------------------------------------------------------------
screens_doc = load_yaml(DOCS / "SCREENS.yaml")
screens = screens_doc.get("screens", []) or []
home = find(screens, "id", "home.main")
if home:
    home["purpose"] = "Личный профиль active actor: компактные связи, ближайшие участия и переход ко всей личной активности без управления событиями."

upsert(screens, "id", "profile.activity", {
    "id": "profile.activity",
    "title": "Вся моя активность",
    "route": "/activity",
    "section": "home",
    "spec": "docs/screens/profile/activity.md",
    "purpose": "Единая личная лента участий: Предстоящие / Прошедшие с фильтрами по типу.",
    "variants": ["player", "trainer_as_player"],
    "back_fallback": "/",
}, after="home.main")

upsert(screens, "id", "management.center", {
    "id": "management.center",
    "title": "Центр управления",
    "route": "/manage",
    "section": "management",
    "spec": "docs/screens/shared/management-center.md",
    "purpose": "Единый список управляемых игр, тренировок, турниров и кэмпов с переходом в кабинет конкретной сущности.",
    "variants": ["player", "trainer", "organization"],
    "permission": "authenticated_with_manageable_entities_or_create_capability",
    "back_fallback": "/",
}, after="profile.activity")

purpose_updates = {
    "profile.my_games": "Совместимый фильтр личной активности по играм: Предстоящие / Прошедшие; управление здесь не показывается.",
    "profile.trainings": "Совместимый фильтр личной активности по тренировкам: Записан / Прошедшие; управление здесь не показывается.",
    "profile.competitions": "Совместимый фильтр личной активности по турнирам: Заявлен / Прошедшие; управление здесь не показывается.",
    "profile.trips": "Совместимый фильтр личной активности по кэмпам: Записан / Прошедшие; управление здесь не показывается.",
}
for screen_id, purpose in purpose_updates.items():
    item = find(screens, "id", screen_id)
    if item:
        item["purpose"] = purpose
screens_doc["screens"] = screens
save_yaml(DOCS / "SCREENS.yaml", screens_doc)

# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
routes_doc = load_yaml(DOCS / "ROUTES.yaml")
routes = routes_doc.get("routes", []) or []
home_route = find(routes, "path", "/")
if home_route:
    home_route["accepts_query"] = ["highlightEntityType", "highlightEntityId"]

upsert(routes, "path", "/activity", {
    "path": "/activity",
    "screen": "profile.activity",
    "navigator": "home_stack",
    "parent": "/",
    "access": "authenticated_onboarded",
    "accepts_query": ["tab", "type", "status", "actorId", "highlightEntityType", "highlightEntityId"],
    "back_fallback": "/",
}, after="/")
upsert(routes, "path", "/manage", {
    "path": "/manage",
    "screen": "management.center",
    "navigator": "home_stack",
    "parent": "/",
    "access": "authenticated_onboarded",
    "permission": "authenticated_with_manageable_entities_or_create_capability",
    "accepts_query": ["tab", "type", "status", "actorId", "highlightEntityType", "highlightEntityId"],
    "back_fallback": "/",
}, after="/activity")

for path in ("/profile/games", "/profile/trainings", "/profile/competitions", "/profile/trips"):
    route = find(routes, "path", path)
    if route:
        route["navigator"] = "home_stack"
        route["parent"] = "/"
        route["accepts_query"] = ["tab", "actorId"]
        route["back_fallback"] = "/activity"

fallbacks = {
    "/games/create": "/manage?tab=active&type=games",
    "/games/:gameId/manage": "/manage?tab=active&type=games",
    "/trainings/create": "/manage?tab=active&type=trainings",
    "/trainings/:trainingId/manage": "/manage?tab=active&type=trainings",
    "/tournaments/create": "/manage?tab=active&type=tournaments",
    "/tournaments/:tournamentId/manage": "/manage?tab=active&type=tournaments",
    "/tours/create": "/manage?tab=active&type=camps",
    "/tours/:tourId/manage": "/manage?tab=active&type=camps",
}
for path, fallback in fallbacks.items():
    route = find(routes, "path", path)
    if route:
        route["back_fallback"] = fallback
routes_doc["routes"] = routes
save_yaml(DOCS / "ROUTES.yaml", routes_doc)

# ---------------------------------------------------------------------------
# Dynamic resolver
# ---------------------------------------------------------------------------
resolvers = load_yaml(DOCS / "NAVIGATION_RESOLVERS.yaml")
dynamic_destinations = resolvers.get("dynamic_destinations", []) or []
upsert(dynamic_destinations, "id", "dynamic.catalog_entity_entry", {
    "id": "dynamic.catalog_entity_entry",
    "requires_context": ["entityType", "entityId", "activeActorId", "canManageHint"],
    "decision": {
        "authorized_after_server_check": "dynamic.entity_manage",
        "not_authorized": "dynamic.entity_details",
        "permission_revoked": "dynamic.entity_details",
    },
    "resolves_to": [
        "game.details", "training.details", "tournament.details", "tour.details",
        "game.manage", "training.manage", "tournament.manage", "tour.manage",
    ],
}, after="dynamic.entity_details")
resolvers["dynamic_destinations"] = dynamic_destinations
save_yaml(DOCS / "NAVIGATION_RESOLVERS.yaml", resolvers)

# ---------------------------------------------------------------------------
# Actions
# ---------------------------------------------------------------------------
actions_doc = load_yaml(DOCS / "ACTIONS.yaml")
actions = actions_doc.get("actions", []) or []
actions = remove_ids(actions, {
    "home.change_activity_mode",
    "home.open_managed_entity",
    "games.change_tab",
    "camps.change_tab",
    "my_games.manage_created_game",
    "competitions.manage_entity",
    "trainings.manage",
    "my_games.create",
    "competitions.create_tournament",
    "trainings.create",
    "trips.create",
    "nav.open_profile_my_games",
    "nav.open_profile_competitions",
    "nav.open_profile_trainings",
    "nav.open_profile_trips",
})

# Existing actions updated in place.
for action in actions:
    action_id = str(action.get("id", ""))
    if action_id in {"games.open_entity", "camps.open_camp"}:
        action["destination"] = "dynamic.catalog_entity_entry"
        action["permission"] = "public"
    if action_id == "nav.open_profile_players":
        action["source"] = "home.main"
    if action_id == "global.open_create_menu":
        action["source"] = "home.main"
        action["label"] = "Создать и управлять"
    if action_id in {"games.create_game", "games.create_training", "games.create_tournament", "camps.create"}:
        action["source"] = "system.create_menu"
        entity_type = {
            "games.create_game": "games",
            "games.create_training": "trainings",
            "games.create_tournament": "tournaments",
            "camps.create": "camps",
        }[action_id]
        action.setdefault("context", {})["actorId"] = "active_actor"
        action["context"]["returnTo"] = f"/manage?tab=active&type={entity_type}"

# Replace old management return paths anywhere else.
actions = replace_recursively(actions, {
    "/profile/games?mode=managing&tab=active": "/manage?tab=active&type=games",
    "/profile/trainings?mode=managing&tab=active": "/manage?tab=active&type=trainings",
    "/profile/competitions?mode=managing&tab=active": "/manage?tab=active&type=tournaments",
    "/profile/trips?mode=managing&tab=active": "/manage?tab=active&type=camps",
    "/play?tab=manage&category=games": "/manage?tab=active&type=games",
    "/play?tab=manage&category=trainings": "/manage?tab=active&type=trainings",
    "/play?tab=manage&category=tournaments": "/manage?tab=active&type=tournaments",
    "/camps?tab=manage": "/manage?tab=active&type=camps",
})

new_actions = [
    {"id": "home.open_activity", "label": "Вся моя активность", "source": "home.main", "destination": "profile.activity", "permission": "authenticated"},
    {"id": "home.open_trainers", "label": "Мои тренеры", "source": "home.main", "destination": "system.linked_trainers_sheet", "permission": "authenticated_player"},
    {"id": "home.open_followed_organizers", "label": "Организации", "source": "home.main", "destination": "play.main", "context": {"scope": "organizers", "followed": True}, "permission": "authenticated"},
    {"id": "activity.change_tab", "label": "Предстоящие / Прошедшие", "source": "profile.activity", "destination": "system.local_filter", "permission": "authenticated"},
    {"id": "activity.change_type", "label": "Все / Игры / Тренировки / Турниры / Кэмпы", "source": "profile.activity", "destination": "system.local_filter", "permission": "authenticated"},
    {"id": "activity.open_entity", "label": "Открыть", "source": "profile.activity", "destination": "dynamic.entity_details", "permission": "authenticated"},
    {"id": "management.open_center", "label": "Мои события", "source": "system.create_menu", "destination": "management.center", "permission": "authenticated"},
    {"id": "management.change_tab", "label": "Активные / Завершённые", "source": "management.center", "destination": "system.local_filter", "permission": "authenticated"},
    {"id": "management.change_type", "label": "Все / Игры / Тренировки / Турниры / Кэмпы", "source": "management.center", "destination": "system.local_filter", "permission": "authenticated"},
    {"id": "management.open_entity", "label": "Управлять", "source": "management.center", "destination": "dynamic.entity_manage", "permission": "entity_manager"},
    {"id": "management.open_create_menu", "label": "Создать событие", "source": "management.center", "destination": "system.create_menu", "permission": "authenticated"},
    {"id": "management.open_drafts", "label": "Черновики", "source": "system.create_menu", "destination": "management.center", "context": {"tab": "active", "status": "draft"}, "permission": "authenticated"},
    {"id": "management.open_requests", "label": "Заявки и участники", "source": "system.create_menu", "destination": "management.center", "context": {"tab": "active", "status": "requires_action"}, "permission": "authenticated"},
    {"id": "management.open_payments", "label": "Оплаты", "source": "system.create_menu", "destination": "management.center", "context": {"tab": "active", "status": "payment_attention"}, "permission": "authenticated"},
]
for item in new_actions:
    upsert(actions, "id", item["id"], item)
actions_doc["actions"] = actions
save_yaml(DOCS / "ACTIONS.yaml", actions_doc)

# ---------------------------------------------------------------------------
# Screen specifications
# ---------------------------------------------------------------------------
(DOCS / "screens/home/main.md").write_text("""# Профиль

- Screen ID: `home.main`
- Route: `/`
- Bottom tab: `Профиль`
- Variants: `player`, `trainer`, `organization`
- Activity contract: `docs/PROFILE_ACTIVITY.yaml`
- Connections contract: `docs/PROFILE_CONNECTIONS.yaml`
- Management contract: `docs/MANAGEMENT_CENTER.yaml`

Первая вкладка является личной профильной страницей active actor. Она не содержит переключателя `Участвую / Управляю`, кабинета управления, черновиков, заявок или операционных таблиц.

## Верхняя часть

- аватар или логотип;
- имя и тип actor-профиля;
- город, уровень или статус проверки;
- уведомления;
- переключение actor;
- `+` → `Создать и управлять`;
- редактирование публичного профиля через контекстное действие.

## Мои связи

Сразу под шапкой находится одна компактная горизонтальная строка из трёх карточек, а не три вертикальных раздела:

```text
Тренеры 2 · Игроки 12 · Организации 6
```

- `Тренеры` показывает до двух аватаров и различает активную связь и ожидающий запрос;
- `Игроки` показывает стек сохранённых игроков;
- `Организации` показывает логотипы отслеживаемых организаций;
- при ширине 320–360 карточки прокручиваются горизонтально;
- строка не называется `Подписки` или `Друзья`.

## Ближайшее

Одна общая хронологическая лента без отдельных домашних секций `Мои игры`, `Мои тренировки`, `Мои турниры`, `Мои кэмпы`.

В ней смешиваются по времени:

- игры;
- тренировки;
- турниры;
- кэмпы.

Карточка показывает дату, время, тип, название, место, статус участия и одно требуемое действие. На первом экране — не более четырёх ближайших элементов.

## Вся моя активность

Кнопка `Вся моя активность` открывает `profile.activity` на `/activity`.

Там находятся только личные участия:

```text
Предстоящие · Прошедшие
```

и фильтры:

```text
Все · Игры · Тренировки · Турниры · Кэмпы
```

## Управление

Управление событиями в Профиль не встраивается.

Доступно двумя путями:

1. `+` → `Мои события` → `management.center`;
2. нажатие на собственное событие в `Игры` или `Кэмпы` → прямой кабинет управления после проверки прав.

## Подтверждение после вступления

После создания или обновления записи участия иконка `Профиль` один раз даёт доступный сигнал на 900 мс. Check означает подтверждённое участие, dot — заявку или ожидание оплаты. Геометрия нижнего меню не меняется, Reduce Motion учитывается.

## Нижняя навигация

```text
Профиль · Игры · Чаты · Кэмпы · Настройки
```

На этом экране активен `Профиль`.

## Состояния

- loading по блокам;
- связи частично загружены;
- нет связей;
- нет ближайших участий;
- есть заявка или ожидание оплаты;
- offline с последним сохранённым состоянием;
- permission changed.
""", encoding="utf-8")

(DOCS / "screens/profile/activity.md").write_text("""# Вся моя активность

- Screen ID: `profile.activity`
- Route: `/activity`
- Parent: `home.main`
- Contract: `docs/PROFILE_ACTIVITY.yaml`

## Назначение

Единый личный список участий пользователя. Экран не содержит созданные события, черновики или управленческие задачи.

## Верхние вкладки

```text
Предстоящие · Прошедшие
```

## Фильтры типов

```text
Все · Игры · Тренировки · Турниры · Кэмпы
```

Чипы находятся в одной горизонтально прокручиваемой строке без переноса.

## Предстоящие

Показываются приглашения, заявки, ожидание оплаты, лист ожидания и подтверждённые участия. Сортировка — от ближайшей даты к более поздней.

Карточка содержит:

- дату и время;
- тип и название;
- место и организатора;
- статус участия;
- оплату, когда применимо;
- одно главное действие.

## Прошедшие

Показываются завершённые и отменённые участия с результатом, посещением или причиной отмены, когда данные доступны.

## Переходы

- карточка → публичный канонический экран сущности;
- календарь → `profile.calendar`;
- пустое `Предстоящие` → `Игры`;
- назад → Профиль.

Управлять событием с этого экрана нельзя. Автор события открывает управление через каталог, `+` или `management.center`.

## Состояния

- loading;
- нет предстоящих участий;
- нет истории;
- фильтр ничего не нашёл;
- событие стало непубличным, но участие сохранено;
- permission changed;
- offline.
""", encoding="utf-8")

(DOCS / "screens/shared/management-center.md").write_text("""# Центр управления

- Screen ID: `management.center`
- Route: `/manage`
- Parent: `home.main`
- Contract: `docs/MANAGEMENT_CENTER.yaml`
- Variants: `player`, `trainer`, `organization`

## Назначение

Единый рабочий список всех сущностей, которыми active actor может управлять. Экран не является нижней вкладкой и не встраивается в Профиль.

## Входы

- `+` → `Мои события`;
- `+` → `Черновики`;
- `+` → `Заявки и участники`;
- `+` → `Оплаты`;
- возврат из кабинета конкретного события;
- уведомление, требующее управленческого действия.

## Вкладки

```text
Активные · Завершённые
```

## Фильтры

```text
Все · Игры · Тренировки · Турниры · Кэмпы
```

Внутри `Активные` фильтруются черновики, опубликованные события, заявки, неоплаченные регистрации, незаполненные результаты и другие задачи. Они не создают дополнительные верхние вкладки.

## Карточка

- actor-профиль владельца;
- тип, название, дата и место;
- статус публикации;
- заполненность;
- количество заявок;
- неоплаченные места;
- ближайшее управленческое действие;
- основная кнопка `Управлять`.

## Создание

Кнопка `Создать событие` открывает общий `system.create_menu` с вариантами:

```text
Игра · Тренировка · Турнир · Кэмп
```

## Переход к конкретной сущности

Карточка открывает канонический manage route:

- `/games/:gameId/manage`;
- `/trainings/:trainingId/manage`;
- `/tournaments/:tournamentId/manage`;
- `/tours/:tourId/manage`.

Возврат восстанавливает вкладку, тип, фильтры и позицию списка.

## Состояния

- нет управляемых событий;
- только черновики;
- требуется действие;
- права были отозваны;
- active actor переключён;
- offline read-only.
""", encoding="utf-8")

(DOCS / "screens/play/main.md").write_text("""# Игры

- Screen ID: `play.main`
- Route: `/play`
- Bottom tab: `Игры`
- Catalog contract: `docs/GAMES_CATALOG.yaml`
- Management contract: `docs/MANAGEMENT_CENTER.yaml`

## Назначение

Публичный каталог для подбора, поиска, фильтрации и начала вступления. Личных вкладок и общего кабинета управления здесь нет.

## Категории

```text
Игры · Тренировки · Турниры
```

Для турниров:

```text
Все · Классика · Король пляжа · Сезонные
```

Все чипы однострочные и прокручиваются горизонтально.

## Выдача

- публичные игры любых игроков;
- игры отслеживаемых организаций;
- публичные игры сохранённых игроков;
- публичные тренировки частных тренеров и организаций;
- классические, Король пляжа и сезонные турниры;
- сортировка от ближайшей даты к более поздней.

## Нажатие на карточку

Используется `dynamic.catalog_entity_entry`:

1. сервер повторно проверяет права active actor;
2. при наличии права управления открывается соответствующий manage route;
3. без права управления открывается публичный detail route;
4. при отозванном праве показывается публичная страница и уведомление об изменении доступа.

Клиентский `canManageHint` не является источником авторизации.

## Вступление

Для чужого события публичная страница показывает единое действие `Вступить`, которое запускает `system.resolve_join_flow`. Бесплатная запись, оплата, заявка, лист ожидания и приглашение будут утверждены отдельно.

## Пустое состояние

```text
Пока нет подходящих игр
[Добавить организацию] [Добавить игроков]
```

## Возврат

После публичного просмотра или управления восстанавливаются категория, чипы, фильтры и позиция каталога.

## Состояния

- loading;
- пустой каталог;
- нет результатов фильтра;
- геолокация выключена;
- права управления изменились;
- offline;
- событие стало непубличным.
""", encoding="utf-8")

(DOCS / "screens/camps/main.md").write_text("""# Кэмпы

- Screen ID: `camps.main`
- Route: `/camps`
- Bottom tab: `Кэмпы`
- Management contract: `docs/MANAGEMENT_CENTER.yaml`

## Назначение

Публичная витрина совместных поездок игроков, тренировочных лагерей тренеров и коммерческих кэмпов организаций. Личные участия и управление здесь не оформляются отдельными вкладками.

## Каталог

- поиск по направлению, дате, уровню и цене;
- сортировка от ближайшей даты к более поздней;
- карточка показывает даты, направление, автора, тип, заполненность, цену или ориентировочный бюджет;
- player, trainer и organization actor могут создавать кэмпы через `+`.

## Нажатие на карточку

Используется тот же `dynamic.catalog_entity_entry`:

- авторизованный менеджер → `/tours/:tourId/manage`;
- другой пользователь → `/tours/:tourId`;
- право всегда повторно проверяется сервером.

## Вступление

На публичной странице используется единое действие `Вступить`; точный сценарий бронирования, заявки или оплаты проектируется отдельно.

## Личные кэмпы

Личные записи находятся в `Вся моя активность` с фильтром `Кэмпы` и вкладками `Предстоящие · Прошедшие`. Совместимый экран `/profile/trips` сохраняет подписи `Записан · Прошедшие`.

## Состояния

- loading;
- пустая выдача;
- нет результатов фильтра;
- кэмп заполнен;
- права управления изменились;
- offline.
""", encoding="utf-8")

legacy_specs = {
    "my-games.md": ("Мои игры", "Предстоящие · Прошедшие", "Игры"),
    "my-trainings.md": ("Мои тренировки", "Записан · Прошедшие", "Тренировки"),
    "my-competitions.md": ("Мои турниры", "Заявлен · Прошедшие", "Турниры"),
    "my-trips.md": ("Мои кэмпы", "Записан · Прошедшие", "Кэмпы"),
}
for filename, (title, tabs, filter_name) in legacy_specs.items():
    path = DOCS / "screens/profile" / filename
    screen_id = {
        "my-games.md": "profile.my_games",
        "my-trainings.md": "profile.trainings",
        "my-competitions.md": "profile.competitions",
        "my-trips.md": "profile.trips",
    }[filename]
    route = {
        "my-games.md": "/profile/games",
        "my-trainings.md": "/profile/trainings",
        "my-competitions.md": "/profile/competitions",
        "my-trips.md": "/profile/trips",
    }[filename]
    path.write_text(f"""# {title}

- Screen ID: `{screen_id}`
- Route: `{route}`
- Parent: `home.main`
- Compatibility role: filtered personal activity view

Этот экран сохраняется для существующих deep links и открывает личные участия с фиксированным фильтром `{filter_name}`. Управляемые и созданные события здесь не показываются.

## Вкладки

```text
{tabs}
```

Карточки используют те же данные и действия, что `profile.activity`. Для управления пользователь открывает собственное событие из каталога либо `+` → `Мои события`.

## Возврат

Назад → `Вся моя активность`, fallback `/activity`.
""", encoding="utf-8")

# Detail/manage specs get a common role-based entry contract.
for filename in ("game-details.md", "training-details.md", "tournament-details.md", "tour-details.md"):
    append_section(
        DOCS / "screens/shared" / filename,
        "## Открытие из каталога по правам",
        """## Открытие из каталога по правам

При нажатии на карточку в `Игры` или `Кэмпы` этот публичный экран открывается только пользователю без действующего права управления. Для manager actor resolver сразу открывает manage route. При прямом deep link владелец всё равно видит действие `Управлять`, но публичный и управленческий режимы не смешиваются.
""",
    )
for filename, entity_type in (
    ("game-manage.md", "games"),
    ("training-manage.md", "trainings"),
    ("tournament-manage.md", "tournaments"),
    ("tour-manage.md", "camps"),
):
    append_section(
        DOCS / "screens/shared" / filename,
        "## Вход из каталога и возврат",
        f"""## Вход из каталога и возврат

Экран может открываться напрямую из каталога после серверной проверки прав либо из `management.center`. Назад без истории → `/manage?tab=active&type={entity_type}`. Возврат восстанавливает фильтры и позицию списка. При потере права управление закрывается и открывается публичный detail screen с уведомлением.
""",
    )
append_section(
    DOCS / "screens/profile/main.md",
    "## Управление событиями",
    """## Управление событиями

Настройки не содержат списки созданных событий. Управление открывается через `+` → `Мои события` или прямым нажатием на собственное событие в публичном каталоге.
""",
)

# ---------------------------------------------------------------------------
# Validator
# ---------------------------------------------------------------------------
(ROOT / "scripts/validate_profile_activity.py").write_text(r'''#!/usr/bin/env python3
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
''', encoding="utf-8")

# ---------------------------------------------------------------------------
# Narrative docs and decisions
# ---------------------------------------------------------------------------
readme = """# VolleyPlay / Beach Volleyball

Архитектура мобильного приложения для поиска, участия и организации пляжного волейбола.

## Источники истины

1. `docs/ARCHITECTURE.md` — общая модель продукта.
2. `docs/SCREENS.yaml` — реестр экранов.
3. `docs/ROUTES.yaml` — маршруты и возвраты.
4. `docs/ACTIONS.yaml` — действия.
5. `docs/NAVIGATION_RESOLVERS.yaml` — динамическая навигация.
6. `docs/PROFILE_ACTIVITY.yaml` — личные участия.
7. `docs/PROFILE_CONNECTIONS.yaml` — тренеры, игроки и организации в Профиле.
8. `docs/MANAGEMENT_CENTER.yaml` — создание и управление событиями.
9. `docs/GAMES_CATALOG.yaml` — каталог игр, тренировок и турниров.
10. `docs/DESIGN_TOKENS.yaml` — UI-контракт.

## Нижняя навигация

```text
Профиль · Игры · Чаты · Кэмпы · Настройки
```

- `Профиль` — личная шапка, одна компактная строка связей, ближайшие участия и `Вся моя активность`;
- `Игры` — публичный подбор игр, тренировок и турниров;
- `Чаты` — личные и событийные разговоры;
- `Кэмпы` — публичная витрина поездок и лагерей;
- `Настройки` — аккаунт, роли, платежи, приватность и служебные параметры.

## Профиль без управления

В Профиле нет переключателя `Участвую / Управляю`. Связи показываются одной горизонтальной строкой `Тренеры · Игроки · Организации`. Ниже находится единая хронологическая лента `Ближайшее` и переход `Вся моя активность`.

Полный список личных участий:

```text
Предстоящие · Прошедшие
Все · Игры · Тренировки · Турниры · Кэмпы
```

## Создание и управление

Кнопка `+` открывает меню:

```text
Создать: Игра · Тренировка · Турнир · Кэмп
Управление: Мои события · Черновики · Заявки и участники · Оплаты
```

`Мои события` открывает `/manage` с вкладками `Активные · Завершённые` и фильтрами типов.

При нажатии на карточку в `Игры` или `Кэмпы` используется `dynamic.catalog_entity_entry`:

- подтверждённое право управления → manage route;
- иначе → публичный detail route;
- сервер всегда повторно проверяет право, клиентский hint не является авторизацией.

## Игры и турниры

```text
Игры · Тренировки · Турниры
```

Для турниров:

```text
Все · Классика · Король пляжа · Сезонные
```

Самостоятельной сущности сезона нет. Сезонный формат является режимом турнира с игровыми днями и накопительной таблицей.

## Кэмпы

Кэмп может создать player, trainer или organization actor. Для частной поездки проживание, транспорт и коммерческая цена не обязательны.

## Игрок и тренер

Игрок отправляет запрос. Тренер получает `Новый игрок` и видит запрос в `Мои игроки → Новые`. Только `Добавить` активирует связь и подпись `Тренируется у`.

## UI

React Native / Expo, dark-first, Lucide icons, горизонтальные чипы без переноса, минимальная зона нажатия 48×48, Reanimated и обязательный Reduce Motion.

## Статус

Это архитектурный контракт MVP. Рабочий клиент, сервер, платежи и алгоритмы должны быть реализованы и протестированы отдельно.
"""
(ROOT / "README.md").write_text(readme, encoding="utf-8")

# Mark the old profile-management decision as superseded and append the accepted decision.
decisions_path = DOCS / "DECISIONS.md"
decisions = decisions_path.read_text(encoding="utf-8")
decisions = decisions.replace(
    "## D-026 — Личная активность переносится в Профиль",
    "## D-026 — Личная активность переносится в Профиль (заменено D-032)",
)
if "## D-032 — Управление вынесено из Профиля" not in decisions:
    decisions += """

## D-032 — Управление вынесено из Профиля

Статус: принято; заменяет управленческую часть предыдущего решения о `Участвую · Управляю`.

Профиль показывает личность active actor, компактную строку связей и ближайшие личные участия. Переключатель `Участвую / Управляю`, черновики и операционные задачи в Профиле запрещены.

Создание и общий список управления открываются через `+`. Экран `management.center` использует `Активные · Завершённые` и фильтры типов.

При нажатии на карточку события в `Игры` или `Кэмпы` resolver повторно проверяет права: manager actor сразу попадает на manage route, остальные пользователи — на публичный detail route. Клиентский признак права не заменяет серверную авторизацию.
"""
decisions_path.write_text(decisions, encoding="utf-8")

for filename, marker, section in [
    ("USER_FLOWS.md", "## Управление из каталога", """## Управление из каталога

```text
Игры или Кэмпы
→ карточка события
→ server permission check
├─ есть право → manage route
└─ нет права → public detail route
```

Общий список: `+ → Мои события → Центр управления`. Профиль остаётся личным экраном без управленческого режима.
"""),
    ("TEST_SCENARIOS.md", "## Capability-aware opening", """## Capability-aware opening

- владелец игры нажимает карточку в каталоге и попадает в `/games/:gameId/manage`;
- обычный игрок нажимает ту же карточку и попадает в `/games/:gameId`;
- отозванное право не позволяет загрузить manage data и переводит на public detail с уведомлением;
- нажатие `Назад` из manage восстанавливает каталог либо `/manage` согласно входу;
- Профиль не содержит `Участвую / Управляю` и не показывает черновики;
- `+ → Мои события` открывает `management.center`;
- `Вся моя активность` содержит только личные участия.
"""),
    ("APP_MAP.md", "## Текущая модель Профиля и управления", """## Текущая модель Профиля и управления

```text
Профиль /
├── Мои связи: Тренеры · Игроки · Организации
├── Ближайшее
└── Вся моя активность /activity
    ├── Предстоящие
    └── Прошедшие

+ system://create-menu
├── Создать игру / тренировку / турнир / кэмп
└── Центр управления /manage
    ├── Активные
    └── Завершённые

Игры /play или Кэмпы /camps
└── карточка
    ├── manager → entity manage
    └── other → entity details
```
"""),
    ("ARCHITECTURE.md", "## Capability-aware event entry", """## Capability-aware event entry

Публичные каталоги не содержат отдельный управленческий режим. `dynamic.catalog_entity_entry` выбирает public detail или manage route после серверной проверки права active actor. Общий рабочий список находится в `management.center`, а Профиль содержит только личные связи и участия.
"""),
]:
    path = DOCS / filename
    append_section(path, marker, section)

print("Direct event management migration applied.")
