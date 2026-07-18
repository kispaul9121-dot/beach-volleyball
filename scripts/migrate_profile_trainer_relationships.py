#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def write(path: str, content: str) -> None:
    target = ROOT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content.rstrip() + "\n", encoding="utf-8")


def replace_required(path: str, old: str, new: str) -> None:
    content = read(path)
    if old not in content:
        raise RuntimeError(f"Expected text not found in {path}: {old[:100]!r}")
    write(path, content.replace(old, new))


def append_once(path: str, marker: str, block: str) -> None:
    content = read(path)
    if marker in content:
        return
    write(path, content.rstrip() + "\n\n" + block.rstrip() + "\n")


# Global user-facing tab labels. Internal ids and routes remain stable.
for target in [ROOT / "AGENTS.md", ROOT / "README.md", *DOCS.rglob("*.md"), *DOCS.rglob("*.yaml")]:
    if not target.exists():
        continue
    text = target.read_text(encoding="utf-8")
    updated = (
        text.replace("Главная · События · Чаты · Клубы · Профиль", "Профиль · События · Чаты · Клубы · Настройки")
        .replace("Главная, События, Чаты, Клубы и Профиль", "Профиль, События, Чаты, Клубы и Настройки")
        .replace("Главная / События / Чаты / Клубы / Профиль", "Профиль / События / Чаты / Клубы / Настройки")
        .replace("Профиль → Мои игроки", "Настройки → Мои игроки")
        .replace("активна вкладка `Профиль`", "активна вкладка `Настройки`")
    )
    if updated != text:
        target.write_text(updated, encoding="utf-8")

# Screen registry.
replace_required(
    "docs/SCREENS.yaml",
    """  - id: global.notifications
    title: Уведомления
    route: /notifications
    section: global
    spec: docs/screens/shared/notifications.md
    purpose: Все системные и событийные уведомления.
    back_fallback: /

  # Bottom tabs
""",
    """  - id: global.notifications
    title: Уведомления
    route: /notifications
    section: global
    spec: docs/screens/shared/notifications.md
    purpose: Все системные, событийные и связанные с тренерами уведомления.
    back_fallback: /

  - id: trainer.search
    title: Найти тренера
    route: /search/trainers
    section: global
    spec: docs/screens/search/trainers.md
    purpose: Поиск и добавление одного или нескольких тренеров в профиль игрока.
    variants: [player]
    permission: authenticated_player
    back_fallback: /

  # Bottom tabs
""",
)
replace_required(
    "docs/SCREENS.yaml",
    """  - id: home.main
    title: Главная
    route: /
    section: home
    spec: docs/screens/home/main.md
    purpose: Адаптивная сводка игрока, тренера или организации.
""",
    """  - id: home.main
    title: Профиль
    route: /
    section: home
    spec: docs/screens/home/main.md
    purpose: Персональная страница активного профиля с тренерами, ближайшими действиями и управляемыми событиями.
""",
)
replace_required(
    "docs/SCREENS.yaml",
    "purpose: Клубы, корты, тренеры и публичные туры.",
    "purpose: Публичный каталог клубов, площадок и кортов.",
)
replace_required(
    "docs/SCREENS.yaml",
    "back_fallback: /clubs?category=trainers",
    "back_fallback: /",
)
replace_required(
    "docs/SCREENS.yaml",
    """  - id: profile.main
    title: Профиль
    route: /profile
    section: profile
    spec: docs/screens/profile/main.md
    purpose: Адаптивный кабинет активного профиля.
""",
    """  - id: profile.main
    title: Настройки
    route: /profile
    section: profile
    spec: docs/screens/profile/main.md
    purpose: Настройки аккаунта и активного профиля, архивы, календарь, платежи и служебные разделы.
""",
)

# Route registry.
replace_required(
    "docs/ROUTES.yaml",
    """  - path: system://player-picker
    screen: player.picker
    navigator: modal_stack
    access: authenticated
    permission: entity_inviter
    accepts_query: [entityType, entityId, draftId, actorId, returnTo]
    back_fallback: system://dismiss

  # Bottom tabs
""",
    """  - path: system://player-picker
    screen: player.picker
    navigator: modal_stack
    access: authenticated
    permission: entity_inviter
    accepts_query: [entityType, entityId, draftId, actorId, returnTo]
    back_fallback: system://dismiss

  - path: /search/trainers
    screen: trainer.search
    navigator: global_stack
    access: authenticated_onboarded
    permission: authenticated_player
    accepts_query: [query, city, specialization, level, format, returnTo]
    back_fallback: /

  # Bottom tabs
""",
)

