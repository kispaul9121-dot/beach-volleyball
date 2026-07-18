#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def write(path: str, content: str) -> None:
    target = ROOT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content.rstrip() + "\n", encoding="utf-8")


def replace(path: str, old: str, new: str, required: bool = True) -> None:
    content = read(path)
    if old not in content:
        if required:
            raise RuntimeError(f"Expected text not found in {path}: {old[:120]!r}")
        return
    write(path, content.replace(old, new))


def append_once(path: str, marker: str, block: str) -> None:
    content = read(path)
    if marker in content:
        return
    write(path, content.rstrip() + "\n\n" + block.rstrip())


write(
    "docs/TRAINER_RELATIONSHIPS.yaml",
    """version: 2
concept: player_trainer_relationship
source_of_truth: docs/TRAINER_RELATIONSHIPS.yaml

principles:
  - player may have zero, one or multiple active trainers
  - relationship is distinct from My Players and event participation
  - player adds a public trainer directly from the Profile tab or trainer public profile
  - trainer confirmation is not required
  - label Тренируется у appears immediately after successful creation
  - trainer receives a New player notification and may send a direct message
  - either side may end the relationship without deleting historical events, chats, payments or attendance
  - blocked users cannot create or message through a relationship
  - relationship never exposes private statistics, payments or unrelated private events

statuses:
  active:
    player_label: Тренируется у
    trainer_label: Мой игрок
    actions: [open_profile, message, remove]
  ended_by_player:
    active: false
  ended_by_trainer:
    active: false
  blocked:
    active: false

player_profile_block:
  empty_title: Без тренера
  empty_action: Найти тренера
  active_item: Тренируется у {trainer_name}
  multiple_relationships: true
  initial_visible_items: 2
  show_all_when_more: true

trainer_notification:
  type: trainer_new_player
  category: players_and_trainers
  title: Новый игрок
  body: "{player_name} добавил(а) вас как тренера"
  actions: [open_player_profile, message]
  deduplicate_by: relationship_id

search:
  route: /trainers/search
  fields: [name, city, distance, specialization, player_level, language, session_format, availability]
  card: [photo, name, verification, city, specializations, player_levels, nearest_public_training]
  primary_action: add_trainer
  ratings_forbidden: true
  blocked_or_hidden_profiles_excluded: true
  pagination: cursor
  recent_queries: local_private
  typo_tolerance: implementation_required

creation:
  actor: player
  confirmation_required_from_trainer: false
  requires_accepting_new_players: true
  idempotent: true
  effects:
    - mark relationship active
    - show trainer immediately on player Profile tab
    - create one New player notification for trainer actor
    - ensure player is visible in trainer My Players working list with source player_selected_trainer
    - allow one direct conversation context while privacy and blocking permit
  forbidden_effects:
    - create event participation
    - enroll in training
    - expose private statistics
    - expose payments
    - expose private events

ending:
  allowed_by: [player, trainer]
  effects:
    - revoke relationship-only permission for new direct messages
    - preserve shared event history
    - preserve allowed chat history according to retention policy
    - keep event participation unchanged

trainer_player_directory:
  source: player_selected_trainer
  appears_in: profile.players
  trainer_can: [open_public_profile, message_player, remove_relationship, invite_to_specific_event]
  trainer_cannot: [see_private_statistics, see_unrelated_private_events, mark_payment_as_completed]

privacy_and_safety:
  - trainer may disable accepting new players in settings
  - mass automatic trainer addition is forbidden
  - create and end operations produce audit events
  - report or block immediately disables addition and relationship messaging
""",
)

