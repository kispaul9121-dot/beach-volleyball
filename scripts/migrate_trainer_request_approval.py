#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def write(path: str, content: str) -> None:
    target = ROOT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content.rstrip() + "\n", encoding="utf-8")


def load_yaml(path: str) -> dict[str, Any]:
    value = yaml.safe_load(read(path))
    if not isinstance(value, dict):
        raise RuntimeError(f"{path} must contain a mapping")
    return value


def save_yaml(path: str, value: dict[str, Any]) -> None:
    write(path, yaml.safe_dump(value, allow_unicode=True, sort_keys=False, width=120))


def replace_once(path: str, old: str, new: str) -> None:
    content = read(path)
    if old not in content:
        raise RuntimeError(f"Expected text not found in {path}: {old[:120]!r}")
    write(path, content.replace(old, new, 1))


def append_once(path: str, marker: str, block: str) -> None:
    content = read(path)
    if marker in content:
        return
    write(path, content.rstrip() + "\n\n" + block.rstrip() + "\n")


# ACTIONS.yaml: request first, trainer explicitly accepts from notification or My Players > New.
actions_doc = load_yaml("docs/ACTIONS.yaml")
actions = actions_doc.get("actions")
if not isinstance(actions, list):
    raise RuntimeError("docs/ACTIONS.yaml actions must be a list")

by_id = {str(item.get("id")): item for item in actions if isinstance(item, dict) and item.get("id")}


def rename_action(old_id: str, new_id: str, **updates: Any) -> None:
    item = by_id.get(old_id) or by_id.get(new_id)
    if item is None:
        raise RuntimeError(f"Missing action {old_id} / {new_id}")
    item["id"] = new_id
    item.update(updates)
    by_id.pop(old_id, None)
    by_id[new_id] = item


def upsert_action(action_id: str, **fields: Any) -> None:
    item = by_id.get(action_id)
    if item is None:
        item = {"id": action_id}
        actions.append(item)
        by_id[action_id] = item
    item.clear()
    item["id"] = action_id
    item.update(fields)


rename_action(
    "trainer.add_from_search",
    "trainer.request_from_search",
    label="Отправить запрос",
    source="trainer.search",
    destination="system.create_trainer_relationship_request",
    success="home.main",
    permission="authenticated_player",
)
rename_action(
    "trainer.add_from_profile",
    "trainer.request_from_profile",
    label="Отправить запрос",
    source="trainer.public_profile",
    destination="system.create_trainer_relationship_request",
    success="home.main",
    permission="authenticated_player",
)
rename_action(
    "trainer.message_new_player",
    "trainer.message_requesting_player",
    label="Написать игроку",
    source="global.notifications",
    destination="system.open_or_create_direct_chat",
    permission="trainer_relationship_request_recipient",
)

upsert_action(
    "profile.cancel_trainer_request",
    label="Отменить запрос тренеру",
    source="home.main",
    destination="system.cancel_trainer_relationship_request_confirmation",
    permission="relationship_request_owner",
)
upsert_action(
    "trainer.open_pending_player",
    label="Открыть профиль игрока",
    source="profile.players",
    destination="player.public_profile",
    permission="trainer_relationship_request_recipient",
)
upsert_action(
    "trainer.message_pending_player",
    label="Написать игроку",
    source="profile.players",
    destination="system.open_or_create_direct_chat",
    permission="trainer_relationship_request_recipient",
)
upsert_action(
    "trainer.accept_player_request",
    label="Добавить",
    source="profile.players",
    destination="system.accept_trainer_relationship_request",
    permission="relationship_target_trainer",
)
upsert_action(
    "trainer.decline_player_request",
    label="Отклонить",
    source="profile.players",
    destination="system.decline_trainer_relationship_request_confirmation",
    permission="relationship_target_trainer",
)
upsert_action(
    "trainer.accept_player_request_notification",
    label="Добавить",
    source="global.notifications",
    destination="system.accept_trainer_relationship_request",
    permission="relationship_target_trainer",
)
upsert_action(
    "trainer.decline_player_request_notification",
    label="Отклонить",
    source="global.notifications",
    destination="system.decline_trainer_relationship_request_confirmation",
    permission="relationship_target_trainer",
)

save_yaml("docs/ACTIONS.yaml", actions_doc)

