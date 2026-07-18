#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
from typing import Any
import re
import yaml

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
BRANCH_WORKFLOW = ROOT / ".github/workflows/migrate-games-camps-catalog.yml"
SELF = ROOT / "scripts/migrate_games_camps_catalog.py"


def load_yaml(path: Path) -> dict[str, Any]:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"{path} must contain a mapping")
    return value


def dump_yaml(path: Path, value: dict[str, Any]) -> None:
    path.write_text(
        yaml.safe_dump(value, allow_unicode=True, sort_keys=False, width=120),
        encoding="utf-8",
    )


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


def replace_in(path: Path, replacements: list[tuple[str, str]]) -> None:
    if not path.exists():
        return
    text = path.read_text(encoding="utf-8")
    updated = text
    for old, new in replacements:
        updated = updated.replace(old, new)
    if updated != text:
        write(path, updated)


# ---------------------------------------------------------------------------
# Navigation contract
# ---------------------------------------------------------------------------
nav_path = DOCS / "NAVIGATION_RESOLVERS.yaml"
nav = load_yaml(nav_path)
nav["version"] = 2
nav["bottom_navigation"] = {
    "immutable": True,
    "rules": [
        "Набор, порядок, screen_id и пользовательские названия не меняются между player, trainer и organization actor.",
        "Вложенные кабинеты не создают вторую нижнюю навигацию.",
        "Модальные экраны могут временно скрывать нижнее меню, но не заменяют его другим набором вкладок.",
        "Изменение списка, порядка, названия или маршрута нижних вкладок является breaking change и блокируется CI.",
    ],
    "items": [
        {"id": "home", "title": "Профиль", "screen": "home.main", "route": "/"},
        {"id": "play", "title": "Игры", "screen": "play.main", "route": "/play"},
        {"id": "chats", "title": "Чаты", "screen": "chats.main", "route": "/chats"},
        {"id": "camps", "title": "Кэмпы", "screen": "camps.main", "route": "/camps"},
        {"id": "profile", "title": "Настройки", "screen": "profile.main", "route": "/profile"},
    ],
}
for resolver in nav.get("dynamic_destinations", []) or []:
    targets = resolver.get("resolves_to", []) or []
    resolver["resolves_to"] = [
        target for target in targets
        if not str(target).startswith("season.")
    ]
dump_yaml(nav_path, nav)


# ---------------------------------------------------------------------------
# Screen registry
# ---------------------------------------------------------------------------
screens_path = DOCS / "SCREENS.yaml"
screens_doc = load_yaml(screens_path)
screens_doc["version"] = 3
screens_doc["bottom_tabs"] = ["home", "play", "chats", "camps", "profile"]
removed_screen_ids = {
    "season.details",
    "season.create",
    "season.manage",
    "season.game_day",
    "season.game_day_manage",
}
new_screens: list[dict[str, Any]] = []
for screen in screens_doc.get("screens", []) or []:
    if not isinstance(screen, dict):
        continue
    screen_id = str(screen.get("id", ""))
    if screen_id in removed_screen_ids:
        continue
    if screen_id == "play.main":
        screen.update({
            "title": "Игры",
            "purpose": "Поиск, участие и управление играми, публичными тренировками и турнирами с выдачей по ближайшей дате.",
        })
    elif screen_id == "clubs.main":
        screen = {
            "id": "camps.main",
            "title": "Кэмпы",
            "route": "/camps",
            "section": "camps",
            "spec": "docs/screens/camps/main.md",
            "purpose": "Каталог, участие и управление кэмпами, лагерями и совместными игровыми поездками.",
            "variants": ["player", "trainer", "organization"],
            "back_fallback": None,
        }
    elif screen_id == "chats.main":
        screen["purpose"] = "Чаты игр, тренировок, турниров, кэмпов, организаций и личные сообщения."
    elif screen_id == "club.details":
        screen["section"] = "discovery"
        screen["back_fallback"] = "/play?scope=organizers"
    elif screen_id == "club.manage":
        screen["section"] = "organization"
    elif screen_id == "venue.details":
        screen["section"] = "discovery"
        screen["back_fallback"] = "/play?scope=venues"
    elif screen_id in {"player.public_profile", "trainer.public_profile"}:
        screen["section"] = "discovery"
    elif screen_id == "trainer.search":
        screen["purpose"] = "Поиск тренеров и отправка запросов одному или нескольким тренерам игрока."
    elif screen_id == "profile.competitions":
        screen["title"] = "Мои турниры"
        screen["purpose"] = "Участие, организация, черновики и завершённые турниры, включая сезонные."
    elif screen_id == "profile.trips":
        screen["title"] = "Мои кэмпы"
        screen["purpose"] = "Участие и организация кэмпов, лагерей и совместных поездок."
    elif screen_id == "tournament.details":
        screen["purpose"] = "Канонический экран классического, Короля пляжа или сезонного турнира."
    elif screen_id == "tournament.create":
        screen["purpose"] = "Создание классического, Короля пляжа или сезонного турнира."
    elif screen_id == "tournament.manage":
        screen["purpose"] = "Регистрация, игровые дни, жеребьёвка, раунды, таблица, корты, результаты и выплаты."
    elif screen_id == "tour.details":
        screen["title"] = "Кэмп"
        screen["purpose"] = "Программа, формат совместной игры, проживание при наличии, тренеры, цена, участники и чат."
        screen["back_fallback"] = "/camps"
    elif screen_id == "tour.create":
        screen["title"] = "Создание кэмпа"
        screen["purpose"] = "Создание совместного игрового кэмпа игроком, лагеря тренером или коммерческого кэмпа организацией."
        screen["back_fallback"] = "/camps?tab=manage"
    elif screen_id == "tour.manage":
        screen["title"] = "Управление кэмпом"
        screen["back_fallback"] = "/camps?tab=manage"
    elif screen_id == "tour.booking":
        screen["title"] = "Бронирование кэмпа"
    new_screens.append(screen)
