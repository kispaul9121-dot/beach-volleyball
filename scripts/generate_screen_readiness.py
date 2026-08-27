#!/usr/bin/env python3
"""Generate the VolleyPlay screen-readiness audit.

The audit inspects every screen registered in docs/SCREENS.yaml against the
ten criteria documented in docs/SCREEN_READINESS.md. It cross-checks routes,
actions and the referenced Markdown specification.

Usage:
    python scripts/generate_screen_readiness.py
    python scripts/generate_screen_readiness.py --check
"""

from __future__ import annotations

import argparse
import re
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

import yaml

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
OUTPUT_MD = DOCS / "SCREEN_READINESS.md"
OUTPUT_YAML = DOCS / "SCREEN_READINESS.yaml"

READY = "ready"
PARTIAL = "partial"
MISSING = "missing"
NA = "na"

ICONS = {READY: "✅", PARTIAL: "◐", MISSING: "○", NA: "—"}

CRITERIA = [
    ("identity_route", "ID и маршрут"),
    ("actors_permissions", "Профили и права"),
    ("purpose_data", "Назначение и данные"),
    ("blocks", "Блоки"),
    ("actions", "Действия"),
    ("states", "Состояния"),
    ("role_variants", "Варианты ролей"),
    ("navigation", "Навигация"),
    ("integrations", "Интеграции"),
    ("spec", "Спецификация"),
]

ROLE_WORDS = {
    "player": ("игрок", "player"),
    "trainer": ("тренер", "trainer"),
    "organization": ("организац", "organization", "клуб"),
    "guest": ("гость", "guest"),
    "participant": ("участник", "participant"),
    "organizer": ("организатор", "organizer"),
    "manager": ("менеджер", "manager", "управля"),
}

INTEGRATION_WORDS = {
    "chat": ("чат", "chat"),
    "notifications": ("уведомлен", "notification"),
    "calendar": ("календар", "calendar"),
    "payments": ("оплат", "платёж", "payment", "refund", "возврат"),
    "maps": ("карта", "геолокац", "location", "адрес"),
    "audit": ("аудит", "audit"),
    "deep_link": ("deep link", "deeplink", "returnto"),
}


@dataclass(frozen=True)
class CriterionResult:
    status: str
    evidence: str


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a YAML mapping")
    return data


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower()).strip()


def contains_any(text: str, needles: Iterable[str]) -> bool:
    lowered = text.lower()
    return any(needle.lower() in lowered for needle in needles)


def markdown_headings(text: str) -> list[str]:
    return [match.group(1).strip() for match in re.finditer(r"(?m)^#{1,6}\s+(.+?)\s*$", text)]


def bullet_count(text: str) -> int:
    return len(re.findall(r"(?m)^\s*(?:[-*+]|\d+[.)])\s+\S", text))


def nonempty_line_count(text: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip())


def matched_categories(text: str, mapping: dict[str, tuple[str, ...]]) -> list[str]:
    lowered = text.lower()
    return sorted(key for key, words in mapping.items() if any(word in lowered for word in words))


def score_statuses(results: dict[str, CriterionResult]) -> tuple[int, str]:
    applicable = [result.status for result in results.values() if result.status != NA]
    if not applicable:
        return 0, "не оценено"
    points = sum(1.0 if status == READY else 0.5 if status == PARTIAL else 0.0 for status in applicable)
    percent = round(points / len(applicable) * 100)
    has_missing = MISSING in applicable
    if percent >= 85 and not has_missing:
        label = "готово"
    elif percent >= 60:
        label = "частично"
    else:
        label = "слабо"
    return percent, label


def route_result(screen: dict[str, Any], routes: list[dict[str, Any]]) -> CriterionResult:
    screen_id = str(screen.get("id", ""))
    declared = str(screen.get("route", ""))
    matches = [route for route in routes if str(route.get("screen", "")) == screen_id]
    if declared and any(str(route.get("path", "")) == declared for route in matches):
        return CriterionResult(READY, "ID, route и запись ROUTES.yaml совпадают.")
    if declared or matches:
        return CriterionResult(PARTIAL, "ID или route есть, но реестры не полностью совпадают.")
    return CriterionResult(MISSING, "Нет route или записи в ROUTES.yaml.")


