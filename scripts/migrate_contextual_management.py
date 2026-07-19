#!/usr/bin/env python3
from __future__ import annotations

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


def save_yaml(path: Path, value: dict[str, Any]) -> None:
    path.write_text(
        yaml.safe_dump(value, allow_unicode=True, sort_keys=False, width=110),
        encoding="utf-8",
    )


def find(items: list[dict[str, Any]], key: str, value: str) -> dict[str, Any] | None:
    return next((item for item in items if str(item.get(key, "")) == value), None)


def remove_ids(items: list[dict[str, Any]], ids: set[str]) -> list[dict[str, Any]]:
    return [item for item in items if str(item.get("id", "")) not in ids]


# PROFILE_ACTIVITY: Profile remains personal; creation and management live in section tabs.
profile_activity = load_yaml(DOCS / "PROFILE_ACTIVITY.yaml")
profile_activity["version"] = 3
profile_activity["source_of_truth_for"] = [
    "personal participation preview on home.main",
    "unified personal activity list",
    "contextual creation and management in Games and Camps",
    "post-join Profile tab feedback",
]
for name in ("games", "camps"):
    cfg = profile_activity.setdefault("catalog_boundaries", {}).setdefault(name, {})
    cfg["mode"] = "discovery_and_contextual_management"
    cfg["allows"] = [
        "browse",
        "search",
        "filter",
        "open_by_capability",
        "start_join_flow",
        "switch_to_management_mode",
        "create_in_section",
    ]
    cfg["forbids"] = [
        "participating_tab",
        "personal_archive",
        "profile_management_entry",
    ]
profile_activity["management"] = {
    "source_of_truth": "docs/MANAGEMENT_CENTER.yaml",
    "profile_embedding_forbidden": True,
    "profile_entry_forbidden": True,
    "standalone_center_removed": True,
    "games": {
        "screen": "play.main",
        "route": "/play",
        "mode_query": "manage",
        "entity_types": ["game", "training", "tournament"],
    },
    "camps": {
        "screen": "camps.main",
        "route": "/camps",
        "mode_query": "manage",
        "entity_types": ["camp"],
    },
}
save_yaml(DOCS / "PROFILE_ACTIVITY.yaml", profile_activity)