screens_doc["screens"] = new_screens
dump_yaml(screens_path, screens_doc)


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
routes_path = DOCS / "ROUTES.yaml"
routes_doc = load_yaml(routes_path)
routes_doc["version"] = 3
new_routes: list[dict[str, Any]] = []
for route in routes_doc.get("routes", []) or []:
    if not isinstance(route, dict):
        continue
    screen_id = str(route.get("screen", ""))
    path = str(route.get("path", ""))
    if screen_id in removed_screen_ids or path.startswith("/seasons"):
        continue
    if screen_id == "play.main":
        route["accepts_query"] = [
            "tab", "category", "tournamentMode", "date", "sort", "distance",
            "level", "price", "freePlaces", "source", "scope", "organizerId",
            "playerId", "trainerId", "followed", "actorId",
        ]
    elif screen_id == "clubs.main":
        route = {
            "path": "/camps",
            "screen": "camps.main",
            "navigator": "tab",
            "access": "public_preview_or_authenticated",
            "accepts_query": ["tab", "type", "date", "sort", "destination", "level", "price", "actorId"],
        }
    elif screen_id == "club.details":
        route["back_fallback"] = "/play?scope=organizers"
    elif screen_id == "venue.details":
        route["back_fallback"] = "/play?scope=venues"
    elif screen_id == "tournament.details":
        route["accepts_query"] = ["tab", "dayId", "round", "mode"]
        route["back_fallback"] = "/play?category=tournaments"
    elif screen_id == "tournament.manage":
        route["accepts_query"] = ["tab", "dayId", "round", "mode"]
        route["back_fallback"] = "/profile/competitions?tab=organized"
    elif screen_id == "tour.details":
        route["back_fallback"] = "/camps"
    elif screen_id == "tour.create":
        route["back_fallback"] = "/camps?tab=manage"
    elif screen_id == "tour.manage":
        route["back_fallback"] = "/camps?tab=manage"
    new_routes.append(route)
routes_doc["routes"] = new_routes
dump_yaml(routes_path, routes_doc)


# ---------------------------------------------------------------------------
# Actions
# ---------------------------------------------------------------------------
actions_path = DOCS / "ACTIONS.yaml"
actions_doc = load_yaml(actions_path)
actions_doc["version"] = 3
replacement_sources = {"play.main", "clubs.main", "camps.main"}
new_actions: list[dict[str, Any]] = []
for action in actions_doc.get("actions", []) or []:
    if not isinstance(action, dict):
        continue
    action_id = str(action.get("id", ""))
    source = str(action.get("source", ""))
    destination = str(action.get("destination", ""))
    success = str(action.get("success", ""))
    context_text = str(action.get("context", {}))
    if source in replacement_sources:
        continue
    if (
        action_id.startswith("season.")
        or source.startswith("season.")
        or destination.startswith("season.")
        or success.startswith("season.")
        or "'season'" in context_text
        or '"season"' in context_text
        or "type=season" in context_text
    ):
        continue
    if action_id == "competitions.create_season":
        continue
    new_actions.append(action)

