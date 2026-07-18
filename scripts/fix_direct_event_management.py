#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
from typing import Any
import yaml

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"


def load(path: Path) -> dict[str, Any]:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(path)
    return value


def save(path: Path, value: dict[str, Any]) -> None:
    path.write_text(yaml.safe_dump(value, allow_unicode=True, sort_keys=False, width=110), encoding="utf-8")


def find(items: list[dict[str, Any]], key: str, value: str) -> dict[str, Any] | None:
    return next((item for item in items if str(item.get(key, "")) == value), None)


# My Players belongs to the Profile stack because it is opened from the compact connections rail.
routes_doc = load(DOCS / "ROUTES.yaml")
routes = routes_doc.get("routes", []) or []
route = find(routes, "path", "/profile/players")
if route:
    route["navigator"] = "home_stack"
    route["parent"] = "/"
    route["accepts_query"] = ["tab", "mode", "entityType", "entityId", "actorId"]
    route["back_fallback"] = "/"
save(DOCS / "ROUTES.yaml", routes_doc)

screens_doc = load(DOCS / "SCREENS.yaml")
screens = screens_doc.get("screens", []) or []
screen = find(screens, "id", "profile.players")
if screen:
    screen["section"] = "home"
    screen["purpose"] = "Сохранённые игроки active actor и новые запросы тренеру; открывается из компактной строки связей в Профиле."
    screen["back_fallback"] = "/"
save(DOCS / "SCREENS.yaml", screens_doc)

# Draft continuation is available only from management center, never from personal activity.
actions_doc = load(DOCS / "ACTIONS.yaml")
actions_doc["actions"] = [
    action for action in (actions_doc.get("actions", []) or [])
    if str(action.get("id", "")) != "my_games.continue_draft"
]
save(DOCS / "ACTIONS.yaml", actions_doc)

# Convert old row terminology to one horizontal card rail and remove the superseded switch reference.
connections = load(DOCS / "PROFILE_CONNECTIONS.yaml")
player = connections.get("player_variant", {}) or {}
if "rows" in player:
    player["cards"] = player.pop("rows")
connections["player_variant"] = player
trainer = connections.get("trainer_variant", {}) or {}
if "default_rows" in trainer:
    trainer["default_cards"] = trainer.pop("default_rows")
connections["trainer_variant"] = trainer
organization = connections.get("organization_variant", {}) or {}
if "default_rows" in organization:
    organization["default_cards"] = organization.pop("default_rows")
connections["organization_variant"] = organization
connections["rules"] = [
    rule for rule in (connections.get("rules", []) or [])
    if "Участвую / Управляю" not in str(rule)
    and "show all three rows" not in str(rule)
]
if "render one compact rail rather than three vertical home sections" not in connections["rules"]:
    connections["rules"].append("render one compact rail rather than three vertical home sections")
save(DOCS / "PROFILE_CONNECTIONS.yaml", connections)

# Update My Players spec ownership without changing its request/acceptance logic.
path = DOCS / "screens/profile/my-players.md"
text = path.read_text(encoding="utf-8")
text = text.replace("- Parent: `profile.main`", "- Parent: `home.main`")
text = text.replace("На экране активна вкладка `Настройки`", "На экране активна вкладка `Профиль`")
text = text.replace("Назад → Настройки", "Назад → Профиль")
if "## Место в Профиле" not in text:
    text = text.rstrip() + "\n\n## Место в Профиле\n\nЭкран открывается из компактной карточки `Игроки` в строке связей. Он не является управлением событиями: сохранение игрока не создаёт участие и не даёт доступ к закрытым данным.\n"
path.write_text(text, encoding="utf-8")

print("Remaining direct management references fixed.")
