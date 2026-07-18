#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
OLD_NAV = "Главная · События · Чаты · Клубы · Профиль"
NEW_NAV = "Профиль · События · Чаты · Клубы · Настройки"


def load_yaml(path: Path) -> dict[str, Any]:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a mapping")
    return value


def save_yaml(path: Path, value: dict[str, Any]) -> None:
    path.write_text(yaml.safe_dump(value, allow_unicode=True, sort_keys=False, width=120), encoding="utf-8")


def upsert_after(items: list[dict[str, Any]], key: str, key_value: str, item: dict[str, Any], after_value: str) -> None:
    for index, current in enumerate(items):
        if str(current.get(key)) == key_value:
            items[index] = item
            return
    for index, current in enumerate(items):
        if str(current.get(key)) == after_value:
            items.insert(index + 1, item)
            return
    items.append(item)


def replace_text(path: Path, replacements: list[tuple[str, str]]) -> None:
    if not path.exists():
        return
    text = path.read_text(encoding="utf-8")
    updated = text
    for old, new in replacements:
        updated = updated.replace(old, new)
    if updated != text:
        path.write_text(updated, encoding="utf-8")


def append_once(path: Path, marker: str, content: str) -> None:
    text = path.read_text(encoding="utf-8") if path.exists() else ""
    if marker not in text:
        if text and not text.endswith("\n"):
            text += "\n"
        path.write_text(text + "\n" + content.strip() + "\n", encoding="utf-8")


# 1. Machine-readable screen and route registries.
screens_path = DOCS / "SCREENS.yaml"
screens_doc = load_yaml(screens_path)
screens = screens_doc.get("screens", [])
for screen in screens:
    if screen.get("id") == "home.main":
        screen["title"] = "Профиль"
        screen["purpose"] = "Профильная страница активного actor с личной информацией, тренерами, ближайшими событиями и задачами."
    elif screen.get("id") == "profile.main":
        screen["title"] = "Настройки"
        screen["purpose"] = "Список настроек аккаунта, профилей, архивов, платежей и служебных разделов."
    elif screen.get("id") == "profile.settings":
        screen["title"] = "Аккаунт и приложение"
        screen["purpose"] = "Безопасность, уведомления, приватность, внешний вид и профильные параметры."
    elif screen.get("id") == "clubs.main":
        screen["purpose"] = "Публичный каталог клубов, площадок и кортов."

trainer_search_screen = {
    "id": "trainer.search",
    "title": "Найти тренера",
    "route": "/trainers/search",
    "section": "home",
    "spec": "docs/screens/shared/trainer-search.md",
    "purpose": "Поиск тренеров и создание подтверждаемой связи игрока с одним или несколькими тренерами.",
    "variants": ["player"],
    "permission": "authenticated_player",
    "back_fallback": "/",
}
upsert_after(screens, "id", "trainer.search", trainer_search_screen, "trainer.public_profile")
save_yaml(screens_path, screens_doc)

routes_path = DOCS / "ROUTES.yaml"
routes_doc = load_yaml(routes_path)
routes = routes_doc.get("routes", [])
trainer_search_route = {
    "path": "/trainers/search",
    "screen": "trainer.search",
    "navigator": "home_stack",
    "parent": "/",
    "access": "authenticated_onboarded",
    "permission": "authenticated_player",
    "accepts_query": ["city", "distance", "specialization", "level", "language", "format", "availability"],
    "back_fallback": "/",
}
upsert_after(routes, "path", "/trainers/search", trainer_search_route, "/trainers/:trainerId")
save_yaml(routes_path, routes_doc)

nav_path = DOCS / "NAVIGATION_RESOLVERS.yaml"
nav_doc = load_yaml(nav_path)
for item in nav_doc.get("bottom_navigation", {}).get("items", []):
    if item.get("id") == "home":
        item["title"] = "Профиль"
    elif item.get("id") == "profile":
        item["title"] = "Настройки"
save_yaml(nav_path, nav_doc)