catalog_actions = [
    {"id": "games.change_tab", "label": "Все / Участвую / Управляю", "source": "play.main", "destination": "system.local_filter", "permission": "public"},
    {"id": "games.change_category", "label": "Игры / Тренировки / Турниры", "source": "play.main", "destination": "system.local_filter", "permission": "public"},
    {"id": "games.change_tournament_mode", "label": "Классика / Король пляжа / Сезонные", "source": "play.main", "destination": "system.local_filter", "permission": "public"},
    {"id": "games.open_search", "label": "Поиск", "source": "play.main", "destination": "system.games_search", "permission": "public"},
    {"id": "games.open_filters", "label": "Фильтры", "source": "play.main", "destination": "system.search_filters", "permission": "public"},
    {"id": "games.open_entity", "label": "Открыть", "source": "play.main", "destination": "dynamic.entity_details", "permission": "public"},
    {"id": "games.find_organizers", "label": "Добавить организацию", "source": "play.main", "destination": "system.organizer_search", "permission": "authenticated"},
    {"id": "games.find_players", "label": "Добавить игроков", "source": "play.main", "destination": "system.player_search", "permission": "authenticated"},
    {"id": "games.follow_organizer", "label": "Отслеживать организацию", "source": "play.main", "destination": "system.follow_organizer", "permission": "authenticated"},
    {"id": "games.open_organizer", "label": "Открыть организацию", "source": "play.main", "destination": "club.details", "permission": "public"},
    {"id": "games.open_venue", "label": "Открыть площадку", "source": "play.main", "destination": "venue.details", "permission": "public"},
    {"id": "games.create_game", "label": "Создать игру", "source": "play.main", "destination": "game.create", "permission": "authenticated", "context": {"actorId": "active_actor", "returnTo": "/play?tab=manage&category=games"}},
    {"id": "games.create_training", "label": "Создать тренировку", "source": "play.main", "destination": "training.create", "permission": "trainer_or_organization", "context": {"actorId": "active_actor", "returnTo": "/play?tab=manage&category=trainings"}},
    {"id": "games.create_tournament", "label": "Создать турнир", "source": "play.main", "destination": "tournament.create", "permission": "authenticated", "context": {"actorId": "active_actor", "returnTo": "/play?tab=manage&category=tournaments"}},
    {"id": "camps.change_tab", "label": "Все / Участвую / Управляю", "source": "camps.main", "destination": "system.local_filter", "permission": "public"},
    {"id": "camps.open_search", "label": "Поиск кэмпов", "source": "camps.main", "destination": "system.camps_search", "permission": "public"},
    {"id": "camps.open_camp", "label": "Открыть кэмп", "source": "camps.main", "destination": "tour.details", "permission": "public"},
    {"id": "camps.create", "label": "Создать кэмп", "source": "camps.main", "destination": "tour.create", "permission": "authenticated", "context": {"actorId": "active_actor", "returnTo": "/camps?tab=manage"}},
]
actions_doc["actions"] = new_actions + catalog_actions
dump_yaml(actions_path, actions_doc)


# ---------------------------------------------------------------------------
# Design tokens
# ---------------------------------------------------------------------------
tokens_path = DOCS / "DESIGN_TOKENS.yaml"
tokens = load_yaml(tokens_path)
tokens.setdefault("navigation", {}).setdefault("bottom_tabs", {})["items"] = [
    {"id": "home", "title": "Профиль", "route": "/"},
    {"id": "play", "title": "Игры", "route": "/play"},
    {"id": "chats", "title": "Чаты", "route": "/chats"},
    {"id": "camps", "title": "Кэмпы", "route": "/camps"},
    {"id": "profile", "title": "Настройки", "route": "/profile"},
]
dump_yaml(tokens_path, tokens)


# ---------------------------------------------------------------------------
# Competition formats: season becomes a tournament mode
# ---------------------------------------------------------------------------
formats_path = DOCS / "COMPETITION_FORMATS.yaml"
formats_doc = load_yaml(formats_path)
formats_doc["version"] = 3
formats = formats_doc.get("formats", {}) or {}
formats.pop("league_season", None)
for value in formats.values():
    if isinstance(value, dict) and isinstance(value.get("entity_types"), list):
        value["entity_types"] = [item for item in value["entity_types"] if item != "season"]
        if not value["entity_types"]:
            value["entity_types"] = ["tournament"]