write(
    "docs/screens/home/main.md",
    """# Профиль

- Screen ID: `home.main`
- Route: `/`
- User-facing bottom-tab title: `Профиль`
- Internal tab ID remains `home`
- Variants: `player`, `trainer`, `organization`
- UI contract: `docs/DESIGN_SYSTEM.md` and `docs/DESIGN_TOKENS.yaml`
- Trainer relationships: `docs/TRAINER_RELATIONSHIPS.yaml`

Первая вкладка является живой профильной страницей активного actor. Она соединяет публичную идентичность, ближайшие события и действительно важные действия, но не заменяет каталог `События` и служебный список `Настройки`.

## Общая верхняя часть

- фото или логотип active actor;
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

- нет активных связей → карточка `Без тренера` и действие `Найти тренера`;
- одна активная связь → `Тренируется у {trainer_name}`;
- несколько связей → несколько карточек под заголовком `Тренируется у`;
- на первом экране показываются максимум две карточки и действие `Показать всех`;
- каждая карточка открывает публичный профиль тренера;
- игрок может удалить одну связь через контекстное меню, не затрагивая остальные.

После успешного нажатия `Добавить тренера` связь сразу становится активной. Отдельного подтверждения тренера нет. Добавление не записывает игрока на тренировку и не раскрывает закрытые данные.

## Тренер

Порядок блоков:

1. шапка и предпросмотр публичного профиля;
2. новые игроки, добавившие тренера;
3. тренировки сегодня;
4. посещаемость, которую нужно заполнить;
5. заявки и неоплаченные места;
6. ближайшие занятия;
7. блок `Управляю` с играми, турнирами, сезонами, турами и кэмпами;
8. личные участия тренера как игрока.

Новый игрок приходит уведомлением `Новый игрок`, появляется в рабочем списке `Мои игроки`, и тренер может открыть профиль или написать. Тренер может завершить связь, но не получает доступ к закрытой статистике, платежам и непубличным событиям игрока.

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

```text
Профиль · События · Чаты · Клубы · Настройки
```

На этом экране активна вкладка `Профиль`.

## Состояния

- loading;
- профиль заполнен не полностью;
- `Без тренера`;
- связь с тренером создана;
- тренер больше не принимает новых игроков;
- нет ближайших действий;
- partial error отдельного блока;
- offline с последними сохранёнными данными;
- permission changed.
""",
)

write(
    "docs/screens/shared/trainer-search.md",
    """# Найти тренера

- Screen ID: `trainer.search`
- Route: `/trainers/search`
- Parent: первая вкладка `Профиль`
- Variants: `player`
- Source of truth: `docs/TRAINER_RELATIONSHIPS.yaml`

## Назначение

Помочь игроку найти одного или нескольких тренеров, открыть публичный профиль и сразу добавить выбранного тренера. Экран не является частью `Клубов` и не ищет события, туры или кэмпы.

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
- принимает новых игроков;
- подтверждённый профиль.

## Карточка тренера

- фото;
- имя;
- статус проверки;
- город;
- специализации;
- уровни игроков;
- ближайшая публичная тренировка, когда есть;
- одно основное действие `Добавить тренера`, статус `Тренируется у` либо `Не принимает новых игроков`.

Числовой рейтинг и звёзды не используются. Вся карточка открывает публичный профиль.

## Поисковая выдача

- серверная пагинация использует cursor;
- новый запрос отменяет устаревший незавершённый запрос;
- поддерживаются варианты написания имени и опечатки;
- порядок результатов не меняется скачком после добавления;
- недавние запросы хранятся локально и могут быть очищены;
- скрытые, заблокированные и недоступные профили не возвращаются.

## Создание связи

1. Игрок нажимает `Добавить тренера`.
2. Сервер идемпотентно создаёт активную связь.
3. Игрок сразу возвращается в `Профиль` и видит `Тренируется у {имя}`.
4. Тренер получает одно уведомление `Новый игрок`.
5. Игрок появляется у тренера в `Моих игроках` с source `player_selected_trainer`.
6. Тренер может открыть игрока или написать ему.

Игрок может иметь несколько активных тренеров. Добавление не создаёт участие в тренировке, оплату или доступ к закрытым данным.

## Состояния

- loading;
- нет результатов;
- геолокация отключена;
- offline read-only;
- связь уже активна;
- тренер не принимает новых игроков;
- профиль скрыт или заблокирован;
- rate limit;
- конфликт создания связи.
""",
)