# Immutable navigation labels and token validation.
replace_required(
    "docs/NAVIGATION_RESOLVERS.yaml",
    """    - id: home
      title: Главная
      screen: home.main
      route: /
""",
    """    - id: home
      title: Профиль
      screen: home.main
      route: /
""",
)
replace_required(
    "docs/NAVIGATION_RESOLVERS.yaml",
    """    - id: profile
      title: Профиль
      screen: profile.main
      route: /profile
""",
    """    - id: profile
      title: Настройки
      screen: profile.main
      route: /profile
""",
)
replace_required(
    "scripts/validate_design_system.py",
    '{"id": "home", "title": "Главная", "route": "/"}',
    '{"id": "home", "title": "Профиль", "route": "/"}',
)
replace_required(
    "scripts/validate_design_system.py",
    '{"id": "profile", "title": "Профиль", "route": "/profile"}',
    '{"id": "profile", "title": "Настройки", "route": "/profile"}',
)
replace_required(
    "docs/DESIGN_TOKENS.yaml",
    """      - id: home
        title: Главная
        route: /
""",
    """      - id: home
        title: Профиль
        route: /
""",
)
replace_required(
    "docs/DESIGN_TOKENS.yaml",
    """      - id: profile
        title: Профиль
        route: /profile
""",
    """      - id: profile
        title: Настройки
        route: /profile
""",
)

# New actions are appended to keep the registry diff compact.
actions_block = """  # Player ↔ trainer relationships
  - id: home.open_trainer_search
    label: Найти тренера
    source: home.main
    destination: trainer.search
    context: {returnTo: /}
    permission: authenticated_player

  - id: home.open_linked_trainer
    label: Открыть тренера
    source: home.main
    destination: trainer.public_profile
    permission: authenticated_player

  - id: home.remove_linked_trainer
    label: Удалить тренера
    source: home.main
    destination: system.remove_trainer_relationship_confirmation
    permission: relationship_owner

  - id: trainer_search.update_query
    label: Поиск тренера
    source: trainer.search
    destination: system.local_search
    permission: authenticated_player

  - id: trainer_search.open_filters
    label: Фильтры тренеров
    source: trainer.search
    destination: system.search_filters
    permission: authenticated_player

  - id: trainer_search.open_profile
    label: Открыть профиль тренера
    source: trainer.search
    destination: trainer.public_profile
    permission: authenticated_player

  - id: trainer_search.add_trainer
    label: Добавить тренера
    source: trainer.search
    destination: system.create_player_trainer_relationship
    success: home.main
    permission: authenticated_player

  - id: trainer.add_relationship
    label: Добавить тренера
    source: trainer.public_profile
    destination: system.create_player_trainer_relationship
    success: home.main
    permission: authenticated_player

  - id: trainer.message_new_player
    label: Написать игроку
    source: global.notifications
    destination: system.open_or_create_direct_chat
    permission: linked_trainer
"""
append_once("docs/ACTIONS.yaml", "id: home.open_trainer_search", actions_block)