tokens_path = DOCS / "DESIGN_TOKENS.yaml"
tokens = load_yaml(tokens_path)
for item in tokens.get("navigation", {}).get("bottom_tabs", {}).get("items", []):
    if item.get("id") == "home":
        item["title"] = "Профиль"
    elif item.get("id") == "profile":
        item["title"] = "Настройки"
save_yaml(tokens_path, tokens)

# 2. Actions.
actions_path = DOCS / "ACTIONS.yaml"
actions_doc = load_yaml(actions_path)
actions = actions_doc.get("actions", [])
new_actions = [
    {
        "id": "profile.open_trainer_search",
        "label": "Найти тренера",
        "source": "home.main",
        "destination": "trainer.search",
        "permission": "authenticated_player",
    },
    {
        "id": "profile.open_linked_trainer",
        "label": "Открыть тренера",
        "source": "home.main",
        "destination": "trainer.public_profile",
        "permission": "authenticated_player",
    },
    {
        "id": "profile.cancel_trainer_request",
        "label": "Отменить запрос тренеру",
        "source": "home.main",
        "destination": "system.cancel_trainer_relationship_confirmation",
        "permission": "relationship_request_owner",
    },
    {
        "id": "profile.remove_trainer_relationship",
        "label": "Убрать тренера",
        "source": "home.main",
        "destination": "system.remove_trainer_relationship_confirmation",
        "permission": "relationship_participant",
    },
    {
        "id": "trainer.search_query",
        "label": "Поиск тренеров",
        "source": "trainer.search",
        "destination": "system.local_search",
        "permission": "authenticated_player",
    },
    {
        "id": "trainer.search_filters",
        "label": "Фильтры тренеров",
        "source": "trainer.search",
        "destination": "system.search_filters",
        "permission": "authenticated_player",
    },
    {
        "id": "trainer.search_open_profile",
        "label": "Открыть профиль тренера",
        "source": "trainer.search",
        "destination": "trainer.public_profile",
        "permission": "authenticated_player",
    },
    {
        "id": "trainer.request_from_search",
        "label": "Добавить тренера",
        "source": "trainer.search",
        "destination": "system.create_trainer_relationship_request",
        "permission": "authenticated_player",
    },
    {
        "id": "trainer.request_from_profile",
        "label": "Добавить тренера",
        "source": "trainer.public_profile",
        "destination": "system.create_trainer_relationship_request",
        "permission": "authenticated_player",
    },
    {
        "id": "trainer.accept_player_relationship",
        "label": "Подтвердить игрока",
        "source": "global.notifications",
        "destination": "system.accept_trainer_relationship",
        "permission": "relationship_target_trainer",
    },
    {
        "id": "trainer.decline_player_relationship",
        "label": "Отклонить запрос",
        "source": "global.notifications",
        "destination": "system.decline_trainer_relationship_confirmation",
        "permission": "relationship_target_trainer",
    },
    {
        "id": "trainer.message_requesting_player",
        "label": "Написать игроку",
        "source": "global.notifications",
        "destination": "system.open_or_create_direct_chat",
        "permission": "trainer_relationship_request_recipient",
    },
]
by_id = {str(action.get("id")): index for index, action in enumerate(actions)}
for action in new_actions:
    action_id = action["id"]
    if action_id in by_id:
        actions[by_id[action_id]] = action
    else:
        actions.append(action)
# Rename the deeper settings action to avoid two identical Settings labels.
for action in actions:
    if action.get("id") == "nav.open_profile_settings":
        action["label"] = "Аккаунт и приложение"
save_yaml(actions_path, actions_doc)