write(
    "docs/screens/shared/notifications.md",
    """# Уведомления

- Screen ID: `global.notifications`
- Route: `/notifications`

## Категории

- Требуют действий;
- События;
- Игроки и тренеры;
- Сообщения;
- Платежи;
- Системные.

## Карточка

- тип и иконка;
- actor-профиль;
- связанный игрок, тренер или событие;
- время;
- прочитано / непрочитано;
- одно главное действие.

## Новый игрок

Сразу после создания активной связи trainer actor получает:

```text
Новый игрок
Анна добавила вас как тренера.
[Написать игроку]
```

Карточка открывает публичный профиль игрока либо личный чат. Действия подтверждения и отклонения отсутствуют, потому что связь уже активна. Тренер может завершить связь отдельно.

Уведомление не означает запись на тренировку и не раскрывает закрытые данные игрока. Повторный идемпотентный запрос не создаёт второе уведомление.

## Другие действия

- оплатить;
- подтвердить перенос;
- принять приглашение;
- проверить заявку;
- опубликовать раунд;
- внести результат;
- открыть чат;
- завершить профиль.

## Правила

- уведомление хранит `action_id` и target context;
- фильтруется по actor;
- критичное действие не исчезает до выполнения или потери актуальности;
- удалённая связь или сущность открывает понятное состояние.

## Состояния

- нет уведомлений;
- только прочитанные;
- связь уже завершена;
- действие выполнено на другом устройстве;
- потеря прав;
- offline.
""",
)

# Actions: direct creation, no request acceptance flow.
replace(
    "docs/ACTIONS.yaml",
    """- id: profile.cancel_trainer_request
  label: Отменить запрос тренеру
  source: home.main
  destination: system.cancel_trainer_relationship_confirmation
  permission: relationship_request_owner
""",
    "",
)
replace(
    "docs/ACTIONS.yaml",
    """- id: trainer.request_from_search
  label: Добавить тренера
  source: trainer.search
  destination: system.create_trainer_relationship_request
  permission: authenticated_player
""",
    """- id: trainer.add_from_search
  label: Добавить тренера
  source: trainer.search
  destination: system.create_active_trainer_relationship
  success: home.main
  permission: authenticated_player
""",
)
replace(
    "docs/ACTIONS.yaml",
    """- id: trainer.request_from_profile
  label: Добавить тренера
  source: trainer.public_profile
  destination: system.create_trainer_relationship_request
  permission: authenticated_player
""",
    """- id: trainer.add_from_profile
  label: Добавить тренера
  source: trainer.public_profile
  destination: system.create_active_trainer_relationship
  success: home.main
  permission: authenticated_player
""",
)
replace(
    "docs/ACTIONS.yaml",
    """- id: trainer.accept_player_relationship
  label: Подтвердить игрока
  source: global.notifications
  destination: system.accept_trainer_relationship
  permission: relationship_target_trainer
- id: trainer.decline_player_relationship
  label: Отклонить запрос
  source: global.notifications
  destination: system.decline_trainer_relationship_confirmation
  permission: relationship_target_trainer
""",
    "",
)
replace(
    "docs/ACTIONS.yaml",
    """- id: trainer.message_requesting_player
  label: Написать игроку
  source: global.notifications
  destination: system.open_or_create_direct_chat
  permission: trainer_relationship_request_recipient
""",
    """- id: trainer.message_new_player
  label: Написать игроку
  source: global.notifications
  destination: system.open_or_create_direct_chat
  permission: linked_trainer
""",
)

# Screen and route metadata.
replace(
    "docs/SCREENS.yaml",
    "purpose: Поиск тренеров и создание подтверждаемой связи игрока с одним или несколькими тренерами.",
    "purpose: Поиск тренеров и прямое добавление одного или нескольких тренеров игроку.",
)
replace("docs/SCREENS.yaml", "back_fallback: /clubs?category=trainers", "back_fallback: /")
replace("docs/ROUTES.yaml", "back_fallback: /clubs?category=trainers", "back_fallback: /")
replace("docs/ROUTES.yaml", "back_fallback: /clubs?category=tours", "back_fallback: /play?category=tours")