# Canonical screen specs.
write(
    "docs/screens/home/main.md",
    """# Профиль

- Screen ID: `home.main`
- Route: `/`
- Visible bottom-tab label: `Профиль`
- Internal screen ID remains `home.main` for backward compatibility.
- Variants: `player`, `trainer`, `organization`
- UI contract: `docs/DESIGN_SYSTEM.md` and `docs/DESIGN_TOKENS.yaml`
- Trainer relationships: `docs/TRAINER_RELATIONSHIPS.yaml`

`Профиль` — персональная живая страница активного actor-профиля. Она показывает человека или организацию, ближайшие действия и актуальные связи, но не заменяет публичный каталог событий.

## Общая верхняя панель

- аватар и название активного профиля → `actor.switcher`;
- статус заполнения или проверки профиля;
- текущий город;
- уведомления;
- глобальное создание, когда active actor может создавать сущности;
- корневой экран не показывает кнопку назад.

## Игрок

Порядок блоков:

1. компактная шапка игрока: фото, имя, город, публичный уровень и редактирование;
2. блок `Мои тренеры`;
3. ближайшее участие;
4. действия: оплатить, подтвердить, внести результат;
5. сегодня в календаре;
6. приглашения;
7. созданные игроком события, если они есть;
8. рекомендации.

### Мои тренеры — пустое состояние

Когда активных связей нет, показывается одна карточка:

```text
Без тренера
Найдите тренера по городу, специализации и формату занятий.
[Найти тренера]
```

Действие `home.open_trainer_search` открывает `/search/trainers` и сохраняет `returnTo=/`.

### Мои тренеры — активные связи

Когда добавлен хотя бы один тренер, заголовок меняется на `Тренируется у`. Игрок может иметь несколько тренеров одновременно.

Карточка тренера показывает:

- фото;
- имя;
- статус проверки;
- короткую специализацию;
- город;
- ближайшую публичную тренировку, когда есть;
- действия `Открыть` и контекстное `Удалить тренера`.

При нескольких тренерах показываются максимум две карточки на первом экране и действие `Показать всех`; порядок стабилен и не меняется случайно.

Добавление тренера не записывает игрока на тренировку и не раскрывает тренеру закрытую статистику, платежи или события игрока.

## Тренер

Порядок блоков:

1. публичная шапка и действие `Предпросмотр профиля`;
2. тренировки сегодня;
3. новые игроки, добавившие тренера;
4. посещаемость, которую нужно заполнить;
5. заявки и неоплаченные места;
6. ближайшие занятия;
7. блок `Управляю` с играми, турнирами, сезонами, турами и кэмпами;
8. личные участия тренера как игрока.

Новый игрок появляется в `Моих игроках` с источником `player_selected_trainer`. Тренер получает уведомление и может написать игроку, пока связь активна и никто не заблокирован.

Отдельных тренировочных групп в MVP нет. Повторные занятия создаются через шаблон или дублирование тренировки.

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

## Карточка управляемой сущности

Показывает actor-создателя, роль пользователя, ближайшее действие, участников X из Y, задолженности или незакрытые результаты и одну кнопку `Управлять`.

## Нижняя навигация

```text
Профиль · События · Чаты · Клубы · Настройки
```

На этом экране активна вкладка `Профиль`. Переключение actor не меняет набор, порядок, названия и маршруты меню.

## Состояния

- loading;
- empty: нет ближайших действий;
- player without trainer;
- trainer relationship created;
- trainer unavailable or stopped accepting players;
- partial error отдельного блока;
- offline с последними сохранёнными данными;
- actor without completed profile.

Любая карточка ведёт на канонический экран или кабинет управления, а не на копию сущности.
""",
)

write(
    "docs/screens/profile/main.md",
    """# Настройки

- Screen ID: `profile.main`
- Route: `/profile`
- Visible bottom-tab label: `Настройки`
- Internal route and technical `profile.*` namespace remain unchanged for backward compatibility.
- Variants: `player`, `trainer`, `organization`

`Настройки` — служебный раздел аккаунта и активного actor-профиля. Он содержит списки, архивы, параметры, финансы и управление профилями; живая персональная страница находится в первой вкладке `Профиль`.

## Верхняя часть

- активный actor и переключатель;
- тип профиля и статус проверки;
- действие `Редактировать профиль`;
- карточка незавершённой настройки, когда требуется действие.

## Мои разделы

Общий список доступных пунктов:

- Мои профили;
- Мой календарь;
- Мои игры;
- Мои тренировки;
- Мои турниры и сезоны;
- Мои туры, поездки и кэмпы;
- Мои игроки;
- Статистика;
- Платежи и выплаты;
- Уведомления;
- Приватность и безопасность;
- Настройки приложения;
- Помощь;
- Опасные действия.

Пункты фильтруются по actor и permission, но не переставляются случайно между открытиями.

## Игрок

Дополнительно доступны спортивные настройки, приватность публичного профиля и управление связями с тренерами. Список тренеров показывается на первой вкладке `Профиль`; здесь находятся только параметры связи и история удалённых связей, если это понадобится для поддержки.

## Тренер

Дополнительно доступны:

- данные публичного профиля;
- специализации и форматы занятий;
- принимает ли тренер новых игроков;
- приватность личных сообщений;
- Мои игроки;
- платежи и выплаты;
- документы проверки.

## Организация

Дополнительно доступны сотрудники, площадки, финансы, публичная страница и переход в административные настройки клуба. Полный оперативный кабинет не дублируется внутри списка.

## Правила

- `/profile` сохраняется как технический маршрут пятой вкладки;
- вложенные пути `/profile/*` сохраняются;
- первая вкладка `Профиль` открывается по `/`;
- переключение actor обновляет доступные пункты;
- настройки не заменяют ежедневное управление в `События → Управляю`;
- глобальное нижнее меню всегда `Профиль · События · Чаты · Клубы · Настройки`.

## Состояния

- actor draft;
- verification pending;
- rejected with correction steps;
- no activity;
- permission changed;
- offline;
- settings load error.
""",
)