formats["king_of_the_beach"] = {
    "title": "Король пляжа",
    "entity_types": ["tournament"],
    "mvp": True,
    "participant_unit": "individual",
    "purpose": "Игроки меняют партнёров и соперников, а итоговая таблица считается персонально.",
    "configuration": {
        "rounds": "configurable",
        "partner_rotation": "required",
        "repeat_partner_policy": "minimize",
        "standings": ["personal_wins", "point_difference", "points_scored", "head_to_head_when_applicable"],
    },
    "tabs": ["overview", "rounds", "standings", "participants", "chat"],
}
formats["seasonal_tournament"] = {
    "title": "Сезонный турнир",
    "entity_types": ["tournament"],
    "mvp": True,
    "purpose": "Один турнир с несколькими игровыми днями и общей накопительной таблицей.",
    "configuration": {
        "schedule_model": ["fixed_dates", "recurring_tournament_days"],
        "scoring_model": ["match_points", "personal_points", "hybrid"],
        "participant_roster": ["fixed", "flexible_by_tournament_day"],
        "court_count": "per_tournament_day",
    },
    "standings_default_order": ["series_points", "wins", "point_difference", "games_played", "head_to_head"],
    "tabs": ["overview", "tournament_days", "standings", "participants", "rules", "chat"],
}
formats_doc["formats"] = formats
formats_doc["catalog_modes"] = {
    "classic": {"title": "Классика", "formats": ["single_elimination", "round_robin", "groups_then_playoff", "swiss", "full_placement"]},
    "king_of_the_beach": {"title": "Король пляжа", "formats": ["king_of_the_beach"]},
    "seasonal": {"title": "Сезонные", "formats": ["seasonal_tournament"]},
}
dump_yaml(formats_path, formats_doc)


# ---------------------------------------------------------------------------
# Lifecycles and entity sections
# ---------------------------------------------------------------------------
lifecycle_path = DOCS / "ENTITY_LIFECYCLES.yaml"
lifecycle = load_yaml(lifecycle_path)
lifecycle["version"] = 4
entity_lifecycles = lifecycle.get("entity_lifecycles", {}) or {}
entity_lifecycles.pop("season", None)
common_rules = entity_lifecycles.get("common", {}).get("rules", []) or []
entity_lifecycles.setdefault("common", {})["rules"] = [
    str(rule).replace("game, training, tournament, season and tour", "game, training, tournament and camp")
    for rule in common_rules
]
tournament_lifecycle = entity_lifecycles.setdefault("tournament", {})
tournament_lifecycle["seasonal_mode"] = {
    "additional_statuses": ["between_tournament_days"],
    "required_for_complete": ["all_required_tournament_days_completed_or_cancelled", "standings_finalized"],
}
lifecycle["entity_lifecycles"] = entity_lifecycles
dump_yaml(lifecycle_path, lifecycle)

sections_path = DOCS / "ENTITY_SECTIONS.yaml"
sections = load_yaml(sections_path)
sections["version"] = 2
chat_types = sections.get("chat", {}).get("context_types", []) or []
sections.setdefault("chat", {})["context_types"] = [item for item in chat_types if item != "season"]
entity_types = sections.get("entity_types", {}) or {}
entity_types.pop("season", None)
tournament_sections = entity_types.setdefault("tournament", {}).setdefault("conditional_sections", {})
tournament_sections["tournament_days"] = "tournament_mode_is_seasonal"
tournament_sections["standings"] = "round_robin_or_swiss_or_groups_or_king_of_the_beach_or_seasonal"
sections["entity_types"] = entity_types
dump_yaml(sections_path, sections)