# Public trainer profile.
replace("docs/screens/clubs/trainer-details.md", "- Section: `Клубы → Тренеры`", "- Entry points: player trainer search, events, club staff lists and direct links")
replace(
    "docs/screens/clubs/trainer-details.md",
    "- Data sources: trainer actor profile, verification status, public trainings, tours, linked clubs, textual reviews and privacy settings",
    "- Data sources: trainer actor profile, verification status, public trainings, tours, linked clubs, textual reviews, privacy settings and trainer relationships",
)
replace(
    "docs/screens/clubs/trainer-details.md",
    """1. `Ближайшая тренировка` — когда есть доступное публичное занятие;
2. `Посмотреть расписание` — когда расписание есть, но ближайшая карточка не выбрана;
3. `Написать` — только когда тренер разрешил личные сообщения;
4. информационное состояние `Сейчас не принимает новых игроков` — без ложной кнопки записи.

Запись всегда происходит через канонический экран конкретной тренировки, а не напрямую из профиля тренера.
""",
    """1. `Добавить тренера` — для игрока, когда связь отсутствует и тренер принимает новых игроков;
2. `Тренируется у этого тренера` — когда активная связь уже существует;
3. `Ближайшая тренировка` — когда приоритетом является публичное занятие;
4. `Посмотреть расписание` — когда есть публичное расписание;
5. `Написать` — когда сообщения разрешены активной связью или другим контекстом;
6. `Сейчас не принимает новых игроков` — информационное состояние без ложной кнопки.

Добавление тренера создаёт активную связь сразу, но не записывает игрока на тренировку. Запись всегда происходит через канонический экран конкретной тренировки.
""",
)
replace(
    "docs/screens/clubs/trainer-details.md",
    "- `trainer.owner_edit_profile` — владельцу открыть настройки публичного профиля.",
    "- `trainer.owner_edit_profile` — владельцу открыть настройки публичного профиля;\n- `trainer.add_from_profile` — игроку сразу добавить тренера и вернуться в первую вкладку `Профиль`.",
)
replace(
    "docs/screens/clubs/trainer-details.md",
    "Может открыть тренировку, записаться или подать заявку уже на её details screen, написать тренеру при разрешённой приватности и перейти к связанным сущностям.",
    "Может сразу добавить тренера, открыть тренировку, записаться или подать заявку на её details screen, написать при разрешённой активной связи или другом контексте и перейти к связанным сущностям. Игрок может иметь несколько тренеров.",
)
replace("docs/screens/clubs/trainer-details.md", "- каталог `Клубы → Тренеры` → `trainer.public_profile`;", "- поиск `/trainers/search` → `trainer.public_profile`;")
replace("docs/screens/clubs/trainer-details.md", "- back fallback: `/clubs?category=trainers`.", "- back fallback: `/`.")
replace("docs/screens/clubs/trainer-details.md", "и Профиле, а не добавляются", "и первой вкладке `Профиль`, а не добавляются")

# Settings page wording.
replace(
    "docs/screens/profile/main.md",
    "Новые запросы игроков показываются на первой вкладке и в уведомлениях.",
    "Новые игроки, добавившие тренера, показываются на первой вкладке и в уведомлениях.",
)

# Player directory integration.
replace(
    "docs/PLAYER_DIRECTORY.yaml",
    """trainer_relationship_integration:
  source_of_truth: docs/TRAINER_RELATIONSHIPS.yaml
  rules:
    - confirmed trainer relationship is separate from actor_player_links
    - after trainer accepts, player is ensured in trainer actor My Players working list
    - ending trainer relationship does not silently delete trainer saved-player entry; trainer may remove it separately
    - unconfirmed request does not create event participation or access to event chats
""",
    """trainer_relationship_integration:
  source_of_truth: docs/TRAINER_RELATIONSHIPS.yaml
  rules:
    - active trainer relationship is separate from ordinary actor_player_links
    - immediately after player adds trainer, player is visible in trainer actor My Players with source player_selected_trainer
    - ending the relationship removes the relationship-derived row unless trainer separately saved the player
    - trainer relationship does not create event participation or access to event chats
    - relationship allows direct messaging only while privacy and blocking permit
""",
)