write(
    "docs/screens/search/trainers.md",
    """# Найти тренера

- Screen ID: `trainer.search`
- Route: `/search/trainers`
- Navigator: global stack
- Permission: authenticated player
- Source of truth: `docs/TRAINER_RELATIONSHIPS.yaml`
- Back fallback: `/`

## Назначение

Найти публичного тренера, открыть его профиль и добавить в список тренеров игрока. Экран открывается из карточки `Без тренера` или действия добавления ещё одного тренера в первой вкладке `Профиль`.

## Верхняя панель

- назад в `returnTo` или `/`;
- заголовок `Найти тренера`;
- строка поиска;
- фильтры;
- текущий город или выбранная область.

## Быстрые фильтры

В одной горизонтально прокручиваемой строке:

```text
Рядом · Новички · Техника · Индивидуально · Группы
```

Одновременно показывается не более трёх приоритетных фильтров; остальные параметры открываются в bottom sheet.

Расширенные фильтры:

- город и расстояние;
- специализация;
- уровень игроков;
- индивидуальный, парный или групповой формат;
- язык;
- принимает новых игроков;
- есть ближайшие публичные тренировки;
- связанные клубы и площадки.

## Результат

Карточка показывает фото, имя, статус проверки, город, специализации, форматы занятий и ближайшую публичную тренировку. Рейтинг и звёзды не используются.

Главное действие:

- `Добавить тренера` — тренер доступен и ещё не добавлен;
- `Добавлен` — активная связь уже существует;
- `Не принимает новых игроков` — информационное состояние без ложной кнопки.

Вся карточка открывает `/trainers/:trainerId`.

## Добавление

`trainer_search.add_trainer` создаёт активную связь без отдельного подтверждения тренера, если trainer profile принимает новых игроков.

После успеха:

1. игрок возвращается в `/`;
2. блок становится `Тренируется у`;
3. тренер получает уведомление `Новый игрок`;
4. игрок появляется у тренера в `Моих игроках` с источником связи;
5. тренеру становится доступно действие `Написать игроку`.

Добавление не создаёт участие в тренировке, не подписывает на события и не даёт доступ к закрытым данным.

## Состояния

- loading skeleton;
- нет результатов;
- геолокация недоступна;
- trainer profile hidden;
- trainer not accepting players;
- already linked;
- blocked;
- rate limited;
- offline read-only;
- relationship creation conflict.
""",
)

write(
    "docs/screens/clubs/main.md",
    """# Клубы

- Screen ID: `clubs.main`
- Route: `/clubs`
- Variants: `player`, `trainer`, `organization`

## Назначение

Публичный каталог клубов, площадок и кортов. Поиск тренеров выполняется из первой вкладки игрока `Профиль`, а туры, поездки и кэмпы находятся в `Событиях`.

## Категории

```text
Клубы · Площадки и корты
```

Поиск, быстрые фильтры, расширенные фильтры и карта относятся только к выбранной категории.

## Игрок

Приоритеты: ближайшие площадки, клубы с публичным расписанием и доступные корты.

## Тренер

Дополнительно сверху показываются клубы, где тренер работает, и доступные площадки. Поиск других тренеров здесь не создаётся.

## Организация

Дополнительно сверху:

- `Моя организация`;
- собственные площадки;
- кнопка управления клубом.

Публичный каталог остаётся ниже.

## Карточки

### Клуб

Название, город, площадки, ближайшие публичные события и действие `Открыть клуб`.

### Площадка

Адрес, корты, покрытие, доступность и ближайший публичный слот.

Тренеры конкретного клуба могут отображаться внутри `club.details`, но не являются отдельной категорией глобального каталога `Клубы`.

## Нижняя навигация

`Профиль · События · Чаты · Клубы · Настройки`, активна вкладка `Клубы`.

## Состояния

- геолокация отключена;
- нет результатов;
- карта недоступна;
- организация без публичной страницы;
- offline.
""",
)