def actors_result(screen: dict[str, Any], route: dict[str, Any] | None, spec_text: str) -> CriterionResult:
    variants = [str(value) for value in (screen.get("variants") or [])]
    permission = screen.get("permission") or (route or {}).get("permission")
    access = (route or {}).get("access")
    roles = matched_categories(spec_text, ROLE_WORDS)
    section = str(screen.get("section", ""))
    actor_sensitive = section in {"home", "play", "chats", "clubs", "profile", "shared"}

    if variants or permission:
        detail = []
        if variants:
            detail.append(f"variants={', '.join(variants)}")
        if permission:
            detail.append(f"permission={permission}")
        return CriterionResult(READY, "; ".join(detail) + ".")
    if not actor_sensitive and access:
        return CriterionResult(READY, f"Доступ ограничен через route access={access}.")
    if access or roles:
        evidence = []
        if access:
            evidence.append(f"route access={access}")
        if roles:
            evidence.append("роли упомянуты в spec: " + ", ".join(roles))
        return CriterionResult(PARTIAL, "; ".join(evidence) + ", но actor-правила не формализованы.")
    return CriterionResult(MISSING, "Не определены actor variants, permission или правила доступа.")


def purpose_data_result(screen: dict[str, Any], spec_text: str) -> CriterionResult:
    purpose = str(screen.get("purpose", "")).strip()
    data_evidence = contains_any(
        spec_text,
        (
            "источник данных", "source of truth", "данные", "модель", "таблиц", "yaml", "api",
            "получает", "загружает", "repository",
        ),
    )
    if purpose and data_evidence:
        return CriterionResult(READY, "Purpose задан; в spec есть источник или модель данных.")
    if purpose:
        return CriterionResult(PARTIAL, "Purpose задан, но источник данных описан неявно.")
    if data_evidence:
        return CriterionResult(PARTIAL, "Данные упомянуты, но purpose отсутствует в SCREENS.yaml.")
    return CriterionResult(MISSING, "Нет purpose и явного источника данных.")


def blocks_result(spec_text: str) -> CriterionResult:
    headings = [normalize(value) for value in markdown_headings(spec_text)]
    structure_heading = any(
        contains_any(
            heading,
            ("блок", "раздел", "структур", "содерж", "шаг", "карточ", "дашборд", "поля", "состав", "экран", "вкладк"),
        )
        for heading in headings
    )
    bullets = bullet_count(spec_text)
    if structure_heading and bullets >= 4:
        return CriterionResult(READY, f"Есть структурный раздел и {bullets} пунктов.")
    if structure_heading or bullets >= 4:
        return CriterionResult(PARTIAL, f"Структура описана частично; пунктов: {bullets}.")
    return CriterionResult(MISSING, "Не найдена явная структура блоков экрана.")


def actions_result(screen_id: str, actions: list[dict[str, Any]], spec_text: str) -> CriterionResult:
    outgoing = [str(action.get("id", "")) for action in actions if str(action.get("source", "")) == screen_id]
    action_words = contains_any(
        spec_text,
        (
            "действи", "кнопк", "нажим", "открыть", "создать", "добавить", "принять", "отклонить",
            "оплатить", "управлять", "сохранить", "удалить", "отправить",
        ),
    )
    if outgoing and action_words:
        preview = ", ".join(outgoing[:4])
        suffix = "…" if len(outgoing) > 4 else ""
        return CriterionResult(READY, f"ACTIONS.yaml: {preview}{suffix}; действия описаны в spec.")
    if outgoing:
        return CriterionResult(PARTIAL, f"Есть {len(outgoing)} action(s), но UX-действия в spec описаны слабо.")
    if action_words:
        return CriterionResult(PARTIAL, "Действия описаны в spec, но не привязаны к ACTIONS.yaml.")
    return CriterionResult(MISSING, "Нет исходящих actions и описания кнопок.")