# Data model.
replace(
    "docs/DATA_MODEL.md",
    "- `active_actor_preferences` — последний активный профиль.\n",
    """- `active_actor_preferences` — последний активный профиль;
- `player_trainer_relationships` — активные и завершённые связи player profile с trainer actor;
- `player_trainer_relationship_events` — аудит создания, завершения и блокировки связи.

`player_trainer_relationships` хранит `player_profile_id`, `trainer_actor_id`, status, source, created_at, ended_at и audit actors. Активная пара уникальна, но игрок может иметь несколько тренеров, а тренер — несколько игроков. Создание сразу устанавливает `active`; отдельного requested/approval состояния нет.
""",
)

# Decision replaces confirmation model.
replace(
    "docs/DECISIONS.md",
    """## D-028 — Связь игрока и тренера подтверждается тренером

Статус: принято.

Игрок может отправить запрос нескольким trainer actors. До подтверждения показывается `Запрос отправлен`; после подтверждения — `Тренируется у {trainer_name}`. Тренер получает уведомление, может открыть игрока, написать, подтвердить или отклонить. Подтверждение добавляет игрока в рабочий список `Мои игроки` trainer actor. Источник истины: `docs/TRAINER_RELATIONSHIPS.yaml`.
""",
    """## D-028 — Игрок напрямую добавляет несколько тренеров

Статус: пересмотрено и принято.

Игрок может напрямую добавить одного или нескольких trainer actors, которые принимают новых игроков. Отдельное подтверждение тренера не требуется: после успешного добавления сразу показывается `Тренируется у {trainer_name}`.

Тренер получает уведомление `Новый игрок`, может открыть профиль или написать, а игрок появляется в рабочем списке `Мои игроки` с source `player_selected_trainer`. Любая сторона может завершить связь. Связь не создаёт participation и не раскрывает закрытые данные. Источник истины: `docs/TRAINER_RELATIONSHIPS.yaml`.
""",
)

# Search architecture wording.
replace(
    "docs/SEARCH_ARCHITECTURE.yaml",
    "  - trainer search is available to player profile from the first Profile tab",
    "  - trainer search is available to player profile from the first Profile tab and creates an active relationship without trainer approval",
)

# Add canonical flow/test once.
append_once(
    "docs/USER_FLOWS.md",
    "## 21. Игрок добавляет несколько тренеров",
    """## 21. Игрок добавляет несколько тренеров

```text
Профиль → Без тренера → Найти тренера
→ поиск и фильтры
→ Добавить тренера
→ активная связь создаётся сразу
→ Профиль показывает «Тренируется у»
→ тренер получает «Новый игрок»
→ игрок появляется в Моих игроках тренера
→ тренер может написать
→ игрок может добавить второго тренера независимо
```
""",
)
append_once(
    "docs/TEST_SCENARIOS.md",
    "## A-14 — Прямое добавление нескольких тренеров",
    """## A-14 — Прямое добавление нескольких тренеров

1. Игрок без trainer relationship видит `Без тренера` на `/`.
2. `Найти тренера` открывает `/trainers/search`.
3. Выдача скрывает заблокированные профили и показывает `Не принимает новых игроков` без CTA.
4. Игрок нажимает `Добавить тренера`; сервер создаёт active relationship без approval.
5. Игрок сразу возвращается на `/` и видит `Тренируется у`.
6. Trainer actor получает ровно одно уведомление `Новый игрок` с действием `Написать игроку`.
7. Игрок появляется в `Моих игроках` тренера с source `player_selected_trainer`.
8. Тренер не получает закрытую статистику, платежи и непубличные события.
9. Игрок добавляет второго тренера; обе связи независимы.
10. Удаление одной связи не затрагивает вторую и не меняет participation.
11. Нижнее меню остаётся `Профиль · События · Чаты · Клубы · Настройки`.
""",
)

print("Direct trainer relationship reconciliation completed.")