# Trainer public profile now sends a request and returns to trainer search for direct deep links.
screens_doc = load_yaml("docs/SCREENS.yaml")
for screen in screens_doc.get("screens", []):
    if isinstance(screen, dict) and screen.get("id") == "trainer.public_profile":
        screen["back_fallback"] = "/trainers/search"
save_yaml("docs/SCREENS.yaml", screens_doc)

routes_doc = load_yaml("docs/ROUTES.yaml")
for route in routes_doc.get("routes", []):
    if isinstance(route, dict) and route.get("screen") == "trainer.public_profile":
        route["back_fallback"] = "/trainers/search"
save_yaml("docs/ROUTES.yaml", routes_doc)

trainer_spec = read("docs/screens/clubs/trainer-details.md")
trainer_spec = trainer_spec.replace("- Section: `Клубы → Тренеры`", "- Entry points: `Профиль → Найти тренера`, клуб, событие или direct link")
trainer_spec = trainer_spec.replace(
    "1. `Ближайшая тренировка` — когда есть доступное публичное занятие;\n2. `Посмотреть расписание` — когда расписание есть, но ближайшая карточка не выбрана;\n3. `Написать` — только когда тренер разрешил личные сообщения;\n4. информационное состояние `Сейчас не принимает новых игроков` — без ложной кнопки записи.",
    "1. `Отправить запрос` — для игрока без pending или active связи, когда тренер принимает новых игроков;\n2. `Запрос отправлен` — информационное состояние pending-запроса;\n3. `Тренируется у` — состояние активной связи;\n4. `Ближайшая тренировка` или `Посмотреть расписание` — когда relationship CTA не является главным;\n5. `Написать` — когда это разрешено текущим relationship или приватностью;\n6. информационное состояние `Сейчас не принимает новых игроков` — без ложной кнопки.",
)
trainer_spec = trainer_spec.replace(
    "- `trainer.owner_edit_profile` — владельцу открыть настройки публичного профиля.",
    "- `trainer.owner_edit_profile` — владельцу открыть настройки публичного профиля;\n- `trainer.request_from_profile` — игроку отправить запрос тренеру.",
)
trainer_spec = trainer_spec.replace(
    "Может открыть тренировку, записаться или подать заявку уже на её details screen, написать тренеру при разрешённой приватности и перейти к связанным сущностям.",
    "Может отправить запрос тренеру, видеть `Запрос отправлен` или `Тренируется у`, открыть тренировку, записаться на её details screen и написать при разрешённом relationship-контексте.",
)
trainer_spec = trainer_spec.replace("- каталог `Клубы → Тренеры` → `trainer.public_profile`;", "- `Профиль → Найти тренера` → `trainer.public_profile`;")
trainer_spec = trainer_spec.replace("- back fallback: `/clubs?category=trainers`.", "- back fallback: `/trainers/search`.")
write("docs/screens/clubs/trainer-details.md", trainer_spec)

# Decision D-028 is replaced with the corrected approval flow.
decisions = read("docs/DECISIONS.md")
pattern = re.compile(r"## D-028 — .*?(?=\n## D-|\Z)", re.S)
replacement = """## D-028 — Игрок отправляет запрос, тренер добавляет игрока

Статус: принято.

Игрок может отправить pending-запрос одному или нескольким trainer actors. До обработки игрок видит `Запрос отправлен`. Trainer actor получает уведомление `Новый игрок`, а запрос также появляется в `Настройки → Мои игроки → Новые`.

Только явное действие тренера `Добавить` активирует связь, переносит игрока в основной список `Мои игроки` и показывает игроку `Тренируется у {trainer_name}`. `Отклонить` закрывает запрос. Открытие профиля или сообщение не принимают запрос автоматически. Источник истины: `docs/TRAINER_RELATIONSHIPS.yaml`.
"""
if not pattern.search(decisions):
    raise RuntimeError("D-028 block not found")
write("docs/DECISIONS.md", pattern.sub(replacement.rstrip(), decisions, count=1))

