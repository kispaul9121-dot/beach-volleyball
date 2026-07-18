#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        value = yaml.safe_load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a mapping")
    return value


def save_yaml(path: Path, value: dict[str, Any]) -> None:
    path.write_text(
        yaml.safe_dump(value, allow_unicode=True, sort_keys=False, width=1000),
        encoding="utf-8",
    )


def find_by(items: list[dict[str, Any]], key: str, value: str) -> dict[str, Any]:
    for item in items:
        if str(item.get(key, "")) == value:
            return item
    raise KeyError(f"Missing {key}={value}")


def replace_action(actions: list[dict[str, Any]], old_ids: set[str], new_action: dict[str, Any]) -> None:
    first_index = next((i for i, item in enumerate(actions) if item.get("id") in old_ids), len(actions))
    actions[:] = [item for item in actions if item.get("id") not in old_ids]
    actions.insert(first_index, new_action)


PROFILE_ACTIVITY = {
    "version": 1,
    "scope": "profile_activity",
    "source_of_truth_for": [
        "personal participation and management entry points",
        "two-tab personal activity lists",
        "post-join Profile tab feedback",
        "discovery-only boundaries for Games and Camps",
    ],
    "catalog_boundaries": {
        "games": {
            "screen": "play.main",
            "route": "/play",
            "mode": "discovery_only",
            "allows": ["browse", "search", "filter", "open_details", "start_join_flow"],
            "forbids": ["participating_tab", "managing_tab", "personal_archive", "management_dashboard"],
        },
        "camps": {
            "screen": "camps.main",
            "route": "/camps",
            "mode": "discovery_only",
            "allows": ["browse", "search", "filter", "open_details", "start_join_flow"],
            "forbids": ["participating_tab", "managing_tab", "personal_archive", "management_dashboard"],
        },
    },
    "profile_root": {
        "screen": "home.main",
        "route": "/",
        "activity_switch": {
            "values": ["participating", "managing"],
            "labels": {"participating": "Участвую", "managing": "Управляю"},
            "default_by_actor": {"player": "participating", "trainer": "managing", "organization": "managing"},
            "persist_per_actor": True,
        },
        "participating_sections": ["games", "trainings", "tournaments", "camps"],
        "managing_sections": ["games", "trainings", "tournaments", "camps"],
        "preview_rule": "show_nearest_items_and_required_actions_then_open_full_list",
    },
    "full_lists": {
        "games": {
            "screen": "profile.my_games",
            "route": "/profile/games",
            "participating_tabs": ["upcoming", "past"],
            "participating_labels": ["Предстоящие", "Прошедшие"],
            "managing_tabs": ["active", "completed"],
            "managing_labels": ["Активные", "Завершённые"],
        },
        "trainings": {
            "screen": "profile.trainings",
            "route": "/profile/trainings",
            "participating_tabs": ["booked", "past"],
            "participating_labels": ["Записан", "Прошедшие"],
            "managing_tabs": ["active", "completed"],
            "managing_labels": ["Активные", "Завершённые"],
        },
        "tournaments": {
            "screen": "profile.competitions",
            "route": "/profile/competitions",
            "participating_tabs": ["registered", "past"],
            "participating_labels": ["Заявлен", "Прошедшие"],
            "managing_tabs": ["active", "completed"],
            "managing_labels": ["Активные", "Завершённые"],
        },
        "camps": {
            "screen": "profile.trips",
            "route": "/profile/trips",
            "participating_tabs": ["booked", "past"],
            "participating_labels": ["Записан", "Прошедшие"],
            "managing_tabs": ["active", "completed"],
            "managing_labels": ["Активные", "Завершённые"],
        },
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
        "confirmed": {
            "semantic_color": "status.success",
            "badge": "check",
            "message": "Игра добавлена в Профиль",
        },
        "pending_or_payment_required": {
            "semantic_color": "status.info",
            "badge": "dot",
            "message": "Статус вступления сохранён в Профиле",
        },
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


HOME_MD = """# Профиль

- Screen ID: `home.main`
- Route: `/`
- User-facing bottom-tab title: `Профиль`
- Internal tab ID remains `home`
- Variants: `player`, `trainer`, `organization`
- Activity contract: `docs/PROFILE_ACTIVITY.yaml`
- UI contract: `docs/DESIGN_SYSTEM.md` and `docs/DESIGN_TOKENS.yaml`

Первая вкладка объединяет живую профильную страницу active actor и всю связанную личную активность. Публичные каталоги остаются в `Игры` и `Кэмпы`; личные участия и управление больше не дублируются в каталогах или Настройках.

## Общая верхняя часть

- фото или логотип active actor;
- имя и тип профиля;
- город и статус проверки;
- уведомления и переключение actor;
- редактирование публичной информации;
- корневой экран не показывает кнопку назад.

## Игрок

Перед личной активностью сохраняются:

1. шапка спортивного профиля;
2. `Мои тренеры`;
3. ближайшее требуемое действие;
4. приглашения и изменения, требующие реакции.

Связь с тренером работает по контракту `docs/TRAINER_RELATIONSHIPS.yaml`.

## Переключатель активности

```text
Участвую · Управляю
```

Переключатель находится внутри Профиля и сохраняется отдельно для каждого actor-профиля.

### Участвую

Короткие блоки:

- Мои игры;
- Мои тренировки;
- Мои турниры;
- Мои кэмпы.

Каждый блок показывает ближайший элемент, текущий статус и требуемое действие, затем ведёт в полный список. В полном списке всегда две временные вкладки:

- игры — `Предстоящие · Прошедшие`;
- тренировки — `Записан · Прошедшие`;
- турниры — `Заявлен · Прошедшие`;
- кэмпы — `Записан · Прошедшие`.

### Управляю

Показывает игры, тренировки, турниры и кэмпы, созданные active actor или доступные по роли. Для каждого типа полный список имеет только:

```text
Активные · Завершённые
```

Черновики, заявки, оплаты, незаполненные результаты и другие задачи показываются статусами и фильтрами внутри `Активные`, а не создают дополнительные верхние вкладки.

## Подтверждение после вступления

Когда после действия `Вступить` в личной активности появляется или обновляется запись:

- иконка нижней вкладки `Профиль` один раз подсвечивается на 900 мс;
- подтверждённое участие использует `status.success` и маленький check-badge;
- заявка или необходимость оплаты использует `status.info` и dot-badge, чтобы не изображать подтверждённое участие;
- одновременно показывается короткое сообщение о том, что игра или её текущий статус сохранены в Профиле;
- анимация не повторяется, не меняет размеры меню и учитывает Reduce Motion.

Конкретные значения цветов ещё не утверждены; используются только semantic tokens.

## Тренер и организация

Для тренера и организации по умолчанию открывается `Управляю`. Операционные задачи, посещаемость, заявки, оплаты, сотрудники и загрузка площадок показываются в профильных блоках active actor. Личное спортивное участие тренера остаётся в `Участвую` и связано с player profile.

## Нижняя навигация

```text
Профиль · Игры · Чаты · Кэмпы · Настройки
```

На этом экране активна вкладка `Профиль`.

## Состояния

- loading;
- профиль заполнен не полностью;
- нет участий;
- нет управляемых сущностей;
- вступление сохранено как заявка или ожидание оплаты;
- участие подтверждено;
- partial error отдельного блока;
- offline с последними сохранёнными данными;
- permission changed.
"""


PLAY_MD = """# Игры

- Screen ID: `play.main`
- Route: `/play`
- Visible bottom-tab label: `Игры`
- Internal route and screen ID remain `play` for compatibility.
- Variants: `player`, `trainer`, `organization`
- Catalog contract: `docs/GAMES_CATALOG.yaml`
- Personal activity contract: `docs/PROFILE_ACTIVITY.yaml`

## Назначение

`Игры` — чистая витрина для подбора, поиска, фильтрации, просмотра и начала вступления. Здесь нет вкладок `Участвую` и `Управляю`: личная активность находится в нижней вкладке `Профиль`.

## Верхняя панель

- строка поиска по играм, тренировкам, турнирам, организациям, площадкам и игрокам;
- фильтры;
- список / карта, когда карта полезна;
- active actor используется для контекста, но спортивное участие привязывается к player profile.

## Категории

```text
Игры · Тренировки · Турниры
```

Если выбран раздел `Турниры`, появляется вторая горизонтальная строка:

```text
Все · Классика · Король пляжа · Сезонные
```

Чипы не переносятся и прокручиваются горизонтально.

## Выдача

- открытые публичные игры любых игроков;
- игры отслеживаемых организаций;
- публичные игры сохранённых в `Мои игроки` людей;
- публичные тренировки частных тренеров и организаций;
- классические, `Король пляжа` и сезонные турниры.

Все списки идут от ближайшей будущей даты к более поздним. Завершённые элементы в каталог не подмешиваются.

## Карточка

- заметные дата и время;
- тип и формат;
- название и место;
- создатель;
- цена либо `Бесплатно`;
- заполненность и свободные места;
- текущий статус пользователя, если отношение уже существует;
- одно основное действие.

## Вступление

Пока используется единая пользовательская кнопка:

```text
Вступить
```

Она запускает `system.resolve_join_flow`. Финальное поведение ещё не утверждено: бесплатное моментальное вступление, оплата, заявка организатору, лист ожидания и приглашение будут спроектированы отдельно.

После появления записи в личной активности пользователь получает одноразовый сигнал на иконке `Профиль` и может найти элемент в `Профиль → Участвую`.

## Пустое состояние

```text
Пока нет подходящих игр
[Добавить организацию] [Добавить игроков]
```

Обе кнопки сразу открывают соответствующий поиск. Каталог не показывает личный архив или кабинет управления.

## Навигация

Карточка открывает один канонический detail route. Возврат восстанавливает категорию, чипы, фильтры и позицию списка. Организации и площадки открываются как deep links из поиска.

## Состояния

- loading skeleton;
- пустой каталог;
- нет результатов после фильтра;
- геолокация выключена;
- offline read-only;
- частичная ошибка карты;
- событие стало непубличным.
"""


CAMPS_MD = """# Кэмпы

- Screen ID: `camps.main`
- Route: `/camps`
- Visible bottom-tab label: `Кэмпы`
- Variants: `player`, `trainer`, `organization`
- Personal activity contract: `docs/PROFILE_ACTIVITY.yaml`

## Назначение

Отдельная витрина многодневных и выездных волейбольных форматов. Экран предназначен для подбора, поиска, фильтрации, просмотра и начала вступления. Личные записи и управление находятся в `Профиль`.

Кэмп может создать организация, частный тренер или игрок, который собирает людей вместе играть. Коммерческое проживание и транспорт необязательны.

## Быстрые фильтры

```text
Ближайшие · На море · С тренером · Только игры · С проживанием
```

Чипы прокручиваются горизонтально и не переносятся.

## Создатели

- player actor — совместная поездка или серия игр без обязательного коммерческого пакета;
- trainer actor — тренировочный лагерь с программой;
- organization actor — кэмп с пакетами, сотрудниками, проживанием и платежами.

## Сортировка и карточка

Кэмпы идут от ближайшей даты к самой поздней. Карточка показывает даты, место, создателя, формат, подходящий уровень, длительность, цену или бюджет, свободные места и одно действие.

## Вступление

Кнопка `Вступить` запускает общий resolver. Способ записи, заявки, оплаты или бронирования будет утверждён отдельно. После создания личной записи кэмп появляется в `Профиль → Участвую → Мои кэмпы`.

## Мои кэмпы

Полный личный список находится по маршруту `/profile/trips` и имеет ровно две вкладки:

```text
Записан · Прошедшие
```

Созданные и управляемые кэмпы находятся в `Профиль → Управляю` и используют `Активные · Завершённые`.

## Создание

Создание открывается из `Профиль → Управляю`. Мастер адаптируется к actor и не требует проживания, транспорта или коммерческой цены для обычной группы игроков.

## Состояния

- loading;
- нет опубликованных кэмпов;
- нет результатов фильтра;
- offline read-only;
- геолокация недоступна;
- кэмп заполнен или набор закрыт.
"""


SETTINGS_MD = """# Настройки

- Screen ID: `profile.main`
- Route: `/profile`
- User-facing bottom-tab title: `Настройки`
- Internal tab ID remains `profile`
- Variants: `player`, `trainer`, `organization`

Пятая вкладка является только служебным центром аккаунта и active actor. Участия, созданные события, личные архивы и управление находятся в первой вкладке `Профиль` и здесь не дублируются.

## Верхняя часть

- компактный active actor;
- переключение actor;
- статус заполнения или проверки;
- переход к первой вкладке для просмотра профильной страницы.

## Общие разделы

- Мои профили;
- Мои игроки;
- Статистика;
- Платежи и выплаты согласно actor;
- Аккаунт и приложение;
- Безопасность, приватность и уведомления;
- Помощь и юридические документы;
- Опасные действия.

## Вариант тренера

Дополнительно показывает рабочий список `Мои игроки`, выплаты, профессиональные параметры и ссылку на публичный профиль.

## Вариант организации

Дополнительно показывает площадки, сотрудников, финансы, аудит и параметры организации без отдельной нижней навигации. Сами игры, тренировки, турниры и кэмпы управляются из первой вкладки `Профиль`.

## Нижняя навигация

```text
Профиль · Игры · Чаты · Кэмпы · Настройки
```

На этом экране активна вкладка `Настройки`.

## Состояния

- actor draft;
- verification pending;
- permission changed;
- offline;
- раздел временно недоступен.
"""


MY_GAMES_MD = """# Мои игры

- Screen ID: `profile.my_games`
- Route: `/profile/games`
- Entry: `Профиль → Участвую` or `Профиль → Управляю`
- Activity contract: `docs/PROFILE_ACTIVITY.yaml`

## Режим «Участвую»

Ровно две вкладки:

```text
Предстоящие · Прошедшие
```

Статусы заявки, оплаты, приглашения, листа ожидания, переноса и отмены показываются внутри карточки и не создают новые верхние вкладки.

Карточка показывает дату, место, формат, организатора, текущий статус, оплату, чат и результат после завершения.

## Режим «Управляю»

Ровно две вкладки:

```text
Активные · Завершённые
```

`Активные` включает опубликованные игры, черновики и элементы, требующие действий. Карточка показывает actor-создателя, заполненность, заявки, оплаты, раунды, результаты и ближайший управленческий шаг.

## Пустые состояния

- нет предстоящих → `Найти игру`;
- нет прошедших → спокойное пустое состояние без создания;
- нет активных управляемых → `Создать игру`;
- нет завершённых управляемых → пустой архив.

Возврат ведёт в Профиль с восстановлением режима `Участвую` или `Управляю`.
"""


MY_TRAININGS_MD = """# Мои тренировки

- Screen ID: `profile.trainings`
- Route: `/profile/trainings`
- Entry: `Профиль → Участвую` or `Профиль → Управляю`
- Activity contract: `docs/PROFILE_ACTIVITY.yaml`

## Режим «Участвую»

```text
Записан · Прошедшие
```

Первая вкладка содержит все текущие отношения с будущими тренировками. Статус внутри карточки отличает приглашение, заявку, ожидание оплаты и подтверждённую запись.

## Режим «Управляю»

```text
Активные · Завершённые
```

`Активные` объединяет занятия сегодня, будущие занятия, черновики и задачи по заявкам, оплатам, программе и посещаемости. Дополнительные статусы не создают новые верхние вкладки.

## Карточка

Показывает тренера или организацию, программу, уровень, дату, место, статус отношения, оплату, заполненность, чат и ближайшее действие.

Постоянные тренировочные группы в MVP не используются. Повтор создаётся дублированием тренировки.
"""


MY_COMPETITIONS_MD = """# Мои турниры

- Screen ID: `profile.competitions`
- Route: `/profile/competitions`
- Entry: `Профиль → Участвую` or `Профиль → Управляю`
- Activity contract: `docs/PROFILE_ACTIVITY.yaml`

Сезонный турнир является режимом `tournament`, а не отдельной сущностью.

## Режим «Участвую»

```text
Заявлен · Прошедшие
```

Первая вкладка содержит текущую регистрацию и будущие турниры. Карточка показывает формат, ближайший матч или игровой день, место в таблице, оплату, статус и сообщения.

## Режим «Управляю»

```text
Активные · Завершённые
```

`Активные` объединяет опубликованные турниры, черновики и задачи по регистрации, жеребьёвке, игровым дням, результатам и оплатам.

Фильтр формата может использовать `Классика`, `Король пляжа` и `Сезонный`, но не заменяет две временные вкладки.
"""


MY_CAMPS_MD = """# Мои кэмпы

- Screen ID: `profile.trips`
- Route: `/profile/trips`
- Entry: `Профиль → Участвую` or `Профиль → Управляю`
- Activity contract: `docs/PROFILE_ACTIVITY.yaml`

## Режим «Участвую»

Ровно две вкладки:

```text
Записан · Прошедшие
```

`Записан` содержит все текущие отношения с будущими кэмпами. Карточка обязана явно показывать реальный статус: приглашение, заявка, ожидание оплаты, подтверждено или лист ожидания. Название вкладки не означает автоматического подтверждения.

Карточка показывает создателя, даты, направление, программу, размещение при наличии, документы, оплату, свободные места и чат.

## Режим «Управляю»

```text
Активные · Завершённые
```

`Активные` включает опубликованные кэмпы, черновики и задачи по заявкам, местам, оплатам, программе и документам. Кэмп может быть создан игроком, тренером или организацией.

## Пустые состояния

- `Записан` пуст → `Найти кэмп`;
- `Прошедшие` пуст → спокойный архив;
- `Активные` пуст → `Создать кэмп`;
- `Завершённые` пуст → пустой архив.
"""


def main() -> None:
    # New source of truth.
    save_yaml(DOCS / "PROFILE_ACTIVITY.yaml", PROFILE_ACTIVITY)

    # Human-readable specs.
    (DOCS / "screens/home/main.md").write_text(HOME_MD, encoding="utf-8")
    (DOCS / "screens/play/main.md").write_text(PLAY_MD, encoding="utf-8")
    (DOCS / "screens/camps/main.md").write_text(CAMPS_MD, encoding="utf-8")
    (DOCS / "screens/profile/main.md").write_text(SETTINGS_MD, encoding="utf-8")
    (DOCS / "screens/profile/my-games.md").write_text(MY_GAMES_MD, encoding="utf-8")
    (DOCS / "screens/profile/my-trainings.md").write_text(MY_TRAININGS_MD, encoding="utf-8")
    (DOCS / "screens/profile/my-competitions.md").write_text(MY_COMPETITIONS_MD, encoding="utf-8")
    (DOCS / "screens/profile/my-trips.md").write_text(MY_CAMPS_MD, encoding="utf-8")

    # Catalog contract.
    games = load_yaml(DOCS / "GAMES_CATALOG.yaml")
    bottom = games.setdefault("bottom_tab", {})
    bottom.pop("primary_tabs", None)
    bottom["mode"] = "discovery_only"
    bottom["capabilities"] = ["browse", "search", "filter", "open_details", "start_join_flow"]
    games["personal_activity"] = {
        "location": "home.main",
        "contract": "docs/PROFILE_ACTIVITY.yaml",
        "catalog_tabs_forbidden": ["participating", "managing"],
    }
    empty = games.get("empty_states", {}) or {}
    games["empty_states"] = {"all": empty.get("all", {})}
    save_yaml(DOCS / "GAMES_CATALOG.yaml", games)

    # Screen registry.
    screens_doc = load_yaml(DOCS / "SCREENS.yaml")
    screens = screens_doc.get("screens", [])
    find_by(screens, "id", "home.main")["purpose"] = "Живая профильная страница active actor с переключателем Участвую / Управляю и входами во всю личную активность."
    find_by(screens, "id", "play.main")["purpose"] = "Публичный подбор, поиск, фильтрация и начало вступления в игры, тренировки и турниры без личных вкладок."
    find_by(screens, "id", "camps.main")["purpose"] = "Публичный подбор, поиск, фильтрация и начало вступления в кэмпы без личных вкладок."
    find_by(screens, "id", "profile.main")["purpose"] = "Настройки аккаунта, профилей, платежей, безопасности и служебных параметров без личных архивов."
    find_by(screens, "id", "profile.my_games")["purpose"] = "Личный список игр из Профиля: Предстоящие / Прошедшие или Активные / Завершённые."
    find_by(screens, "id", "profile.trainings")["purpose"] = "Личный список тренировок из Профиля: Записан / Прошедшие или Активные / Завершённые."
    find_by(screens, "id", "profile.competitions")["purpose"] = "Личный список турниров из Профиля: Заявлен / Прошедшие или Активные / Завершённые."
    find_by(screens, "id", "profile.trips")["purpose"] = "Мои кэмпы: Записан / Прошедшие или управляемые Активные / Завершённые."
    save_yaml(DOCS / "SCREENS.yaml", screens_doc)

    # Routes.
    routes_doc = load_yaml(DOCS / "ROUTES.yaml")
    routes = routes_doc.get("routes", [])
    play_route = find_by(routes, "path", "/play")
    play_route["accepts_query"] = [
        value for value in play_route.get("accepts_query", [])
        if value not in {"tab", "actorId"}
    ]
    camps_route = find_by(routes, "path", "/camps")
    camps_route["accepts_query"] = [
        value for value in camps_route.get("accepts_query", [])
        if value not in {"tab", "actorId"}
    ]
    home_route = find_by(routes, "path", "/")
    home_route["accepts_query"] = ["activityMode", "highlightEntityType", "highlightEntityId"]
    for path in ("/profile/games", "/profile/trainings", "/profile/competitions", "/profile/trips"):
        find_by(routes, "path", path)["accepts_query"] = ["mode", "tab", "actorId"]
    save_yaml(DOCS / "ROUTES.yaml", routes_doc)

    # Actions.
    actions_doc = load_yaml(DOCS / "ACTIONS.yaml")
    actions = actions_doc.get("actions", [])
    for action_id in (
        "nav.open_profile_calendar",
        "nav.open_profile_my_games",
        "nav.open_profile_competitions",
        "nav.open_profile_trainings",
        "nav.open_profile_trips",
    ):
        find_by(actions, "id", action_id)["source"] = "home.main"
    find_by(actions, "id", "nav.open_profile_competitions")["label"] = "Мои турниры"
    find_by(actions, "id", "nav.open_profile_trips")["label"] = "Мои кэмпы"
    replace_action(
        actions,
        {"entity.join", "entity.request_to_join", "entity.join_waitlist"},
        {
            "id": "entity.start_join_flow",
            "label": "Вступить",
            "source": "dynamic.entity_details",
            "destination": "system.resolve_join_flow",
            "success": "system.profile_activity_feedback",
            "permission": "authenticated",
        },
    )
    if not any(item.get("id") == "home.change_activity_mode" for item in actions):
        insert_at = next((i for i, item in enumerate(actions) if item.get("id") == "home.open_managed_entity"), len(actions))
        actions.insert(insert_at, {
            "id": "home.change_activity_mode",
            "label": "Участвую / Управляю",
            "source": "home.main",
            "destination": "system.local_state",
            "permission": "authenticated",
        })
    replacements = {
        "my_games.create": "/profile/games?mode=managing&tab=active",
        "my_games.continue_draft": "/profile/games?mode=managing&tab=active",
        "competitions.create_tournament": "/profile/competitions?mode=managing&tab=active",
        "trainings.create": "/profile/trainings?mode=managing&tab=active",
        "trips.create": "/?activityMode=managing",
    }
    for action_id, return_to in replacements.items():
        action = find_by(actions, "id", action_id)
        action.setdefault("context", {})["returnTo"] = return_to
    trips_create = find_by(actions, "id", "trips.create")
    trips_create["label"] = "Создать кэмп"
    trips_create["source"] = "home.main"
    save_yaml(DOCS / "ACTIONS.yaml", actions_doc)

    # One-shot tab feedback token.
    tokens = load_yaml(DOCS / "DESIGN_TOKENS.yaml")
    tokens.setdefault("motion", {}).setdefault("one_shot_feedback", {})["profile_activity_confirmation"] = {
        "component": "AppTabBar",
        "tab_id": "home",
        "duration_ms": 900,
        "repetitions": 1,
        "confirmed_semantic_color": "status.success",
        "pending_semantic_color": "status.info",
        "non_color_signal": "check_or_dot_badge_and_accessibility_announcement",
        "reduce_motion_fallback": "static_badge_then_fade",
        "layout_change_forbidden": True,
    }
    save_yaml(DOCS / "DESIGN_TOKENS.yaml", tokens)

    # README summary.
    readme_path = ROOT / "README.md"
    readme = readme_path.read_text(encoding="utf-8")
    readme = readme.replace(
        "- `Игры` — открытые игры, публичные тренировки и турниры;",
        "- `Игры` — подбор, поиск и начало вступления в открытые игры, публичные тренировки и турниры;",
    )
    readme = readme.replace(
        "- `Кэмпы` — лагеря, совместные поездки и многодневные игровые форматы;",
        "- `Кэмпы` — подбор и начало вступления в лагеря, совместные поездки и многодневные игровые форматы;",
    )
    marker = "Организации, площадки и публичные игроки ищутся внутри `Игры`."
    insertion = (
        "Личные вкладки `Участвую` и `Управляю` находятся в `Профиль`; "
        "каталоги `Игры` и `Кэмпы` используются только для подбора, поиска и вступления. "
        "После появления личной записи иконка `Профиль` даёт одноразовый доступный сигнал.\n\n"
    )
    if insertion not in readme and marker in readme:
        readme = readme.replace(marker, insertion + marker)
    readme_path.write_text(readme, encoding="utf-8")

    # Decision log.
    decisions_path = DOCS / "DECISIONS.md"
    decisions = decisions_path.read_text(encoding="utf-8")
    decision = """

## D-026 — Личная активность переносится в Профиль

- `Игры` и `Кэмпы` являются discovery-only каталогами: подбор, поиск, фильтры, просмотр и начало вступления.
- `Участвую · Управляю` находится в первой вкладке `Профиль`.
- Полные личные списки используют ровно две временные вкладки; для `Мои кэмпы` это `Записан · Прошедшие`.
- Управляемые сущности используют `Активные · Завершённые`.
- Финальный способ вступления не утверждён; единая кнопка `Вступить` запускает resolver.
- После создания или обновления личной записи иконка `Профиль` даёт одноразовый доступный сигнал без изменения геометрии нижнего меню.
"""
    if "## D-026 — Личная активность переносится в Профиль" not in decisions:
        decisions_path.write_text(decisions.rstrip() + decision + "\n", encoding="utf-8")

    # Permanent validator and workflow registration.
    workflow_path = ROOT / ".github/workflows/validate-architecture.yml"
    workflow = workflow_path.read_text(encoding="utf-8")
    if '"scripts/validate_profile_activity.py"' not in workflow:
        workflow = workflow.replace(
            '      - "scripts/validate_design_system.py"\n',
            '      - "scripts/validate_design_system.py"\n      - "scripts/validate_profile_activity.py"\n',
        )
    if "Validate Profile activity and discovery boundaries" not in workflow:
        workflow = workflow.replace(
            "      - name: Validate dark-first cross-platform design system\n        run: python scripts/validate_design_system.py\n",
            "      - name: Validate dark-first cross-platform design system\n        run: python scripts/validate_design_system.py\n\n      - name: Validate Profile activity and discovery boundaries\n        run: python scripts/validate_profile_activity.py\n",
        )
    workflow_path.write_text(workflow, encoding="utf-8")


if __name__ == "__main__":
    main()