# ---------------------------------------------------------------------------
# Discovery source of truth
# ---------------------------------------------------------------------------
write(DOCS / "GAMES_CATALOG.yaml", """version: 1
scope: games_catalog
source_of_truth_for:
  - Игры bottom tab
  - catalog categories and ordering
  - followed organizers and saved players
  - empty-state recovery

bottom_tab:
  screen_id: play.main
  route: /play
  title: Игры
  primary_tabs: [all, participating, managing]
  category_chips: [games, trainings, tournaments]
  default_sort: starts_at_ascending
  sorting_rule: nearest_upcoming_first_then_later_dates

categories:
  games:
    title: Игры
    sources:
      - public_open_games_from_any_player
      - followed_organizers
      - saved_players
    rules:
      - public games are discoverable even when creator is not followed
      - followed and saved sources improve relevance but do not hide the open public catalog
  trainings:
    title: Тренировки
    sources:
      - public_trainings_from_private_trainers
      - public_trainings_from_organizations
    rules:
      - only whole public trainings appear in the catalog
      - private trainings remain accessible only through participation or invitation
  tournaments:
    title: Турниры
    mode_chips: [all, classic, king_of_the_beach, seasonal]
    mode_labels:
      all: Все
      classic: Классика
      king_of_the_beach: Король пляжа
      seasonal: Сезонные
    rules:
      - seasonal is a tournament mode and badge, not a separate entity
      - every list is ordered from nearest date to latest date

following:
  organizer_follow:
    owner: player_profile
    target: organization_actor
    selectable_categories: [games, trainings, tournaments, camps]
    effects:
      - prioritize matching public publications in catalogs
      - allow notification preferences per category
    forbidden_effects:
      - automatic participation
      - access to private events
  saved_players:
    source: docs/PLAYER_DIRECTORY.yaml
    effects:
      - prioritize public games created by saved players
    mutual_friendship_required: false

search:
  entities: [game, training, tournament, organization, venue, player]
  result_groups: [games, trainings, tournaments, organizers, venues, players]
  organizer_search_entry: empty_state_or_search_scope
  player_search_entry: empty_state_or_saved_players

empty_states:
  all:
    title: Пока нет подходящих игр
    actions:
      - id: games.find_organizers
        label: Добавить организацию
      - id: games.find_players
        label: Добавить игроков
    rules:
      - actions open search immediately rather than an explanatory dead-end screen
      - show nearby public suggestions when available
  participating:
    title: Вы пока нигде не участвуете
    primary_action: open_all
  managing:
    title: Вы ещё ничего не создали
    primary_action: open_create_menu

card:
  required_fields: [type, title, starts_at, venue, creator, price_or_free, capacity, free_places, relationship_status]
  date_is_prominent: true
  capacity_examples: [8 из 12, Осталось 4 места]
  primary_action_count: 1
""")

write(DOCS / "SEARCH_ARCHITECTURE.yaml", """version: 2
scope: contextual_search
universal_search_screen_in_mvp: false

contexts:
  games:
    screen: play.main
    entities: [game, training, tournament, organization, venue, player]
    categories: [games, trainings, tournaments]
    default_sort: starts_at_ascending
    tournament_modes: [classic, king_of_the_beach, seasonal]
  camps:
    screen: camps.main
    entities: [tour]
    creator_actor_types: [player, trainer, organization]
    default_sort: starts_at_ascending
  trainers:
    screen: trainer.search
    entry_points: [home.player_no_trainer, home.player_my_trainers, trainer.public_profile]
    entities: [trainer_profile]
  players:
    screens: [profile.players, player.picker, play.main]
    entities: [player_profile]
  chats:
    screen: chats.main
    entities: [conversation, conversation_member]
  personal_archive:
    parent: profile.main
    entities: [owned_or_related_entities]

rules:
  - search context determines initial entity type and filters
  - organizations and venues are found inside Games search, not a bottom tab
  - camps have a dedicated bottom tab and are not mixed into the Games category chips
  - seasonal competition is a tournament mode and never a separate search entity
  - all public lists default to nearest upcoming date first
  - blocked, hidden or nonpublic entities are excluded according to permissions
""")