def states_result(spec_text: str) -> CriterionResult:
    state_groups = {
        "loading": ("loading", "загруз"),
        "empty": ("empty", "пуст"),
        "error": ("error", "ошиб"),
        "offline": ("offline", "офлайн"),
        "permission": ("permission denied", "нет доступа", "доступ запрещ", "недостаточно прав"),
    }
    found = [name for name, words in state_groups.items() if contains_any(spec_text, words)]
    if len(found) >= 4:
        return CriterionResult(READY, "Описаны состояния: " + ", ".join(found) + ".")
    if found:
        return CriterionResult(PARTIAL, "Описана только часть состояний: " + ", ".join(found) + ".")
    return CriterionResult(MISSING, "Нет loading, empty, error, offline и permission states.")


def role_variants_result(screen: dict[str, Any], spec_text: str) -> CriterionResult:
    screen_id = str(screen.get("id", ""))
    section = str(screen.get("section", ""))
    not_applicable = section in {"auth", "onboarding"} or screen_id in {"actor.switcher", "global.notifications", "player.picker"}
    if not_applicable:
        return CriterionResult(NA, "Различия участника и организатора для этого экрана не применяются.")

    variants = [str(value) for value in (screen.get("variants") or [])]
    roles = matched_categories(spec_text, ROLE_WORDS)
    if len(variants) >= 2 or len(roles) >= 3:
        evidence = "variants=" + ", ".join(variants) if len(variants) >= 2 else "роли в spec=" + ", ".join(roles)
        return CriterionResult(READY, evidence + ".")
    if variants or roles:
        evidence = "variants=" + ", ".join(variants) if variants else "роли в spec=" + ", ".join(roles)
        return CriterionResult(PARTIAL, evidence + "; различия описаны не полностью.")
    return CriterionResult(MISSING, "Не описаны различия участника, организатора и других ролей.")


def navigation_result(screen: dict[str, Any], route: dict[str, Any] | None, spec_text: str) -> CriterionResult:
    navigator = str((route or {}).get("navigator", ""))
    path = str((route or {}).get("path", screen.get("route", "")))
    root = navigator == "tab" or path in {"/", "/auth"}
    fallback = (route or {}).get("back_fallback") or screen.get("back_fallback")
    route_ok = root or bool(fallback)
    spec_ok = contains_any(spec_text, ("deep link", "deeplink", "returnto", "назад", "back_fallback", "возврат"))
    if route_ok and (spec_ok or root):
        return CriterionResult(READY, "Route определяет вход/возврат; deep-link поведение описано или экран корневой.")
    if route_ok or spec_ok:
        return CriterionResult(PARTIAL, "Навигация определена только в реестре или только в spec.")
    return CriterionResult(MISSING, "Не определены возврат назад и deep-link поведение.")


def integrations_result(screen: dict[str, Any], spec_text: str) -> CriterionResult:
    screen_id = str(screen.get("id", ""))
    section = str(screen.get("section", ""))
    if section == "auth" and screen_id != "auth.verify_email":
        return CriterionResult(NA, "Событийные интеграции для базовой auth-формы не обязательны.")

    categories = matched_categories(spec_text, INTEGRATION_WORDS)
    if len(categories) >= 2:
        return CriterionResult(READY, "Связи: " + ", ".join(categories) + ".")
    if categories:
        return CriterionResult(PARTIAL, "Указана одна связь: " + ", ".join(categories) + ".")
    return CriterionResult(MISSING, "Не описаны связи с чатами, уведомлениями, календарём или оплатами.")


def spec_result(spec_path: Path | None, spec_text: str) -> CriterionResult:
    if spec_path is None or not spec_path.is_file():
        return CriterionResult(MISSING, "Файл спецификации отсутствует.")
    lines = nonempty_line_count(spec_text)
    headings = len(markdown_headings(spec_text))
    if lines >= 35 and headings >= 4:
        return CriterionResult(READY, f"Spec существует: {lines} непустых строк, {headings} заголовков.")
    if lines >= 10 and headings >= 1:
        return CriterionResult(PARTIAL, f"Spec существует, но краткий: {lines} строк, {headings} заголовков.")
    return CriterionResult(MISSING, f"Spec формально существует, но почти пуст: {lines} строк, {headings} заголовков.")


