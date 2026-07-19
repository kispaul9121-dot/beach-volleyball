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


def replace_scalar(value: Any) -> Any:
    if isinstance(value, str):
        replacements = {
            "&manageTab=active": "",
            "manageTab=active&": "",
            "?manageTab=active": "",
            "/play?mode=manage&category=games&manageTab=active": "/play?mode=manage&category=games",
            "/play?mode=manage&category=trainings&manageTab=active": "/play?mode=manage&category=trainings",
            "/play?mode=manage&category=tournaments&manageTab=active": "/play?mode=manage&category=tournaments",
            "/camps?mode=manage&manageTab=active": "/camps?mode=manage",
        }
        for old, new in replacements.items():
            value = value.replace(old, new)
        return value
    if isinstance(value, list):
        return [replace_scalar(item) for item in value]
    if isinstance(value, dict):
        return {key: replace_scalar(item) for key, item in value.items()}
    return value


def migrate_routes() -> None:
    path = DOCS / "ROUTES.yaml"
    doc = load_yaml(path)
    doc["version"] = max(int(doc.get("version", 0) or 0), 4)
    routes = doc.get("routes", []) or []
    for route in routes:
        if not isinstance(route, dict):
            continue
        if route.get("path") in {"/play", "/camps"}:
            route["accepts_query"] = [
                item for item in (route.get("accepts_query", []) or []) if item != "manageTab"
            ]
    save_yaml(path, replace_scalar(doc))


def migrate_actions() -> None:
    path = DOCS / "ACTIONS.yaml"
    doc = load_yaml(path)
    doc["version"] = max(int(doc.get("version", 0) or 0), 4)
    obsolete = {"games.change_management_tab", "camps.change_management_tab"}
    doc["actions"] = [
        action
        for action in (doc.get("actions", []) or [])
        if not isinstance(action, dict) or str(action.get("id", "")) not in obsolete
    ]
    save_yaml(path, replace_scalar(doc))


def update_decision_log() -> None:
    path = DOCS / "DECISIONS.md"
    text = path.read_text(encoding="utf-8")
    marker = "## D-034 — Завершённые управляемые события относятся к архиву"
    if marker not in text:
        text = text.rstrip() + "\n\n" + marker + "\n\n"
        text += "Статус: принято частично; расположение архива отложено.\n\n"
        text += (
            "В режимах управления разделов `Игры` и `Кэмпы` нет временных вкладок "
            "`Активные` и `Завершённые`. Экран сразу показывает единый список текущих "
            "управляемых сущностей. Завершённые игры, тренировки, турниры и кэмпы "
            "перемещаются в архив без удаления данных. Место архива, маршрут и кнопка "
            "входа имеют статус `placement_pending` и будут утверждены отдельно.\n"
        )
        path.write_text(text, encoding="utf-8")


def remove_stale_markdown_contracts() -> None:
    replacements = {
        "вкладки `Активные · Завершённые`": "единый текущий список без временных вкладок",
        "`Активные · Завершённые`": "единый текущий список; завершённые относятся к архиву",
        "manageTab=active&": "",
        "&manageTab=active": "",
    }
    for path in DOCS.rglob("*.md"):
        if path.name in {"SCREEN_READINESS.md"}:
            continue
        text = path.read_text(encoding="utf-8")
        updated = text
        for old, new in replacements.items():
            updated = updated.replace(old, new)
        if updated != text:
            path.write_text(updated, encoding="utf-8")


def main() -> None:
    migrate_routes()
    migrate_actions()
    update_decision_log()
    remove_stale_markdown_contracts()


if __name__ == "__main__":
    main()