# Player directory integration reflects pending requests and acceptance.
player_directory = read("docs/PLAYER_DIRECTORY.yaml")
player_directory = re.sub(
    r"trainer_relationship_integration:\n(?:  .*\n)*",
    """trainer_relationship_integration:
  source_of_truth: docs/TRAINER_RELATIONSHIPS.yaml
  rules:
    - pending trainer request is separate from actor_player_links
    - pending request appears in trainer My Players > Новые
    - only trainer action Добавить creates or ensures actor_player_link with source trainer_accepted_request
    - accepted player moves to trainer saved My Players list
    - declining or cancelling a request does not create event participation
    - ending active trainer relationship does not silently delete event history
""",
    player_directory,
    count=1,
)
write("docs/PLAYER_DIRECTORY.yaml", player_directory)

# Data model gets explicit request and active relationship records.
data_model = read("docs/DATA_MODEL.md")
marker = "### Запрос игрока тренеру"
block = """### Запрос игрока тренеру

Источник истины: `docs/TRAINER_RELATIONSHIPS.yaml`.

- `trainer_relationship_requests` — player profile, trainer actor, status `pending / accepted / declined / cancelled`, timestamps and optional message;
- `player_trainer_relationships` — active or ended confirmed relationship created only after trainer acceptance;
- `trainer_relationship_events` — audit of request, message, accept, decline, cancel and end actions.

Pending-запрос не создаёт `actor_player_link`. После `Добавить` создаётся или восстанавливается `actor_player_link` trainer actor → player profile с source `trainer_accepted_request`, а запрос становится `accepted`.
"""
if marker not in data_model:
    needle = "## 5. Участие"
    if needle not in data_model:
        raise RuntimeError("DATA_MODEL participation heading not found")
    data_model = data_model.replace(needle, block.rstrip() + "\n\n" + needle, 1)
write("docs/DATA_MODEL.md", data_model)

# Settings screen mentions the New tab explicitly.
settings = read("docs/screens/profile/main.md")
settings = settings.replace(
    "Новые запросы игроков показываются на первой вкладке и в уведомлениях.",
    "Новые запросы игроков показываются в уведомлениях и в `Мои игроки → Новые`; только `Добавить` переносит игрока в основной список.",
)
write("docs/screens/profile/main.md", settings)

# README summary.
readme = read("README.md")
readme = re.sub(
    r"Связь с тренером .*?\n",
    "Связь с тренером подтверждает trainer actor: игрок видит `Запрос отправлен`, а после действия `Добавить` — `Тренируется у {имя}`. Pending-запросы находятся в уведомлениях и `Настройки → Мои игроки → Новые`. Поддерживается несколько тренеров. Источник истины — [`docs/TRAINER_RELATIONSHIPS.yaml`](docs/TRAINER_RELATIONSHIPS.yaml), поисковые области — [`docs/SEARCH_ARCHITECTURE.yaml`](docs/SEARCH_ARCHITECTURE.yaml).\n",
    readme,
    count=1,
)
write("README.md", readme)

# Cross-product flow and test scenario.
append_once(
    "docs/USER_FLOWS.md",
    "## 21. Игрок отправляет запрос тренеру",
    """## 21. Игрок отправляет запрос тренеру

```text
Профиль игрока → Без тренера → Найти тренера
→ Отправить запрос
→ игрок видит «Запрос отправлен»
→ тренер получает «Новый игрок»
→ Настройки тренера → Мои игроки → Новые
→ Добавить
→ игрок видит «Тренируется у {имя}»
→ игрок переносится в основной список Мои игроки тренера
```

`Отклонить` закрывает запрос. `Написать` и просмотр профиля не принимают его автоматически.
""",
)
append_once(
    "docs/TEST_SCENARIOS.md",
    "## A-14 — Запрос игрока тренеру",
    """## A-14 — Запрос игрока тренеру

1. Игрок без тренера открывает `Профиль → Без тренера → Найти тренера`.
2. Нажимает `Отправить запрос` и видит `Запрос отправлен`, но не `Тренируется у`.
3. Trainer actor получает одно уведомление `Новый игрок`; запрос появляется в `Мои игроки → Новые`.
4. Действие `Написать` не принимает запрос.
5. Тренер нажимает `Добавить`; запрос исчезает из `Новые`, игрок появляется в основном списке.
6. Игрок получает уведомление и видит `Тренируется у {trainer_name}`.
7. Повторная обработка на другом устройстве идемпотентна и не создаёт дубль.
""",
)

print("Trainer request approval migration completed.")