def evaluate_screen(screen: dict[str, Any], routes: list[dict[str, Any]], actions: list[dict[str, Any]]) -> dict[str, Any]:
    screen_id = str(screen.get("id", ""))
    route_matches = [route for route in routes if str(route.get("screen", "")) == screen_id]
    route = route_matches[0] if route_matches else None

    spec_value = screen.get("spec")
    spec_path = ROOT / str(spec_value) if spec_value else None
    spec_text = spec_path.read_text(encoding="utf-8") if spec_path is not None and spec_path.is_file() else ""

    results = {
        "identity_route": route_result(screen, routes),
        "actors_permissions": actors_result(screen, route, spec_text),
        "purpose_data": purpose_data_result(screen, spec_text),
        "blocks": blocks_result(spec_text),
        "actions": actions_result(screen_id, actions, spec_text),
        "states": states_result(spec_text),
        "role_variants": role_variants_result(screen, spec_text),
        "navigation": navigation_result(screen, route, spec_text),
        "integrations": integrations_result(screen, spec_text),
        "spec": spec_result(spec_path, spec_text),
    }
    percent, label = score_statuses(results)
    return {
        "id": screen_id,
        "title": str(screen.get("title", "")),
        "section": str(screen.get("section", "")),
        "route": str(screen.get("route", "")),
        "spec": str(spec_value or ""),
        "score": percent,
        "status": label,
        "criteria": {key: {"status": value.status, "evidence": value.evidence} for key, value in results.items()},
    }


def build_yaml(audit: list[dict[str, Any]]) -> str:
    criterion_summary: dict[str, Counter[str]] = {key: Counter() for key, _ in CRITERIA}
    for item in audit:
        for key, result in item["criteria"].items():
            criterion_summary[key][result["status"]] += 1

    payload = {
        "version": 1,
        "method": "evidence_based_automatic_audit",
        "source_files": ["docs/SCREENS.yaml", "docs/ROUTES.yaml", "docs/ACTIONS.yaml", "docs/screens/**/*.md"],
        "status_values": {
            READY: "полностью подтверждено источниками",
            PARTIAL: "есть часть необходимых свидетельств",
            MISSING: "свидетельства отсутствуют",
            NA: "критерий не применяется",
        },
        "criteria": [{"id": key, "name": name} for key, name in CRITERIA],
        "summary": {
            "screens": len(audit),
            "ready": sum(1 for item in audit if item["status"] == "готово"),
            "partial": sum(1 for item in audit if item["status"] == "частично"),
            "weak": sum(1 for item in audit if item["status"] == "слабо"),
            "average_score": round(sum(item["score"] for item in audit) / len(audit)) if audit else 0,
            "by_criterion": {key: dict(counter) for key, counter in criterion_summary.items()},
        },
        "screens": audit,
    }
    return yaml.safe_dump(payload, allow_unicode=True, sort_keys=False, width=120)