write(DOCS / "screens/play/main.md", """# Игры

- Screen ID: `play.main`
- Route: `/play`
- Visible bottom-tab label: `Игры`
- Internal route and screen ID remain `play` for compatibility.
- Variants: `player`, `trainer`, `organization`
- Catalog contract: `docs/GAMES_CATALOG.yaml`

## Назначение

Один раздел для поиска, участия и управления локальными играми, публичными тренировками и турнирами. Кэмпы находятся в отдельной четвёртой вкладке. Самостоятельной сущности `Сезон` нет: повторяющееся соревнование является турниром с меткой `Сезонный`.

## Нижняя навигация

```text
Профиль · Игры · Чаты · Кэмпы · Настройки
```

На экране активна вкладка `Игры`.

## Верхняя панель

- активный actor и переключение профиля;
- строка поиска по событиям, организациям, площадкам и игрокам;
- фильтры;
- переключение список / карта, когда карта полезна;
- создание из вкладки `Управляю`.

## Основные вкладки

```text
Все · Участвую · Управляю
```

- `Все` — публичный каталог;
- `Участвую` — подтверждённые участия, приглашения, заявки и лист ожидания;
- `Управляю` — созданные события, доступные по роли, черновики и задачи.

## Категории

Первая горизонтальная строка:

```text
Игры · Тренировки · Турниры
```

Если выбран раздел `Турниры`, появляется вторая горизонтальная строка:

```text
Все · Классика · Король пляжа · Сезонные
```

Обе строки не переносятся и прокручиваются горизонтально, когда не помещаются.

## Состав выдачи

### Игры

- открытые публичные игры любых игроков;
- игры организаций, которые пользователь отслеживает;
- публичные игры сохранённых в `Мои игроки` людей;
- отметка источника не ограничивает общий публичный каталог.

### Тренировки

- публичные тренировки частных тренеров;
- публичные тренировки организаций;
- непубличная тренировка не показывается в `Все`, даже когда есть места.

### Турниры

- классические турнирные форматы;
- `Король пляжа` с персональной таблицей;
- `Сезонный турнир` с несколькими игровыми днями и общей таблицей.

`Сезонный` — бейдж и режим турнира, а не отдельная сущность или отдельный экран.

## Сортировка

Во всех категориях по умолчанию:

1. ближайшая будущая дата;
2. затем более поздние даты;
3. при одинаковом старте — расстояние и релевантность источника.

Дата и время всегда заметны на карточке. Завершённые элементы не смешиваются с предстоящими.

## Карточка

- дата и время;
- тип и формат;
- название;
- место;
- создатель: игрок, тренер или организация;
- цена либо `Бесплатно`;
- заполненность и свободные места;
- статус пользователя;
- одно основное действие.

Примеры заполненности: `8 из 12`, `Осталось 4 места`.

## Подписки и источники

Пользователь может отслеживать организацию и выбрать публикации: игры, тренировки, турниры или кэмпы. Отслеживание повышает приоритет подходящих публичных публикаций и может включать уведомления, но не создаёт участие и не открывает приватные события.

`Мои игроки` остаётся односторонним сохранённым списком. Публичные игры этих людей могут получать отметку `От вашего игрока`; отдельная взаимная сущность дружбы не вводится.

## Пустые состояния

Пустой каталог не заканчивается тупиком:

```text
Пока нет подходящих игр
[Добавить организацию] [Добавить игроков]
```

- `Добавить организацию` сразу открывает поиск организаций;
- `Добавить игроков` сразу открывает поиск публичных игроков;
- после подписки или сохранения пользователь возвращается в каталог с обновлённой выдачей;
- при наличии общедоступных вариантов рядом показываются рекомендации.

Пустое `Участвую` ведёт в `Все`. Пустое `Управляю` показывает создание игры, тренировки или турнира согласно правам actor.

## Навигация

Карточка открывает канонический detail screen. Возврат восстанавливает вкладку, категорию, чипы, фильтры и позицию списка. Организации и площадки открываются как deep-link экраны из поиска; отдельной нижней вкладки для них нет.

## Состояния

- loading skeleton;
- пустой каталог;
- пустое участие;
- пустое управление;
- нет результатов после фильтра;
- геолокация выключена;
- offline read-only;
- частичная ошибка карты;
- событие стало непубличным;
- actor permission changed.
""")

write(DOCS / "screens/camps/main.md", """# Кэмпы

- Screen ID: `camps.main`
- Route: `/camps`
- Visible bottom-tab label: `Кэмпы`
- Variants: `player`, `trainer`, `organization`

## Назначение

Отдельная витрина многодневных или выездных волейбольных форматов. Кэмп может создать организация, частный тренер или игрок, который собирает людей вместе играть. Коммерческое проживание и транспорт необязательны.

## Нижняя навигация

```text
Профиль · Игры · Чаты · Кэмпы · Настройки
```

На экране активна вкладка `Кэмпы`.

## Основные вкладки

```text
Все · Участвую · Управляю
```

## Быстрые фильтры

```text
Ближайшие · На море · С тренером · Только игры · С проживанием
```

Чипы прокручиваются горизонтально и не переносятся.

## Создатели

- player actor — совместная поездка или серия игр без коммерческого пакета;
- trainer actor — тренировочный лагерь с программой;
- organization actor — кэмп с пакетами, сотрудниками, проживанием и платежами.

## Сортировка и карточка

По умолчанию кэмпы идут от ближайшей даты к самой поздней. Карточка показывает даты, место, создателя, формат, подходящий уровень, длительность, цену или бюджет, свободные места и одно действие.

## Создание и управление

`Кэмпы → Управляю → Создать кэмп`. Мастер адаптируется к actor и не требует проживания, транспорта или коммерческой цены для обычной группы игроков.

## Состояния

- loading;
- нет опубликованных кэмпов;
- нет участий;
- нет управляемых кэмпов;
- нет результатов фильтра;
- offline read-only;
- геолокация недоступна;
- кэмп заполнен или набор закрыт.
""")


