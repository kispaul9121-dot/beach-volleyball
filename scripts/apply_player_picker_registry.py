from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def write(path: str, content: str) -> None:
    (ROOT / path).write_text(content, encoding="utf-8")


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: expected one match, found {count}")
    return text.replace(old, new, 1)


def update_screens() -> None:
    path = "docs/SCREENS.yaml"
    text = read(path)

    if "  - player.picker\n" not in text:
        text = replace_once(
            text,
            "global_overlays:\n  - actor.switcher\n",
            "global_overlays:\n  - actor.switcher\n  - player.picker\n",
            "register player picker overlay",
        )

    screen_block = """  - id: player.picker
    title: Добавить игроков
    route: system://player-picker
    section: global
    spec: docs/screens/shared/player-picker.md
    purpose: Множественный выбор и приглашение игроков в конкретное событие.
    variants: [create_context, manage_context]
    permission: entity_inviter
    back_fallback: system://dismiss

"""
    marker = "  - id: global.notifications\n"
    if "  - id: player.picker\n" not in text:
        text = replace_once(text, marker, screen_block + marker, "insert player picker screen")

    write(path, text)


def update_routes() -> None:
    path = "docs/ROUTES.yaml"
    text = read(path)

    route_block = """  - path: system://player-picker
    screen: player.picker
    navigator: modal_stack
    access: authenticated
    permission: entity_inviter
    accepts_query: [entityType, entityId, draftId, actorId, returnTo]
    back_fallback: system://dismiss

"""
    marker = "  # Bottom tabs\n"
    if "  - path: system://player-picker\n" not in text:
        text = replace_once(text, marker, route_block + marker, "insert player picker route")

    write(path, text)


def update_actions() -> None:
    path = "docs/ACTIONS.yaml"
    text = read(path)

    text = text.replace(
        "    destination: system.player_picker\n",
        "    destination: player.picker\n",
        1,
    )
    text = text.replace(
        "    source: system.player_picker\n    destination: system.create_event_invitations\n",
        "    source: player.picker\n    destination: system.create_event_invitations\n",
        1,
    )
    text = text.replace(
        "    source: system.player_picker\n    destination: system.add_confirmed_participant_with_audit\n",
        "    source: player.picker\n    destination: system.add_confirmed_participant_with_audit\n",
        1,
    )

    picker_actions = """  - id: players.close_picker
    label: Закрыть выбор игроков
    source: player.picker
    destination: system.dismiss_modal
    permission: entity_inviter

  - id: players.picker_change_source
    label: Мои игроки / Недавние / Поиск
    source: player.picker
    destination: system.local_filter
    permission: entity_inviter

  - id: players.picker_toggle_player
    label: Выбрать игрока
    source: player.picker
    destination: system.local_state
    permission: entity_inviter

  - id: players.picker_search
    label: Поиск игроков
    source: player.picker
    destination: system.local_search
    permission: entity_inviter

"""
    marker = "  - id: players.send_invitations\n"
    if "  - id: players.close_picker\n" not in text:
        text = replace_once(text, marker, picker_actions + marker, "insert player picker actions")

    write(path, text)


def update_directory() -> None:
    path = "docs/PLAYER_DIRECTORY.yaml"
    text = read(path)

    if "  screen_id: player.picker\n" not in text:
        text = replace_once(
            text,
            "player_picker:\n  presentation: full_screen_modal_or_bottom_sheet\n",
            "player_picker:\n  screen_id: player.picker\n  route: system://player-picker\n  presentation: full_screen_modal\n  hide_global_bottom_tabs: true\n  return_to_required: true\n",
            "register picker contract",
        )

    if "    - Глобальная нижняя навигация скрыта только внутри picker." not in text:
        text = replace_once(
            text,
            "  rules:\n    - Один picker используется для игры, тренировки, турнира, сезона и тура.\n",
            "  rules:\n    - Один picker используется для игры, тренировки, турнира, сезона и тура.\n    - Глобальная нижняя навигация скрыта только внутри picker.\n    - Picker нельзя открыть без entity или draft context и returnTo.\n",
            "add picker navigation rules",
        )

    write(path, text)