# MANAGEMENT_CENTER becomes the source for contextual section management rather than a standalone screen.
management = {
    "version": 2,
    "scope": "contextual_section_management",
    "source_of_truth_for": [
        "management mode in Games and Camps",
        "contextual creation entry points",
        "capability-aware event opening",
        "return paths from entity management",
    ],
    "principles": [
        "Profile has no creation or event-management controls",
        "Games owns creation and management of games, trainings and tournaments",
        "Camps owns creation and management of camps",
        "management mode behaves as a reversible list filter, not a separate bottom tab",
        "server authorization is authoritative; client capability hints are never sufficient",
        "public detail and entity management remain separate routes",
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
    "games_section": {
        "screen": "play.main",
        "route": "/play",
        "mode_control": {
            "label": "Режим управления",
            "active_label": "Вернуться к подбору",
            "query": "mode=manage",
            "action_id": "games.change_mode",
            "presentation": "header_button",
        },
        "managed_types": ["games", "trainings", "tournaments"],
        "management_tabs": ["active", "completed"],
        "tab_labels": {"active": "Активные", "completed": "Завершённые"},
        "active_status_filters": ["all", "draft", "requires_action", "published", "in_progress"],
        "create_action_ids": ["games.create_game", "games.create_training", "games.create_tournament"],
        "create_presentation": "contextual_create_sheet",
    },
    "camps_section": {
        "screen": "camps.main",
        "route": "/camps",
        "mode_control": {
            "label": "Режим управления",
            "active_label": "Вернуться к подбору",
            "query": "mode=manage",
            "action_id": "camps.change_mode",
            "presentation": "header_button",
        },
        "managed_types": ["camps"],
        "management_tabs": ["active", "completed"],
        "tab_labels": {"active": "Активные", "completed": "Завершённые"},
        "active_status_filters": ["all", "draft", "requires_action", "published", "in_progress"],
        "create_action_ids": ["camps.create"],
        "create_presentation": "primary_contextual_button",
    },
    "managed_card_fields": [
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
    "multi_actor": {
        "default_scope": "active_actor",
        "actor_filter_when_multiple": True,
        "all_actors_option": True,
    },
    "return_policy": {
        "game": "/play?mode=manage&category=games&manageTab=active",
        "training": "/play?mode=manage&category=trainings&manageTab=active",
        "tournament": "/play?mode=manage&category=tournaments&manageTab=active",
        "camp": "/camps?mode=manage&manageTab=active",
        "restore": ["mode", "category", "manageTab", "filters", "actor", "scroll_position"],
    },
}
save_yaml(DOCS / "MANAGEMENT_CENTER.yaml", management)

# Games catalog supports a contextual management mode.
games = load_yaml(DOCS / "GAMES_CATALOG.yaml")
games["version"] = 2
games["source_of_truth_for"] = [
    "Игры bottom tab",
    "catalog categories and ordering",
    "followed organizers and saved players",
    "empty-state recovery",
    "contextual management mode",
]
games["bottom_tab"]["mode"] = "discovery_and_contextual_management"
games["bottom_tab"]["capabilities"] = [
    "browse", "search", "filter", "open_by_capability", "start_join_flow",
    "switch_to_management_mode", "create_in_section",
]
games["personal_activity"] = {
    "home_preview": "home.main",
    "full_list": "profile.activity",
    "participation_tabs_forbidden_in_catalog": True,
}
games["management_mode"] = {
    "contract": "docs/MANAGEMENT_CENTER.yaml",
    "query": "mode=manage",
    "button_label": "Режим управления",
    "shows_only": "entities_manageable_by_active_actor",
    "categories": ["games", "trainings", "tournaments"],
    "tabs": ["active", "completed"],
    "create": ["game", "training", "tournament"],
}
save_yaml(DOCS / "GAMES_CATALOG.yaml", games)

# Screen registry: remove standalone management center and update purposes.
screens_doc = load_yaml(DOCS / "SCREENS.yaml")
screens = screens_doc.get("screens", []) or []
screens = [item for item in screens if item.get("id") != "management.center"]
home = find(screens, "id", "home.main")
if home:
    home["purpose"] = "Личный профиль active actor: связи, ближайшие участия и переход ко всей личной активности без создания и управления событиями."
play = find(screens, "id", "play.main")
if play:
    play["purpose"] = "Подбор игр, тренировок и турниров; контекстное создание и режим управления своими событиями."
camps = find(screens, "id", "camps.main")
if camps:
    camps["purpose"] = "Подбор кэмпов; контекстное создание и режим управления своими кэмпами."
screens_doc["screens"] = screens
screens_doc["global_overlays"] = [x for x in screens_doc.get("global_overlays", []) or [] if x != "system.create_menu"]
save_yaml(DOCS / "SCREENS.yaml", screens_doc)

# Routes: remove /manage, add contextual mode queries, and return manage/create routes to their owning sections.
routes_doc = load_yaml(DOCS / "ROUTES.yaml")
routes = routes_doc.get("routes", []) or []
routes = [item for item in routes if item.get("path") != "/manage"]
for path in ("/play", "/camps"):
    route = find(routes, "path", path)
    if route:
        accepted = list(route.get("accepts_query", []) or [])
        for key in ("mode", "manageTab", "manageStatus", "actorId"):
            if key not in accepted:
                accepted.append(key)
        route["accepts_query"] = accepted
fallbacks = {
    "/games/create": "/play?mode=manage&category=games&manageTab=active",
    "/games/:gameId/manage": "/play?mode=manage&category=games&manageTab=active",
    "/trainings/create": "/play?mode=manage&category=trainings&manageTab=active",
    "/trainings/:trainingId/manage": "/play?mode=manage&category=trainings&manageTab=active",
    "/tournaments/create": "/play?mode=manage&category=tournaments&manageTab=active",
    "/tournaments/:tournamentId/manage": "/play?mode=manage&category=tournaments&manageTab=active",
    "/tours/create": "/camps?mode=manage&manageTab=active",
    "/tours/:tourId/manage": "/camps?mode=manage&manageTab=active",
}
for path, fallback in fallbacks.items():
    route = find(routes, "path", path)
    if route:
        route["back_fallback"] = fallback
routes_doc["routes"] = routes
save_yaml(DOCS / "ROUTES.yaml", routes_doc)

# Actions: remove Profile/global management entry and standalone center actions; add section-local mode and creation actions.
actions_doc = load_yaml(DOCS / "ACTIONS.yaml")
actions = actions_doc.get("actions", []) or []
actions = remove_ids(actions, {
    "global.open_create_menu",
    "management.open_center",
    "management.change_tab",
    "management.change_type",
    "management.open_entity",
    "management.open_create_menu",
    "management.open_drafts",
    "management.open_requests",
    "management.open_payments",
    "games.create_game",
    "games.create_training",
    "games.create_tournament",
    "camps.create",
})
actions.extend([
    {
        "id": "games.change_mode",
        "label": "Режим управления / Вернуться к подбору",
        "source": "play.main",
        "destination": "system.local_state",
        "permission": "authenticated",
    },
    {
        "id": "games.change_management_tab",
        "label": "Активные / Завершённые",
        "source": "play.main",
        "destination": "system.local_filter",
        "permission": "authenticated",
    },
    {
        "id": "games.open_management_filters",
        "label": "Фильтры управления",
        "source": "play.main",
        "destination": "system.search_filters",
        "permission": "authenticated",
    },
    {
        "id": "games.open_managed_entity",
        "label": "Управлять",
        "source": "play.main",
        "destination": "dynamic.entity_manage",
        "permission": "entity_manager",
    },
    {
        "id": "games.create_game",
        "label": "Создать игру",
        "source": "play.main",
        "destination": "game.create",
        "permission": "authenticated",
        "context": {"actorId": "active_actor", "returnTo": "/play?mode=manage&category=games&manageTab=active"},
    },
    {
        "id": "games.create_training",
        "label": "Создать тренировку",
        "source": "play.main",
        "destination": "training.create",
        "permission": "trainer_or_organization",
        "context": {"actorId": "active_actor", "returnTo": "/play?mode=manage&category=trainings&manageTab=active"},
    },
    {
        "id": "games.create_tournament",
        "label": "Создать турнир",
        "source": "play.main",
        "destination": "tournament.create",
        "permission": "authenticated",
        "context": {"actorId": "active_actor", "returnTo": "/play?mode=manage&category=tournaments&manageTab=active"},
    },
    {
        "id": "camps.change_mode",
        "label": "Режим управления / Вернуться к подбору",
        "source": "camps.main",
        "destination": "system.local_state",
        "permission": "authenticated",
    },
    {
        "id": "camps.change_management_tab",
        "label": "Активные / Завершённые",
        "source": "camps.main",
        "destination": "system.local_filter",
        "permission": "authenticated",
    },
    {
        "id": "camps.open_management_filters",
        "label": "Фильтры управления",
        "source": "camps.main",
        "destination": "system.search_filters",
        "permission": "authenticated",
    },
    {
        "id": "camps.open_managed_camp",
        "label": "Управлять кэмпом",
        "source": "camps.main",
        "destination": "tour.manage",
        "permission": "entity_manager",
    },
    {
        "id": "camps.create",
        "label": "Создать кэмп",
        "source": "camps.main",
        "destination": "tour.create",
        "permission": "authenticated",
        "context": {"actorId": "active_actor", "returnTo": "/camps?mode=manage&manageTab=active"},
    },
])
actions_doc["actions"] = actions
save_yaml(DOCS / "ACTIONS.yaml", actions_doc)

# Resolvers: create menu is no longer a global overlay. Capability-aware catalog opening remains.
resolvers = load_yaml(DOCS / "NAVIGATION_RESOLVERS.yaml")
# This document may not own overlays; remove stale dynamic source only when it is no longer used.
resolvers["dynamic_sources"] = [
    value for value in resolvers.get("dynamic_sources", []) or []
    if value != "dynamic.global_or_section_header"
]
save_yaml(DOCS / "NAVIGATION_RESOLVERS.yaml", resolvers)

# Markdown screen specs.
(DOCS / "screens/home/main.md").write_text("""# Профиль

- Screen ID: `home.main`
- Route: `/`
- Bottom tab: `Профиль`
- Variants: `player`, `trainer`, `organization`
- Activity contract: `docs/PROFILE_ACTIVITY.yaml`
- Connections contract: `docs/PROFILE_CONNECTIONS.yaml`

Первая вкладка является личной профильной страницей active actor. Создание игр, тренировок, турниров и кэмпов, а также управление ими, на этом экране отсутствуют.

## Верхняя часть

- аватар или логотип;
- имя и тип actor-профиля;
- город, уровень или статус проверки;
- уведомления;
- переключение actor;
- редактирование публичного профиля через контекстное действие;
- кнопка `+` отсутствует.

## Мои связи

Сразу под шапкой находится одна компактная горизонтальная строка из трёх карточек:

```text
Тренеры 2 · Игроки 12 · Организации 6
```

- `Тренеры` различает активную связь и ожидающий запрос;
- `Игроки` показывает стек сохранённых игроков;
- `Организации` показывает логотипы отслеживаемых организаций;
- при ширине 320–360 карточки прокручиваются горизонтально;
- строка не называется `Подписки` или `Друзья`.

## Ближайшее

Одна общая хронологическая лента личных участий:

- игры;
- тренировки;
- турниры;
- кэмпы.

Карточка показывает дату, время, тип, название, место, статус участия и одно требуемое действие. На первом экране — не более четырёх ближайших элементов.

## Вся моя активность

Кнопка `Вся моя активность` открывает `/activity`:

```text
Предстоящие · Прошедшие
```

Фильтры:

```text
Все · Игры · Тренировки · Турниры · Кэмпы
```

## Где создавать и управлять

- игры, тренировки и турниры: `Игры` → `Режим управления`;
- кэмпы: `Кэмпы` → `Режим управления`;
- нажатие на собственное событие в обычной выдаче также открывает его кабинет после серверной проверки прав.

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

(DOCS / "screens/play/main.md").write_text("""# Игры

- Screen ID: `play.main`
- Route: `/play`
- Bottom tab: `Игры`
- Catalog contract: `docs/GAMES_CATALOG.yaml`
- Management contract: `docs/MANAGEMENT_CENTER.yaml`

## Два режима одного экрана

По умолчанию открыт подбор публичных событий. В шапке находится кнопка:

```text
Режим управления
```

Она работает как обратимый фильтр текущего раздела. После нажатия экран не меняет нижнюю вкладку и показывает только события, которыми управляет active actor. Активная кнопка получает label `Вернуться к подбору`.

## Режим подбора

Категории:

```text
Игры · Тренировки · Турниры
```

Для турниров:

```text
Все · Классика · Король пляжа · Сезонные
```

Показываются публичные события, поиск, фильтры и единое действие `Вступить` на публичной странице.

## Режим управления

Сохраняются категории `Игры · Тренировки · Турниры`, но выдача содержит только доступные active actor события.

Временные вкладки:

```text
Активные · Завершённые
```

В `Активные` находятся черновики, опубликованные события, события с заявками, оплатами или другими требуемыми действиями. Дополнительные состояния являются фильтрами, а не новыми верхними вкладками.

Карточка показывает:

- автора/actor;
- статус публикации;
- дату;
- заполненность;
- новые заявки;
- неоплаченные места;
- ближайшее действие.

Нажатие открывает соответствующий manage route.

## Создание

В режиме управления показывается контекстная кнопка:

```text
+ Создать
```

Она открывает небольшой sheet:

```text
Создать игру
Создать тренировку
Создать турнир
```

Недоступный active actor вариант скрывается или получает понятное объяснение. Создание возвращает в ту же категорию режима управления.

## Нажатие на карточку в подборе

Используется `dynamic.catalog_entity_entry`:

1. сервер повторно проверяет права active actor;
2. при наличии права управления открывается manage route;
3. без права открывается публичный detail route;
4. при отозванном праве показывается публичная страница и уведомление.

## Пустые состояния

Подбор:

```text
Пока нет подходящих игр
[Добавить организацию] [Добавить игроков]
```

Управление:

```text
Вы пока не создавали событий этого типа
[Создать]
```

## Возврат

После detail/manage/create восстанавливаются режим, категория, вкладка управления, actor-фильтр, фильтры и позиция списка.
""", encoding="utf-8")

(DOCS / "screens/camps/main.md").write_text("""# Кэмпы

- Screen ID: `camps.main`
- Route: `/camps`
- Bottom tab: `Кэмпы`
- Management contract: `docs/MANAGEMENT_CENTER.yaml`

## Два режима одного экрана

По умолчанию открыта публичная витрина кэмпов. Кнопка `Режим управления` переключает текущую выдачу на кэмпы, которыми управляет active actor. При включённом режиме label меняется на `Вернуться к подбору`.

## Режим подбора

- поиск по направлению, дате, уровню и цене;
- сортировка от ближайшей даты к более поздней;
- карточка показывает даты, направление, автора, тип, заполненность, цену или ориентировочный бюджет;
- публичная страница использует единое действие `Вступить`.

## Режим управления

Показываются только собственные или доступные по роли кэмпы.

```text
Активные · Завершённые
```

В `Активные` входят черновики, опубликованные кэмпы и записи, требующие обработки заявок, оплат или документов. Нажатие открывает `/tours/:tourId/manage`.

Основная кнопка:

```text
+ Создать кэмп
```

Кэмп может создать player, trainer или organization actor. После создания пользователь возвращается в режим управления кэмпами.

## Нажатие на карточку в подборе

Используется `dynamic.catalog_entity_entry`:

- авторизованный менеджер → `/tours/:tourId/manage`;
- другой пользователь → `/tours/:tourId`;
- право повторно проверяется сервером.

## Личные участия

Личные записи находятся в `Вся моя активность` с фильтром `Кэмпы` и вкладками `Предстоящие · Прошедшие`.

## Пустое состояние управления

```text
Вы пока не создавали кэмпы
[Создать кэмп]
```

## Возврат

После detail/manage/create восстанавливаются режим, вкладка управления, actor-фильтр, фильтры и позиция списка.
""", encoding="utf-8")

# Remove obsolete standalone management screen spec.
management_spec = DOCS / "screens/shared/management-center.md"
if management_spec.exists():
    management_spec.unlink()

# Append a decision once.
decisions_path = DOCS / "DECISIONS.md"
decisions_text = decisions_path.read_text(encoding="utf-8")
if "D-033 — Контекстное управление в Играх и Кэмпах" not in decisions_text:
    decisions_text += """

## D-033 — Контекстное управление в Играх и Кэмпах

Статус: принято.

Профиль не содержит кнопку создания или вход в управление событиями. В `Игры` кнопка `Режим управления` фильтрует выдачу до игр, тренировок и турниров, которыми управляет active actor; там же находится контекстное создание этих типов. В `Кэмпы` применяется тот же режим только для кэмпов и находится `Создать кэмп`. Самостоятельный экран `/manage` удаляется. Manage/create routes возвращают в соответствующий раздел с восстановлением режима, категории и позиции списка.
"""
    decisions_path.write_text(decisions_text, encoding="utf-8")

# README gets a concise current-state section.
readme = ROOT / "README.md"
text = readme.read_text(encoding="utf-8")
marker = "## Контекстное создание и управление"
section = """## Контекстное создание и управление

- `Профиль` не содержит `+` и управленческих элементов.
- `Игры` имеет кнопку `Режим управления`; она показывает только управляемые игры, тренировки и турниры и открывает их создание.
- `Кэмпы` имеет собственный `Режим управления` и кнопку `Создать кэмп`.
- Отдельного `/manage` нет; создание и управление остаются в контексте соответствующей нижней вкладки.

"""
if marker in text:
    before = text.split(marker, 1)[0]
    # Keep later content after the next heading if possible.
    tail = text.split(marker, 1)[1]
    next_heading = tail.find("\n## ", 1)
    suffix = tail[next_heading + 1:] if next_heading != -1 else ""
    text = before + section + suffix
else:
    text = section + text
readme.write_text(text, encoding="utf-8")

# Replace validator with the new contextual-management contract.
(ROOT / "scripts/validate_profile_activity.py").write_text("""#!/usr/bin/env python3
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
    if management.get("games_section", {}).get("mode_control", {}).get("label") != "Режим управления":
        errors.append("Games management mode label differs")
    if management.get("camps_section", {}).get("mode_control", {}).get("label") != "Режим управления":
        errors.append("Camps management mode label differs")

    if find(routes, "path", "/manage"):
        errors.append("Standalone /manage route must be removed")
    if find(screens, "id", "management.center"):
        errors.append("Standalone management.center screen must be removed")

    for path in ("/play", "/camps"):
        route = find(routes, "path", path)
        accepted = set((route or {}).get("accepts_query", []) or [])
        if not {"mode", "manageTab", "actorId"}.issubset(accepted):
            errors.append(f"{path} must accept contextual management queries")

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

    action_ids = {str(item.get("id", "")) for item in actions}
    required = {
        "games.change_mode", "games.create_game", "games.create_training", "games.create_tournament",
        "camps.change_mode", "camps.create", "games.open_entity", "camps.open_camp",
    }
    for action_id in sorted(required - action_ids):
        errors.append(f"Missing action {action_id}")
    for obsolete in {"global.open_create_menu", "management.open_center", "management.open_entity"}:
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
""", encoding="utf-8")

print("Contextual management migration applied.")