# ---------------------------------------------------------------------------
# Text documents and active source cleanup
# ---------------------------------------------------------------------------
menu_replacements = [
    ("Профиль · События · Чаты · Клубы · Настройки", "Профиль · Игры · Чаты · Кэмпы · Настройки"),
    ("`Профиль · События · Чаты · Клубы · Настройки`", "`Профиль · Игры · Чаты · Кэмпы · Настройки`"),
]
for path in [ROOT / "AGENTS.md", ROOT / "README.md", DOCS / "UI_RULES.md", DOCS / "DESIGN_SYSTEM.md", DOCS / "APP_MAP.md", DOCS / "ARCHITECTURE.md", DOCS / "ARCHITECTURE_AUDIT.md", DOCS / "MVP_SCOPE.md", DOCS / "USER_FLOWS.md", DOCS / "TEST_SCENARIOS.md", DOCS / "screens/home/main.md", DOCS / "screens/profile/main.md", DOCS / "screens/profile/my-calendar.md", DOCS / "screens/chats/main.md", DOCS / "screens/chats/details.md"]:
    replace_in(path, menu_replacements)

replace_in(ROOT / "README.md", [
    ("`События` — игры, тренировки, турниры, сезоны, туры, поездки и кэмпы;", "`Игры` — игры, публичные тренировки и турниры;"),
    ("`Клубы` — только клубы, площадки и корты;", "`Кэмпы` — лагеря, совместные поездки и многодневные игровые форматы;"),
    ("поиск тренеров открывается игроком", "поиск организаций, площадок и игроков находится внутри `Игры`, а поиск тренеров открывается игроком"),
])

replace_in(DOCS / "DATA_MODEL.md", [
    ("- `seasons`;\n- `season_game_days`;", "- `tournament_days` — игровые дни сезонного турнира;\n- `tournament_series_configs` — правила накопительной таблицы сезонного турнира;"),
    ("season_game_day", "tournament_day"),
    ("формата сезона", "режима сезонного турнира"),
    ("сезонной таблицы", "таблицы сезонного турнира"),
])

replace_in(DOCS / "PROFILE_SETTINGS.yaml", [("season", "seasonal_tournament")])
replace_in(DOCS / "PLAYER_DIRECTORY.yaml", [
    ("игру, тренировку, турнир, сезон или тур", "игру, тренировку, турнир или кэмп"),
    ("игры, тренировки, турниры, сезоны и туры", "игры, тренировки, турниры и кэмпы"),
])

replace_in(DOCS / "screens/profile/my-calendar.md", [
    ("- игровой день сезона;", "- игровой день сезонного турнира;"),
    ("занятия, группы, окна расписания", "занятия, окна расписания"),
    ("Назад → Профиль. При deep link fallback `/profile`.", "Назад → Настройки. При deep link fallback `/profile`."),
])

replace_in(DOCS / "screens/profile/my-competitions.md", [
    ("# Мои турниры и сезоны", "# Мои турниры"),
    ("турниры и сезоны", "турниры"),
    ("Турниры и сезоны", "Турниры"),
    ("сезон", "сезонный турнир"),
    ("Сезон", "Сезонный турнир"),
])

replace_in(DOCS / "screens/profile/my-trips.md", [
    ("# Мои туры и поездки", "# Мои кэмпы"),
    ("туры и поездки", "кэмпы"),
    ("Туры и поездки", "Кэмпы"),
])

# Remove legacy standalone season specifications from the active branch.
for relative in [
    "screens/shared/season-create.md",
    "screens/shared/season-details.md",
    "screens/shared/season-game-day.md",
    "screens/shared/season-manage.md",
]:
    path = DOCS / relative
    if path.exists():
        path.unlink()