# 3. Canonical relationship model and trainer search specification.
(DOCS / "TRAINER_RELATIONSHIPS.yaml").write_text("""version: 1
concept: player_trainer_relationship
source_of_truth: docs/TRAINER_RELATIONSHIPS.yaml

principles:
  - player may have multiple active trainers
  - relationship is distinct from My Players and event participation
  - player initiates a request from the Profile tab or trainer public profile
  - label Trains with is shown only after trainer confirmation
  - request grants the selected trainer permission to view the request context and send a direct message
  - either side may end the relationship without deleting historical events, chats, payments or attendance
  - blocked users cannot create, accept or message through a relationship

statuses:
  requested:
    player_label: Запрос отправлен
    trainer_label: Новый игрок
    trainer_actions: [message, accept, decline]
  active:
    player_label: Тренируется у
    trainer_label: Мой игрок
    actions: [open_profile, message, remove]
  declined:
    visible_to_player: temporary
  cancelled:
    visible_to_trainer: false
  ended_by_player:
    active: false
  ended_by_trainer:
    active: false

player_profile_block:
  empty_title: Без тренера
  empty_action: Найти тренера
  pending_item: Запрос отправлен
  active_item: Тренируется у {trainer_name}
  multiple_relationships: true
  order: [active, requested]

trainer_notification:
  title: Новый игрок
  body: "{player_name} хочет добавить вас как тренера"
  actions: [open_player_profile, message, accept, decline]

search:
  route: /trainers/search
  fields: [name, city, distance, specialization, player_level, language, session_format, availability]
  card: [photo, name, verification, city, specializations, player_levels, nearest_public_training]
  ratings_forbidden: true
  blocked_or_hidden_profiles_excluded: true
  pagination: cursor
  recent_queries: local_private
  typo_tolerance: implementation_required

side_effects:
  on_request:
    - create notification for trainer actor
    - allow one direct conversation context between requester and trainer
  on_accept:
    - mark relationship active
    - show trainer on player Profile tab
    - ensure player is visible in trainer My Players working list
    - notify player
  on_decline:
    - close request
    - notify player without exposing a reason unless trainer supplies one
  on_end:
    - revoke relationship-only permissions
    - preserve shared event history and allowed chat history
""", encoding="utf-8")

trainer_search_spec = """# Найти тренера

- Screen ID: `trainer.search`
- Route: `/trainers/search`
- Parent: первая вкладка `Профиль`
- Variants: `player`
- Source of truth: `docs/TRAINER_RELATIONSHIPS.yaml`

## Назначение

Помочь игроку найти одного или нескольких тренеров, открыть публичный профиль и отправить подтверждаемый запрос на связь. Экран не является частью `Клубов` и не ищет события, туры или кэмпы.

## Навигация

- открывается из блока `Без тренера`, `Мои тренеры` или публичного профиля тренера;
- глобальное нижнее меню сохраняется;
- активна вкладка `Профиль`;
- назад возвращает на `/` с сохранённой позицией;
- результат открывает `/trainers/:trainerId`;
- туры и кэмпы ищутся только в `Событиях`.

## Верхняя часть

- назад;
- заголовок `Найти тренера`;
- поле поиска по имени;
- город или область поиска;
- кнопка расширенных фильтров.

## Быстрые фильтры

В одной горизонтально прокручиваемой строке:

```text
Рядом · Для новичков · Для любителей · Индивидуально · Есть занятия
```

Показывается не более трёх приоритетных чипов одновременно; остальные параметры находятся в bottom sheet. Чипы не переносятся на вторую строку.

## Расширенные фильтры

- город и расстояние;
- специализация;
- уровень игроков;
- язык;
- индивидуальный, парный или групповой формат;
- наличие публичных тренировок;
- доступность для новых игроков;
- подтверждённый профиль.

## Карточка тренера

- фото;
- имя;
- статус проверки;
- город;
- специализации;
- уровни игроков;
- ближайшая публичная тренировка, когда есть;
- одно основное действие `Добавить тренера` либо статус `Запрос отправлен` / `Тренируется у`.

Числовой рейтинг и звёзды не используются. Вся карточка открывает публичный профиль.

## Создание связи

1. Игрок нажимает `Добавить тренера`.
2. Создаётся статус `requested`.
3. На Профиле игрока появляется `Запрос отправлен`.
4. Тренер получает уведомление `Новый игрок`.
5. Тренер может открыть профиль игрока, написать, подтвердить или отклонить.
6. После подтверждения игрок видит `Тренируется у {имя}`.

Игрок может иметь несколько активных и ожидающих связей. Нельзя показывать `Тренируется у` до подтверждения тренером.

## Состояния

- loading;
- нет результатов;
- геолокация отключена;
- offline read-only;
- запрос уже отправлен;
- связь уже активна;
- профиль скрыт или заблокирован;
- rate limit;
- ошибка отправки запроса.
"""
(DOCS / "screens/shared/trainer-search.md").write_text(trainer_search_spec, encoding="utf-8")