write(
    "docs/screens/play/main.md",
    """# События

- Screen ID: `play.main`
- Route: `/play`
- Visible bottom-tab label: `События`
- Internal route and screen ID remain `play` for backward compatibility.
- Variants: `player`, `trainer`, `organization`

## Назначение

Единый каталог, участие и управление играми, тренировками, турнирами, сезонами, турами, поездками и кэмпами. Поиск тренеров здесь не выполняется: игрок открывает его из блока `Мои тренеры` первой вкладки `Профиль`.

## Верхняя панель

- активный профиль;
- поиск событий;
- фильтры;
- список / карта;
- `Создать` с типами, разрешёнными active actor.

## Главный переключатель

```text
Все · Участвую · Управляю
```

- `Все` — только целиком публичные сущности;
- `Участвую` — участия, приглашения, заявки и ожидание, включая непубличные события;
- `Управляю` — созданные и доступные по роли события, задачи и черновики.

## Типы событий

Горизонтальная строка чипов:

```text
Все типы · Игры · Тренировки · Турниры · Сезоны · Туры и кэмпы
```

Внутри `Туры и кэмпы` доступны подтипы:

```text
Все · Тренерские кэмпы · Волейбольные туры · Поездки
```

Чипы не переносятся на второй ряд и прокручиваются горизонтально.

Дополнительные фильтры: дата, расстояние, уровень, формат, цена, свободные места, организатор, площадка, направление, проживание и ответственный сотрудник согласно типу и правам.

## Вкладка по умолчанию

- игрок → `Участвую`, если есть ближайшие участия; иначе `Все`;
- тренер → `Управляю`, если есть занятия или задачи; иначе `Участвую`;
- организация → `Управляю`;
- выбор сохраняется отдельно для каждого actor.

## Карточка события

Тип и подтип, название, дата, время, место или направление, организатор, цена, свободные места, статус пользователя и одно ближайшее действие.

Для trainer camp дополнительно кратко показываются ведущий тренер, уровень и число тренировок.

## Главное действие

- посторонний → `Присоединиться`, `Подать заявку` или `Забронировать`;
- участник → актуальное действие;
- организатор → `Управлять`;
- черновик → `Продолжить`.

## Навигация

- глобальное меню всегда `Профиль · События · Чаты · Клубы · Настройки`;
- отдельный административный tab bar запрещён;
- возврат восстанавливает вкладку, фильтры и позицию;
- `/play` сохраняется.

## Состояния

- loading skeleton;
- пустое `Участвую`;
- пустое `Управляю`;
- нет результатов фильтра;
- геолокация недоступна;
- offline read-only;
- частичная ошибка карты;
- actor permission changed.
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

## Новый игрок у тренера

После создания `player_trainer_relationship` trainer actor получает уведомление:

```text
Новый игрок
Анна добавила вас как тренера.
[Написать игроку]
```

Уведомление открывает публичный профиль игрока или личный чат. Оно не означает запись на тренировку и не раскрывает закрытые данные игрока.

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
- удалённая связь или сущность открывает понятное состояние;
- уведомление о новом игроке не создаётся повторно при идемпотентном повторе запроса.

## Состояния

- нет уведомлений;
- только прочитанные;
- связь уже удалена;
- действие выполнено на другом устройстве;
- потеря прав;
- offline.
""",
)

# Trainer profile additions.
replace_required(
    "docs/screens/clubs/trainer-details.md",
    "- Data sources: trainer actor profile, verification status, public trainings, tours, linked clubs, reviews and privacy settings",
    "- Data sources: trainer actor profile, verification status, public trainings, tours, linked clubs, reviews, privacy settings and player-trainer relationships",
)
replace_required(
    "docs/screens/clubs/trainer-details.md",
    """4. информационное состояние `Сейчас не принимает новых игроков` — без ложной кнопки записи.

Запись всегда происходит через канонический экран конкретной тренировки, а не напрямую из профиля тренера.
""",
    """4. `Добавить тренера` — для авторизованного игрока, когда связь ещё не создана и тренер принимает новых игроков;
5. состояние `Тренируется у этого тренера` — когда связь уже активна;
6. информационное состояние `Сейчас не принимает новых игроков` — без ложной кнопки.

Добавление тренера создаёт связь профилей, но не записывает игрока на тренировку. Запись всегда происходит через канонический экран конкретной тренировки.
""",
)
replace_required(
    "docs/screens/clubs/trainer-details.md",
    "- `trainer.owner_edit_profile` — владельцу открыть настройки публичного профиля.",
    "- `trainer.owner_edit_profile` — владельцу открыть настройки публичного профиля;\n- `trainer.add_relationship` — игроку добавить тренера и вернуться в первую вкладку `Профиль`.",
)
replace_required(
    "docs/screens/clubs/trainer-details.md",
    "Может открыть тренировку, записаться или подать заявку уже на её details screen, написать тренеру при разрешённой приватности и перейти к связанным сущностям.",
    "Может открыть тренировку, добавить тренера, записаться или подать заявку на details screen, написать при разрешённой приватности и перейти к связанным сущностям. Игрок может иметь несколько тренеров.",
)

