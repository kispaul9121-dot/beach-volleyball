#!/usr/bin/env python3
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"


def load(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        value = yaml.safe_load(handle)
    if not isinstance(value, dict):
        raise ValueError(path)
    return value


def save(path: Path, value: dict[str, Any]) -> None:
    path.write_text(yaml.safe_dump(value, allow_unicode=True, sort_keys=False, width=1000), encoding="utf-8")


def find(items: list[dict[str, Any]], key: str, value: str) -> dict[str, Any]:
    for item in items:
        if str(item.get(key, "")) == value:
            return item
    raise KeyError(f"Missing {key}={value}")


def main() -> None:
    screens_doc = load(DOCS / "SCREENS.yaml")
    screens = screens_doc.get("screens", [])

    activity_screens = {
        "profile.calendar": "/",
        "profile.my_games": "/",
        "profile.competitions": "/",
        "profile.trainings": "/",
        "profile.trips": "/",
    }
    for screen_id, fallback in activity_screens.items():
        screen = find(screens, "id", screen_id)
        screen["section"] = "home"
        screen["back_fallback"] = fallback

    screen_fallbacks = {
        "game.create": "/profile/games?mode=managing&tab=active",
        "game.manage": "/profile/games?mode=managing&tab=active",
        "training.create": "/profile/trainings?mode=managing&tab=active",
        "training.manage": "/profile/trainings?mode=managing&tab=active",
        "tournament.create": "/profile/competitions?mode=managing&tab=active",
        "tournament.manage": "/profile/competitions?mode=managing&tab=active",
        "tour.create": "/profile/trips?mode=managing&tab=active",
        "tour.manage": "/profile/trips?mode=managing&tab=active",
    }
    for screen_id, fallback in screen_fallbacks.items():
        find(screens, "id", screen_id)["back_fallback"] = fallback
    save(DOCS / "SCREENS.yaml", screens_doc)

    routes_doc = load(DOCS / "ROUTES.yaml")
    routes = routes_doc.get("routes", [])
    for path in (
        "/profile/calendar",
        "/profile/games",
        "/profile/competitions",
        "/profile/trainings",
        "/profile/trips",
    ):
        route = find(routes, "path", path)
        route["navigator"] = "home_stack"
        route["parent"] = "/"
        route["back_fallback"] = "/"

    route_fallbacks = {
        "/games/create": "/profile/games?mode=managing&tab=active",
        "/games/:gameId/manage": "/profile/games?mode=managing&tab=active",
        "/trainings/create": "/profile/trainings?mode=managing&tab=active",
        "/trainings/:trainingId/manage": "/profile/trainings?mode=managing&tab=active",
        "/tournaments/create": "/profile/competitions?mode=managing&tab=active",
        "/tournaments/:tournamentId/manage": "/profile/competitions?mode=managing&tab=active",
        "/tours/create": "/profile/trips?mode=managing&tab=active",
        "/tours/:tourId/manage": "/profile/trips?mode=managing&tab=active",
    }
    for path, fallback in route_fallbacks.items():
        find(routes, "path", path)["back_fallback"] = fallback
    save(DOCS / "ROUTES.yaml", routes_doc)

    calendar_path = DOCS / "screens/profile/my-calendar.md"
    calendar = calendar_path.read_text(encoding="utf-8")
    calendar = calendar.replace("- Parent: `profile.main`", "- Parent: `home.main`")
    calendar = calendar.replace("Назад → Настройки. При deep link fallback `/profile`.", "Назад → Профиль. При deep link fallback `/`.")
    calendar_path.write_text(calendar, encoding="utf-8")


if __name__ == "__main__":
    main()