# 4. Rewrite first and fifth tab specifications.
home_spec = f"""# Профиль

- Screen ID: `home.main`
- Route: `/`
- User-facing bottom-tab title: `Профиль`
- Internal tab ID remains `home`
- Variants: `player`, `trainer`, `organization`
- UI contract: `docs/DESIGN_SYSTEM.md` and `docs/DESIGN_TOKENS.yaml`

Первая вкладка является профильной страницей активного actor. Она соединяет публичную идентичность, ближайшие события и несколько действительно важных действий, но не заменяет каталог `События` и список `Настройки`.

## Общая верхняя часть

- фото или логотип активного actor;
- имя и тип профиля;
- город;
- статус проверки, когда применимо;
- уведомления;
- переключение actor;
- редактирование публичной информации;
- корневой экран не показывает кнопку назад.

## Игрок

Порядок блоков:

1. шапка спортивного профиля;
2. `Мои тренеры`;
3. ближайшее участие и требуемое действие;
4. сегодня в календаре;
5. приглашения;
6. созданные игроком события, если есть;
7. рекомендации событий.

### Мои тренеры

- нет активных и ожидающих связей → карточка `Без тренера` и действие `Найти тренера`;
- запрос ожидает → имя тренера и статус `Запрос отправлен`;
- подтверждённая связь → `Тренируется у {{trainer_name}}`;
- поддерживается несколько тренеров;
- каждая строка открывает публичный профиль тренера;
- игрок может отменить ожидающий запрос или завершить активную связь через контекстное меню.

После выбора тренера надпись `Тренируется у` не появляется сразу: сначала тренер подтверждает запрос. Это предотвращает ложное указание тренера.

## Тренер

Порядок блоков:

1. шапка и предпросмотр публичного профиля;
2. новые запросы игроков;
3. тренировки сегодня;
4. посещаемость, которую нужно заполнить;
5. заявки и неоплаченные места;
6. ближайшие занятия;
7. блок `Управляю` с играми, турнирами, сезонами, турами и кэмпами;
8. личные участия тренера как игрока.

Новый запрос игрока также приходит уведомлением. Тренер может открыть игрока, написать ему, подтвердить или отклонить связь. После подтверждения игрок появляется в рабочем списке `Мои игроки` тренера.

## Организация

Порядок блоков:

1. публичная шапка организации;
2. операционная сводка сегодня;
3. события, требующие действий;
4. загрузка площадок и кортов;
5. заявки и оплаты;
6. назначенные сотрудники;
7. блок `Управляю`;
8. сообщения и инциденты.

## События и поиск

Игры, тренировки, турниры, сезоны, туры, поездки и кэмпы ищутся в `Событиях`. Первая вкладка показывает только связанные с пользователем ближайшие элементы и рекомендации. Поиск тренеров для игрока открывается из блока `Мои тренеры`.

## Нижняя навигация

Всегда один глобальный компонент:

```text
{NEW_NAV}
```

На этом экране активна вкладка `Профиль`.

## Состояния

- loading;
- профиль заполнен не полностью;
- `Без тренера`;
- запрос тренеру ожидает;
- нет ближайших действий;
- partial error отдельного блока;
- offline с последними сохранёнными данными;
- permission changed.
"""
(DOCS / "screens/home/main.md").write_text(home_spec, encoding="utf-8")