# New relationship source of truth.
write(
    "docs/TRAINER_RELATIONSHIPS.yaml",
    """version: 1

scope: player_trainer_relationships

source_of_truth_for:
  - player trainer section on home.main
  - trainer search and selection
  - trainer new-player notifications
  - relationship-enabled direct messaging
  - trainer My Players relationship source

principles:
  - Игрок может иметь ноль, одного или несколько активных тренеров.
  - Связь инициирует игрок и отдельное подтверждение тренера не требуется.
  - Добавить можно только публичного тренера, который принимает новых игроков.
  - Связь не создаёт участие в тренировке, оплату, подписку на события или доступ к закрытым данным.
  - Это рабочая спортивная связь, а не дружба, подписка или социальный граф.
  - Игрок или тренер может завершить связь; блокировка всегда имеет приоритет.

model:
  table: player_trainer_relationships
  fields:
    - id
    - player_profile_id
    - trainer_actor_id
    - created_by_user_id
    - status
    - source
    - created_at
    - ended_at
    - ended_by_user_id
    - end_reason
  statuses:
    - active
    - removed_by_player
    - removed_by_trainer
    - blocked
  uniqueness: one active relationship per player_profile_id and trainer_actor_id
  multiple_trainers_per_player: true
  multiple_players_per_trainer: true

player_home:
  no_relationship:
    title: Без тренера
    primary_action: Найти тренера
    destination: trainer.search
  active_relationships:
    title: Тренируется у
    initial_visible_cards: 2
    show_all_when_more: true
    row_fields: [avatar, name, verification, specialization, city, next_public_training]
    actions: [open_trainer, remove_relationship]

search:
  screen_id: trainer.search
  route: /search/trainers
  searchable_fields: [display_name, city, specializations, languages]
  filters:
    - distance
    - player_level
    - specialization
    - session_format
    - language
    - accepting_new_players
    - has_upcoming_public_training
    - club_or_venue
  result_primary_action: add_trainer
  ranking_signals:
    - exact_name_match
    - same_city_or_distance
    - specialization_match
    - level_match
    - accepting_new_players
    - upcoming_public_training
  excluded:
    - hidden_profiles
    - blocked_relationships
    - verification_rejected_profiles

creation:
  actor: player
  requires_trainer_accepting_players: true
  confirmation_required_from_trainer: false
  idempotent: true
  effects:
    - relationship becomes active
    - player home section refreshes
    - trainer receives new_player notification
    - player appears in trainer My Players with source player_selected_trainer
    - direct messaging becomes allowed while privacy and blocking permit
  forbidden_effects:
    - create participation
    - enroll in training
    - expose private statistics
    - expose payments
    - expose private events

trainer_notification:
  type: trainer_new_player
  category: players_and_trainers
  title: Новый игрок
  body_template: "{player_name} добавил(а) вас как тренера."
  primary_action: trainer.message_new_player
  secondary_target: player.public_profile
  deduplicate_by: relationship_id

trainer_player_directory:
  source: player_selected_trainer
  appears_in: profile.players
  trainer_can:
    - open_public_profile
    - message_player
    - remove_relationship
    - invite_to_specific_event
  trainer_cannot:
    - see_private_statistics_without_separate_permission
    - see_unrelated_private_events
    - mark_payment_as_completed

messaging:
  allowed_when: relationship_active_and_not_blocked
  creates_social_group: false
  relationship_end_behavior: existing_chat_retention_by_policy_and_new_messages_disabled_unless_other_context_allows

privacy_and_safety:
  - Игрок показывает тренеру только публичные поля и данные, разрешённые отдельным контекстом.
  - Тренер может отключить принятие новых игроков в настройках.
  - Массовое автоматическое добавление тренеров запрещено.
  - Создание и удаление связи записывается в audit events.
  - Жалоба или блокировка немедленно отключает добавление и сообщения.
""",
)

# Integrate with player directory.
replace_required(
    "docs/PLAYER_DIRECTORY.yaml",
    """source_of_truth_for:
  - actor-owned player lists
  - player picker
""",
    """source_of_truth_for:
  - actor-owned player lists
  - trainer relationship-derived player rows
  - player picker
""",
)
replace_required(
    "docs/PLAYER_DIRECTORY.yaml",
    "  - В MVP нет друзей, подписчиков, социальных групп, учеников или партнёров как отдельных сущностей.",
    "  - В MVP нет друзей, подписчиков, социальных групп, учеников или партнёров как общих социальных сущностей; явная player-trainer связь описана отдельно в `docs/TRAINER_RELATIONSHIPS.yaml`.",
)
replace_required(
    "docs/PLAYER_DIRECTORY.yaml",
    """  recent:
    description: Игроки из общих завершённых или текущих событий, доступные по контексту участия.
  search:
""",
    """  recent:
    description: Игроки из общих завершённых или текущих событий, доступные по контексту участия.
  trainer_relationship:
    description: Игроки, которые сами добавили активный trainer actor; видны тренеру в `Моих игроках` с источником `player_selected_trainer`.
  search:
""",
)
replace_required(
    "docs/PLAYER_DIRECTORY.yaml",
    "  - Сохранение игрока не отправляет ему уведомление.",
    "  - Ручное сохранение игрока не отправляет ему уведомление; создание player-trainer связи, напротив, отправляет тренеру уведомление `Новый игрок`.",
)