def update_agents() -> None:
    path = "AGENTS.md"
    text = read(path)

    new_rules = (
        "- `Профиль → Мои игроки` является profile stack-экраном: глобальное нижнее меню сохраняется, активна вкладка `Профиль`.\n"
        "- `player.picker` является отдельным full-screen modal из конкретного события: нижнее меню скрыто, обязательны entity/draft context и `returnTo`.\n"
    )
    marker = "- Для выбора людей во всех сущностях использовать один player picker: `Мои игроки · Недавние · Поиск`.\n"
    if "- `player.picker` является отдельным full-screen modal" not in text:
        text = replace_once(text, marker, marker + new_rules, "add player navigation rules")

    write(path, text)


def update_decisions() -> None:
    path = "docs/DECISIONS.md"
    text = read(path)

    decision = """

## D-024 — «Мои игроки» и Player Picker являются разными экранами

Статус: принято.

`Профиль → Мои игроки` использует маршрут `/profile/players`, остаётся внутри profile stack и сохраняет глобальное нижнее меню `Главная · События · Чаты · Клубы · Профиль` с активной вкладкой `Профиль`.

`player.picker` открывается только из создания или управления конкретным событием как `system://player-picker`. Это полноэкранный modal без нижней навигации, с обязательным контекстом entity или draft и `returnTo`.

Обычный экран `Мои игроки` не показывает постоянную кнопку `Отправить приглашения`; множественный выбор и отправка приглашений относятся к picker. Источники истины: `docs/PLAYER_DIRECTORY.yaml`, `docs/screens/profile/my-players.md`, `docs/screens/shared/player-picker.md`.
"""
    if "## D-024 — «Мои игроки» и Player Picker являются разными экранами" not in text:
        text = text.rstrip() + decision + "\n"

    write(path, text)


def update_tests() -> None:
    path = "docs/TEST_SCENARIOS.md"
    text = read(path)

    text = text.replace(
        "4. Приглашает друзей.\n\nОжидание: не требуются данные компании; интерфейс не обещает коммерческий пакет; участники присоединяются к группе.",
        "4. Открывает `Добавить игроков`, выбирает людей из `Мои игроки` и отправляет приглашения.\n\nОжидание: не требуются данные компании; интерфейс не обещает коммерческий пакет; приглашения относятся к туру, а отдельная социальная группа не создаётся.",
        1,
    )

    old = """## A-13 — Тренировочная группа

1. Тренер создаёт группу.
2. Приглашает участников.
3. Создаёт занятие из группы.
4. Отмечает посещаемость.
5. Применяется абонемент.

Ожидание: группа и занятие — разные сущности; статистика обновляется, история сохраняется.
"""
    new = """## A-13 — Тренер приглашает игроков в тренировку

1. Активен trainer actor.
2. Тренер создаёт тренировку и задаёт вместимость 8 мест.
3. Нажимает `Добавить игроков` и открывает `player.picker` без глобального нижнего меню.
4. Выбирает трёх игроков из `Мои игроки` и одного из `Недавние`.
5. Отправляет приглашения и возвращается на тот же шаг создания.
6. Публикует тренировку в режиме `Сначала приглашения, потом публично`.
7. Два игрока подтверждают участие; для платного события получают `payment_required`.
8. Тренер открывает оставшиеся места в `События → Все`.
9. Подтверждённые игроки получают доступ к чату тренировки.

Ожидание: `Мои игроки` остаётся profile stack-экраном с глобальным меню; picker является отдельным modal; выбор не создаёт участие до отправки; приглашённые не видят чат до подтверждения; постоянная тренировочная группа не создаётся.
"""
    if old not in text:
        raise RuntimeError("replace A-13: legacy scenario not found")
    text = text.replace(old, new, 1)

    write(path, text)


def main() -> None:
    update_screens()
    update_routes()
    update_actions()
    update_directory()
    update_agents()
    update_decisions()
    update_tests()
    print("Player picker registry migration applied")


if __name__ == "__main__":
    main()