settings_hub = f"""# Настройки

- Screen ID: `profile.main`
- Route: `/profile`
- User-facing bottom-tab title: `Настройки`
- Internal tab ID remains `profile`
- Variants: `player`, `trainer`, `organization`

Пятая вкладка является служебным списком аккаунта и активного actor. Здесь находятся настройки, архивы, платежи и административные переходы; публичная профильная страница находится в первой вкладке `Профиль`.

## Верхняя часть

- компактный активный actor;
- переключение actor;
- статус заполнения или проверки;
- переход к первой вкладке для просмотра профильной страницы.

## Общие разделы

- Мои профили;
- Мой календарь;
- архив игр, тренировок, турниров, сезонов, туров и поездок;
- Мои игроки;
- Статистика;
- Платежи и выплаты согласно actor;
- Аккаунт и приложение;
- Безопасность, приватность и уведомления;
- Помощь и юридические документы;
- Опасные действия.

## Вариант игрока

Дополнительно показывает личные архивы участий и созданных событий. Связи `Мои тренеры` управляются на первой вкладке `Профиль`, а не дублируются здесь.

## Вариант тренера

Дополнительно показывает расписание, рабочий список `Мои игроки`, выплаты, статистику и ссылку на публичный профиль. Новые запросы игроков показываются на первой вкладке и в уведомлениях.

## Вариант организации

Дополнительно показывает переходы к площадкам, сотрудникам, финансам, аудиту и настройкам организации без отдельной нижней навигации.

## Нижняя навигация

```text
{NEW_NAV}
```

На этом экране активна вкладка `Настройки`.

## Состояния

- actor draft;
- verification pending;
- permission changed;
- offline;
- раздел временно недоступен.
"""
(DOCS / "screens/profile/main.md").write_text(settings_hub, encoding="utf-8")

clubs_spec = f"""# Клубы

- Screen ID: `clubs.main`
- Route: `/clubs`
- Variants: `player`, `trainer`, `organization`

Раздел предназначен только для публичного каталога клубов, площадок и кортов. Тренеры ищутся игроком через блок `Мои тренеры` на вкладке `Профиль`; туры, поездки и кэмпы находятся в `Событиях`.

## Категории

```text
Клубы · Площадки и корты
```

Поиск, быстрые фильтры, расширенные фильтры и карта относятся к выбранной категории.

## Игрок

Приоритеты: ближайшие площадки и клубы с подходящими событиями.

## Тренер

Дополнительно показываются клубы, где тренер работает, и доступные площадки. Собственный публичный профиль находится на первой вкладке `Профиль`.

## Организация

Сверху показываются `Моя организация`, собственные площадки и действие управления клубом. Сотрудники и тренеры открываются внутри организации, а не как глобальная категория поиска.

## Карточка клуба

- название;
- город;
- площадки;
- ближайшие публичные события;
- публичные тренеры клуба;
- одно главное действие.

## Карточка площадки

- адрес;
- корты;
- покрытие;
- доступность;
- ближайший слот;
- одно главное действие.

## Нижняя навигация

```text
{NEW_NAV}
```

Активна вкладка `Клубы`.

## Состояния

- геолокация отключена;
- нет результатов;
- карта недоступна;
- организация без публичной страницы;
- offline.
"""
(DOCS / "screens/clubs/main.md").write_text(clubs_spec, encoding="utf-8")