# Data model.
replace_required(
    "docs/DATA_MODEL.md",
    """- `active_actor_preferences` — последний активный профиль.

Ключевой принцип:""",
    """- `active_actor_preferences` — последний активный профиль;
- `player_trainer_relationships` — явные активные и завершённые связи игрока с одним или несколькими trainer actor;
- `player_trainer_relationship_events` — аудит создания, завершения и блокировки связи.

`player_trainer_relationships` содержит `player_profile_id`, `trainer_actor_id`, status, source, created_at, ended_at и actor/user аудита. Активная пара уникальна, но один игрок может иметь несколько тренеров, а тренер — несколько игроков.

Ключевой принцип:""",
)
replace_required(
    "docs/DATA_MODEL.md",
    "- связь не является дружбой, ученичеством, партнёрством или участием;",
    "- обычная `actor_player_link` не является дружбой, ученичеством, партнёрством или участием; явная связь игрока с выбранным тренером хранится отдельно в `player_trainer_relationships`;",
)

# Decisions.
replace_required(
    "docs/DECISIONS.md",
    """`Профиль → Мои игроки` использует маршрут `/profile/players`, остаётся внутри profile stack и сохраняет глобальное нижнее меню `Профиль · События · Чаты · Клубы · Настройки` с активной вкладкой `Настройки`.
""",
    """`Настройки → Мои игроки` использует маршрут `/profile/players`, остаётся внутри технического profile stack и сохраняет глобальное нижнее меню `Профиль · События · Чаты · Клубы · Настройки` с активной вкладкой `Настройки`.
""",
)
append_once(
    "docs/DECISIONS.md",
    "## D-027 — Первая вкладка называется «Профиль»",
    """## D-027 — Первая вкладка называется «Профиль», пятая — «Настройки»

Статус: принято.

Пользовательское нижнее меню: `Профиль · События · Чаты · Клубы · Настройки`. Внутренние ids и маршруты сохраняются: первая вкладка — `home.main` на `/`, пятая — `profile.main` на `/profile`.

Первая вкладка является живой персональной страницей активного actor с ближайшими действиями и связями. Пятая вкладка является служебным списком настроек, архивов, календаря, платежей и управления профилями.

## D-028 — Туры, поездки и кэмпы находятся в «Событиях»

Статус: принято.

Глобальный каталог `Клубы` содержит только клубы, площадки и корты. Туры, поездки, лагеря и кэмпы являются вариантами сущности `tour` и ищутся в `События → Все` через тип `Туры и кэмпы`.

## D-029 — Игрок может добавить несколько тренеров

Статус: принято.

В первой вкладке игрок видит `Без тренера` либо `Тренируется у` с одной или несколькими активными связями. Поиск открывается на `/search/trainers`. Добавление инициирует игрок и не требует подтверждения тренера, если тренер принимает новых игроков.

Тренер получает уведомление `Новый игрок`, игрок появляется у него в `Моих игроках`, и личные сообщения становятся допустимы в рамках приватности и блокировок. Связь не создаёт участие, оплату или доступ к закрытым данным. Источник истины — `docs/TRAINER_RELATIONSHIPS.yaml`.
""",
)

# UI rules and design docs semantics.
replace_required(
    "docs/UI_RULES.md",
    """## Поиск

- В Событиях: игры, тренировки, турниры и сезоны.
- В Клубах: клубы, площадки, тренеры и туры.
- В Чатах: разговоры и участники.
- В личных разделах поиск работает по собственному архиву, а не по публичной выдаче города.
""",
    """## Поиск

- В `Событиях`: игры, тренировки, турниры, сезоны, туры, поездки и кэмпы.
- В `Клубах`: только клубы, площадки и корты.
- Тренер ищется из блока `Мои тренеры` первой вкладки игрока через `/search/trainers`.
- В `Чатах`: разговоры и участники.
- В `Настройках` и вложенных личных разделах поиск работает по собственному архиву, а не по публичной выдаче города.
""",
)
replace_required(
    "docs/UI_RULES.md",
    "- На Главной и в верхней части Событий показывается блок `Управляю`, если есть активные сущности.",
    "- В первой вкладке `Профиль` и в верхней части `Событий` показывается блок `Управляю`, если есть активные сущности.",
)