def build_markdown(audit: list[dict[str, Any]]) -> str:
    ready_count = sum(1 for item in audit if item["status"] == "готово")
    partial_count = sum(1 for item in audit if item["status"] == "частично")
    weak_count = sum(1 for item in audit if item["status"] == "слабо")
    average = round(sum(item["score"] for item in audit) / len(audit)) if audit else 0

    lines = [
        "# Готовность экранов VolleyPlay",
        "",
        "Таблица автоматически проверяет каждый экран из `SCREENS.yaml` по десяти архитектурным критериям и сверяет `ROUTES.yaml`, `ACTIONS.yaml` и соответствующий файл в `docs/screens/`.",
        "",
        "> Это аудит полноты документации, а не доказательство UX-удобства. UX подтверждается только прототипом и тестированием с пользователями.",
        "",
        "## Итог",
        "",
        f"- Экранов проверено: **{len(audit)}**.",
        f"- Средняя архитектурная готовность: **{average}%**.",
        f"- Готово: **{ready_count}**.",
        f"- Частично: **{partial_count}**.",
        f"- Слабо описано: **{weak_count}**.",
        "",
        "## Десять критериев",
        "",
    ]
    for index, (_, name) in enumerate(CRITERIA, start=1):
        lines.append(f"{index}. **{name}**.")
    lines.extend([
        "",
        "Обозначения: `✅` — подтверждено; `◐` — частично; `○` — отсутствует; `—` — не применяется.",
        "",
        "## Матрица",
        "",
        "| Экран | Route | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | Итог |",
        "|---|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|---:|",
    ])

    for item in audit:
        icons = [ICONS[item["criteria"][key]["status"]] for key, _ in CRITERIA]
        title = item["title"].replace("|", "\\|")
        screen_id = item["id"].replace("|", "\\|")
        route = item["route"].replace("|", "\\|")
        lines.append(
            f"| **{title}**<br><code>{screen_id}</code> | <code>{route}</code> | "
            + " | ".join(icons)
            + f" | **{item['score']}% · {item['status']}** |"
        )

    lines.extend([
        "",
        "## Сводка по критериям",
        "",
        "| № | Критерий | ✅ | ◐ | ○ | — |",
        "|---:|---|---:|---:|---:|---:|",
    ])
    for index, (key, name) in enumerate(CRITERIA, start=1):
        counts = Counter(item["criteria"][key]["status"] for item in audit)
        lines.append(f"| {index} | {name} | {counts[READY]} | {counts[PARTIAL]} | {counts[MISSING]} | {counts[NA]} |")

    weakest = sorted(audit, key=lambda item: (item["score"], item["section"], item["id"]))[:15]
    lines.extend([
        "",
        "## Первые экраны на доработку",
        "",
        "Ниже показаны экраны с наименьшей подтверждённой готовностью; причины берутся непосредственно из результатов проверки.",
        "",
    ])
    for item in weakest:
        missing_names = [name for key, name in CRITERIA if item["criteria"][key]["status"] == MISSING]
        partial_names = [name for key, name in CRITERIA if item["criteria"][key]["status"] == PARTIAL]
        details = []
        if missing_names:
            details.append("нет: " + ", ".join(missing_names))
        if partial_names:
            details.append("частично: " + ", ".join(partial_names))
        lines.append(
            f"- **{item['title']}** (`{item['id']}`, {item['score']}%): "
            + ("; ".join(details) if details else "нет критических пробелов")
            + "."
        )

    lines.extend([
        "",
        "## Как обновлять",
        "",
        "После изменения `SCREENS.yaml`, `ROUTES.yaml`, `ACTIONS.yaml` или файлов `docs/screens/` запусти:",
        "",
        "```bash",
        "python scripts/generate_screen_readiness.py",
        "```",
        "",
        "CI запускает команду с `--check` и сообщает, когда таблица устарела.",
        "",
        "Машиночитаемые результаты и объяснение каждой оценки находятся в `docs/SCREEN_READINESS.yaml`.",
        "",
    ])
    return "\n".join(lines)


def compare_or_write(path: Path, expected: str, check: bool) -> bool:
    current = path.read_text(encoding="utf-8") if path.exists() else None
    if current == expected:
        return True
    if check:
        print(f"{path.relative_to(ROOT)} is stale. Run scripts/generate_screen_readiness.py")
        return False
    path.write_text(expected, encoding="utf-8")
    print(f"Wrote {path.relative_to(ROOT)}")
    return True


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="Fail when generated readiness files are missing or stale.")
    args = parser.parse_args()

    screens_doc = load_yaml(DOCS / "SCREENS.yaml")
    routes_doc = load_yaml(DOCS / "ROUTES.yaml")
    actions_doc = load_yaml(DOCS / "ACTIONS.yaml")

    screens = screens_doc.get("screens", [])
    routes = routes_doc.get("routes", [])
    actions = actions_doc.get("actions", [])
    if not isinstance(screens, list) or not isinstance(routes, list) or not isinstance(actions, list):
        raise ValueError("screens, routes and actions must be YAML lists")

    audit = [evaluate_screen(screen, routes, actions) for screen in screens if isinstance(screen, dict)]

    md = build_markdown(audit)
    yaml_text = build_yaml(audit)

    ok_md = compare_or_write(OUTPUT_MD, md, args.check)
    ok_yaml = compare_or_write(OUTPUT_YAML, yaml_text, args.check)
    if not (ok_md and ok_yaml):
        return 1

    average = round(sum(item["score"] for item in audit) / len(audit)) if audit else 0
    print(f"Screen readiness audit: {len(audit)} screens, average {average}%")
    return 0


if __name__ == "__main__":
    sys.exit(main())