# 5. Update connected specs and source-of-truth documents.
append_once(
    DOCS / "screens/shared/notifications.md",
    "## Связь игрока и тренера",
    """## Связь игрока и тренера

Уведомление тренеру `Новый игрок` создаётся после запроса игрока и содержит переход в публичный профиль игрока, а также действия `Написать`, `Подтвердить` и `Отклонить`. Уведомление игроку сообщает о подтверждении или отклонении. Текст `Тренируется у` используется только после подтверждения.
""",
)
append_once(
    DOCS / "PLAYER_DIRECTORY.yaml",
    "trainer_relationship_integration:",
    """trainer_relationship_integration:
  source_of_truth: docs/TRAINER_RELATIONSHIPS.yaml
  rules:
    - confirmed trainer relationship is separate from actor_player_links
    - after trainer accepts, player is ensured in trainer actor My Players working list
    - ending trainer relationship does not silently delete trainer saved-player entry; trainer may remove it separately
    - unconfirmed request does not create event participation or access to event chats
""",
)
append_once(
    DOCS / "DATA_MODEL.md",
    "## 14. Связь игрока и тренера",
    """## 14. Связь игрока и тренера

Источник истины: `docs/TRAINER_RELATIONSHIPS.yaml`.

- `player_trainer_relationships` — player profile, trainer actor, status, initiator and timestamps;
- `player_trainer_relationship_events` — request, message permission, accept, decline and end audit;
- `trainer_relationship_message_grants` — ограниченный контекст прямого диалога после запроса;
- `trainer_search_documents` — поисковое представление публичных полей тренера.

Статусы: `requested`, `active`, `declined`, `cancelled`, `ended_by_player`, `ended_by_trainer`. Надпись `Тренируется у` разрешена только для `active`. Один player profile может иметь несколько активных trainer relationships. Принятие обеспечивает наличие игрока в рабочем списке `Мои игроки` тренера, но сама связь остаётся отдельной подтверждаемой сущностью.
""",
)
append_once(
    DOCS / "TEST_SCENARIOS.md",
    "### A-14. Игрок находит и добавляет тренера",
    """### A-14. Игрок находит и добавляет тренера

1. Игрок открывает первую вкладку `Профиль` и видит `Без тренера`.
2. Нажимает `Найти тренера`, применяет фильтры и открывает публичный профиль.
3. Отправляет запрос; на Профиле отображается `Запрос отправлен`, но не `Тренируется у`.
4. Тренер получает уведомление `Новый игрок`, открывает профиль и может написать игроку.
5. После подтверждения игрок видит `Тренируется у {имя}`, а игрок появляется в `Мои игроки` trainer actor.
6. Игрок повторяет сценарий со вторым тренером; обе активные связи отображаются.
7. Туры и кэмпы при этом находятся только в `Событиях`, а не в `Клубах`.
""",
)

# Update trainer public profile with relationship states.
append_once(
    DOCS / "screens/clubs/trainer-details.md",
    "## Связь с игроком",
    """## Связь с игроком

Авторизованный игрок видит одно из состояний: `Добавить тренера`, `Запрос отправлен` или `Тренируется у`. Запрос создаёт подтверждаемую связь и уведомление тренеру. До подтверждения нельзя показывать `Тренируется у`. Один игрок может иметь несколько тренеров. Туры и кэмпы тренера открываются как события и не создают отдельный каталог в `Клубах`.
""",
)

# Search scopes.
(DOCS / "SEARCH_ARCHITECTURE.yaml").write_text("""version: 1
scope: contextual_search
universal_search_screen_in_mvp: false

contexts:
  events:
    screen: play.main
    entities: [game, training, tournament, season, tour]
    tour_variants: [informal, training_camp, organization_package]
    user_labels: [Игры, Тренировки, Турниры, Сезоны, Туры и кэмпы]
  clubs:
    screen: clubs.main
    entities: [club, venue, court]
  trainers:
    screen: trainer.search
    entry_points: [home.player_no_trainer, home.player_my_trainers, trainer.public_profile]
    entities: [trainer_profile]
  players:
    screens: [profile.players, player.picker]
    entities: [player_profile]
  chats:
    screen: chats.main
    entities: [conversation, conversation_member]
  personal_archive:
    parent: profile.main
    entities: [owned_or_related_entities]

rules:
  - search context determines initial entity type and filters
  - tours and training camps are discoverable only in Events
  - global Clubs catalog does not contain trainer or tour categories
  - trainer search is available to player profile from the first Profile tab
  - all result cards open canonical detail screens
  - blocked, hidden or nonpublic entities are excluded according to permissions
""", encoding="utf-8")