# My Players spec relation source and fifth-tab semantics.
replace_required(
    "docs/screens/profile/my-players.md",
    "`Мои игроки` является обычным stack-экраном внутри `Профиля`:",
    "`Мои игроки` является обычным stack-экраном внутри технического раздела `Настройки`:",
)
replace_required(
    "docs/screens/profile/my-players.md",
    "- `Недавние` — игроки из общих текущих или завершённых событий. Раздел не раскрывает историю вне общего контекста.",
    "- `Недавние` — игроки из общих текущих или завершённых событий; у trainer actor сюда также попадают игроки с активной связью `player_selected_trainer`. Раздел не раскрывает историю вне разрешённого контекста.",
)

# Architecture and flows.
append_once(
    "docs/USER_FLOWS.md",
    "## Игрок находит и добавляет тренера",
    """## Игрок находит и добавляет тренера

1. Игрок открывает первую вкладку `Профиль`.
2. В блоке `Мои тренеры` видит `Без тренера` или список уже добавленных тренеров.
3. Нажимает `Найти тренера`.
4. Ищет по имени, городу, специализации и формату, применяет фильтры.
5. Открывает публичный профиль либо нажимает `Добавить тренера` в выдаче.
6. Связь создаётся без отдельного подтверждения, если тренер принимает новых игроков.
7. Игрок возвращается в `Профиль` и видит `Тренируется у: Имя тренера`.
8. Тренер получает уведомление `Новый игрок`, видит человека в `Моих игроках` и может написать.
9. Добавление второго тренера создаёт ещё одну независимую активную связь.
10. Удаление связи не отменяет прошлые события и не удаляет историю чата автоматически.
""",
)
append_once(
    "docs/TEST_SCENARIOS.md",
    "## A-14 — Несколько тренеров у игрока",
    """## A-14 — Несколько тренеров у игрока

1. Игрок без trainer relationship открывает `/` и видит карточку `Без тренера`.
2. `Найти тренера` открывает `/search/trainers` и сохраняет возврат.
3. Поиск скрывает заблокированные и неактивные профили и показывает состояние `Не принимает новых игроков` без кнопки добавления.
4. Игрок добавляет доступного тренера и возвращается в `/`.
5. Профиль показывает `Тренируется у` и имя тренера.
6. Trainer actor получает ровно одно уведомление `Новый игрок`, а игрок появляется в `Моих игроках` с source `player_selected_trainer`.
7. Тренер может написать игроку, но не видит его закрытую статистику, платежи и непубличные события.
8. Игрок добавляет второго тренера; обе связи отображаются независимо.
9. Удаление одной связи оставляет вторую активной и не меняет участия в событиях.
10. Нижнее меню на всех шагах остаётся `Профиль · События · Чаты · Клубы · Настройки`; search stack не создаёт шестую вкладку.
""",
)

# Compact architecture/app map notes.
append_once(
    "docs/ARCHITECTURE.md",
    "## Player ↔ trainer relationships",
    """## Player ↔ trainer relationships

Игрок на первой вкладке `Профиль` может найти и добавить несколько trainer actor. Поиск открывается на `/search/trainers`; тренер получает уведомление и видит игрока в `Моих игроках`. Связь не создаёт participation и не раскрывает закрытые данные. Полный контракт: `docs/TRAINER_RELATIONSHIPS.yaml`.

Туры, поездки и кэмпы относятся к `Событиям`. `Клубы` остаются каталогом клубов, площадок и кортов.
""",
)
append_once(
    "docs/APP_MAP.md",
    "Найти тренера (`trainer.search`)",
    """### Профиль игрока и тренеры

- Профиль (`home.main`, `/`)
  - `Без тренера` → Найти тренера (`trainer.search`, `/search/trainers`)
  - результат → Публичный тренер (`trainer.public_profile`, `/trainers/:trainerId`)
  - Добавить тренера → создать relationship → вернуться в `/`
  - `Тренируется у` → одна или несколько карточек тренеров
- Настройки (`profile.main`, `/profile`)
  - архивы, календарь, платежи, параметры и управление actor-профилями

Туры, поездки и кэмпы находятся в `Событиях`; глобальный каталог `Клубы` содержит клубы, площадки и корты.
""",
)

# Mermaid map: append standalone nodes/edges if not already present.
append_once(
    "docs/diagrams/app-map.mmd",
    "TrainerSearch[\"Найти тренера",
    """%% Player trainer relationship flow
HomeProfile["Профиль / home.main"] -->|Без тренера / добавить ещё| TrainerSearch["Найти тренера / trainer.search"]
TrainerSearch --> TrainerPublic["Публичный тренер / trainer.public_profile"]
TrainerSearch -->|Добавить тренера| HomeProfile
SettingsRoot["Настройки / profile.main"]
""",
)

print("Profile/settings rename and trainer relationship migration completed.")