# Decisions record.
decisions_path = DOCS / "DECISIONS.md"
decisions_text = decisions_path.read_text(encoding="utf-8")
marker = "## D-029 — Игры и Кэмпы заменяют События и Клубы"
if marker not in decisions_text:
    write(decisions_path, decisions_text.rstrip() + """

## D-029 — Игры и Кэмпы заменяют События и Клубы

Статус: принято.

Нижнее меню: `Профиль · Игры · Чаты · Кэмпы · Настройки`. Вторая вкладка содержит игры, публичные тренировки и турниры. Четвёртая вкладка содержит кэмпы, которые могут создавать player, trainer и organization actor. Организации, площадки и игроки ищутся внутри `Игры` и не имеют отдельной нижней вкладки.

## D-030 — Сезон является режимом турнира

Статус: принято.

Отдельные entity, screen_id и route сезона удаляются. Повторяющееся соревнование создаётся как `tournament` с режимом `seasonal`, несколькими игровыми днями и общей накопительной таблицей. В пользовательском интерфейсе используется метка `Сезонный турнир`.

## D-031 — Пустая выдача ведёт к источникам игр

Статус: принято.

Пустой каталог `Игры` предлагает `Добавить организацию` и `Добавить игроков`. Действия сразу открывают соответствующий поиск. Публичный каталог всё равно показывает открытые игры любых авторов; отслеживаемые организации и сохранённые игроки повышают релевантность, но не ограничивают выдачу.
""")


# ---------------------------------------------------------------------------
# Validators
# ---------------------------------------------------------------------------
nav_validator = ROOT / "scripts/validate_navigation.py"
replace_in(nav_validator, [
    ('["home", "play", "chats", "clubs", "profile"]', '["home", "play", "chats", "camps", "profile"]'),
    ("Bottom navigation IDs must be exactly home, play, chats, clubs, profile", "Bottom navigation IDs must be exactly home, play, chats, camps, profile"),
    ('legacy_phrase = "Главная · События · Чаты · Клубы · Профиль"', 'legacy_phrase = "Профиль · События · Чаты · Клубы · Настройки"'),
    ('{"game.create", "training.create", "tournament.create", "season.create", "tour.create"}', '{"game.create", "training.create", "tournament.create", "tour.create"}'),
])
validator_text = nav_validator.read_text(encoding="utf-8")
anchor = "    # Block known obsolete concepts from returning to source-of-truth navigation docs.\n"
block = """    # Standalone season and the removed Clubs bottom tab are forbidden in active registries.\n    forbidden_registry_tokens = {\n        DOCS / \"SCREENS.yaml\": [\"season.details\", \"season.create\", \"season.manage\", \"clubs.main\"],\n        DOCS / \"ROUTES.yaml\": [\"/seasons/\", \"screen: season.\", \"screen: clubs.main\"],\n        DOCS / \"NAVIGATION_RESOLVERS.yaml\": [\"season.details\", \"season.manage\", \"id: clubs\"],\n        DOCS / \"ENTITY_SECTIONS.yaml\": [\"  season:\"],\n    }\n    for registry_path, tokens in forbidden_registry_tokens.items():\n        registry_text = registry_path.read_text(encoding=\"utf-8\")\n        for token in tokens:\n            if token in registry_text:\n                errors.append(f\"Removed concept {token!r} remains in {registry_path.relative_to(ROOT)}\")\n\n"""
if block.strip() not in validator_text:
    validator_text = validator_text.replace(anchor, block + anchor)
    write(nav_validator, validator_text)

ui_validator = ROOT / "scripts/validate_design_system.py"
ui_text = ui_validator.read_text(encoding="utf-8")
ui_text = re.sub(
    r"    expected_tabs = \[.*?\n    \]",
    """    expected_tabs = [
        {\"id\": \"home\", \"title\": \"Профиль\", \"route\": \"/\"},
        {\"id\": \"play\", \"title\": \"Игры\", \"route\": \"/play\"},
        {\"id\": \"chats\", \"title\": \"Чаты\", \"route\": \"/chats\"},
        {\"id\": \"camps\", \"title\": \"Кэмпы\", \"route\": \"/camps\"},
        {\"id\": \"profile\", \"title\": \"Настройки\", \"route\": \"/profile\"},
    ]""",
    ui_text,
    count=1,
    flags=re.S,
)
write(ui_validator, ui_text)

# Remove this one-off migration and workflow from the resulting commit.
for path in (SELF, BRANCH_WORKFLOW):
    if path.exists():
        path.unlink()

print("Games, camps and seasonal tournament migration completed.")