# 6. Decisions and broad terminology synchronization.
append_once(
    DOCS / "DECISIONS.md",
    "## D-026 — Первая вкладка является Профилем",
    f"""## D-026 — Первая вкладка является Профилем, пятая — Настройками

Статус: принято; заменяет пользовательские названия из D-001.

Пользовательские названия нижних вкладок: `{NEW_NAV}`. Внутренние идентификаторы и маршруты сохраняются: `home` → `/`, `profile` → `/profile`. Первая вкладка показывает профильную страницу активного actor и ближайший контекст; пятая содержит служебный список, архивы и настройки.

## D-027 — Туры и кэмпы находятся в Событиях

Статус: принято.

Игры, тренировки, турниры, сезоны, поездки, туры и training camps ищутся в `Событиях`. Глобальный раздел `Клубы` содержит только клубы, площадки и корты. Тренер может быть открыт из клуба, но общий поиск тренеров запускается игроком из блока `Мои тренеры` на первой вкладке.

## D-028 — Связь игрока и тренера подтверждается тренером

Статус: принято.

Игрок может отправить запрос нескольким trainer actors. До подтверждения показывается `Запрос отправлен`; после подтверждения — `Тренируется у {{trainer_name}}`. Тренер получает уведомление, может открыть игрока, написать, подтвердить или отклонить. Подтверждение добавляет игрока в рабочий список `Мои игроки` trainer actor. Источник истины: `docs/TRAINER_RELATIONSHIPS.yaml`.
""",
)

# Replace the exact old navigation contract wherever it remains, excluding generated audit files.
for path in list(ROOT.glob("*.md")) + list(DOCS.rglob("*.md")) + list(DOCS.rglob("*.yaml")) + list(DOCS.rglob("*.mmd")):
    if path.name.startswith("SCREEN_READINESS"):
        continue
    replace_text(path, [
        (OLD_NAV, NEW_NAV),
        ("Главная, События, Чаты, Клубы и Профиль", "Профиль, События, Чаты, Клубы и Настройки"),
        ("Главная, События, Чаты, Клубы и Профиль", "Профиль, События, Чаты, Клубы и Настройки"),
    ])

# Profile-stack wording now points to the Settings tab.
for path in (DOCS / "screens/profile").glob("*.md"):
    replace_text(path, [
        ("Профиль →", "Настройки →"),
        ("внутри `Профиля`", "внутри `Настроек`"),
        ("активна вкладка `Профиль`", "активна вкладка `Настройки`"),
        ("активной вкладкой `Профиль`", "активной вкладкой `Настройки`"),
        ("возврат в `Профиль`", "возврат в `Настройки`"),
    ])

# UI search rules and design-system visible labels.
replace_text(DOCS / "UI_RULES.md", [
    ("- В Клубах: клубы, площадки, тренеры и туры.", "- В Клубах: клубы, площадки и корты."),
    ("- В Событиях: игры, тренировки, турниры и сезоны.", "- В Событиях: игры, тренировки, турниры, сезоны, туры и кэмпы."),
])
replace_text(DOCS / "DESIGN_SYSTEM.md", [(OLD_NAV, NEW_NAV)])

# Validator expected visible titles.
replace_text(ROOT / "scripts/validate_design_system.py", [
    ('{"id": "home", "title": "Главная", "route": "/"}', '{"id": "home", "title": "Профиль", "route": "/"}'),
    ('{"id": "profile", "title": "Профиль", "route": "/profile"}', '{"id": "profile", "title": "Настройки", "route": "/profile"}'),
])

# Add a legacy-label guard to the navigation validator once.
validator_path = ROOT / "scripts/validate_navigation.py"
validator = validator_path.read_text(encoding="utf-8")
marker = "Legacy bottom navigation title contract returned"
if marker not in validator:
    needle = "    # One screen ↔ one route and valid navigation fallbacks.\n"
    insertion = f'''    legacy_phrase = "{OLD_NAV}"\n    for source in (DOCS / "NAVIGATION_RESOLVERS.yaml", DOCS / "DESIGN_TOKENS.yaml", DOCS / "UI_RULES.md"):\n        if legacy_phrase in source.read_text(encoding="utf-8"):\n            errors.append("{marker}: " + str(source.relative_to(ROOT)))\n\n'''
    validator = validator.replace(needle, insertion + needle)
    validator_path.write_text(validator, encoding="utf-8")

print("Profile tab, Settings tab, contextual search and trainer relationships migrated.")
