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
        raise RuntimeError(f"{label}: expected exactly one match, found {count}")
    return text.replace(old, new, 1)


def regex_replace_once(text: str, pattern: str, replacement: str, label: str) -> str:
    updated, count = re.subn(pattern, replacement, text, count=1, flags=re.MULTILINE | re.DOTALL)
    if count != 1:
        raise RuntimeError(f"{label}: expected exactly one match, found {count}")
    return updated


def update_screens() -> None:
    path = "docs/SCREENS.yaml"
    text = read(path)

    text = replace_once(
        text,
        "  - id: play.main\n    title: Играть\n",
        "  - id: play.main\n    title: События\n",
        "rename Play tab",
    )
    text = replace_once(
        text,
        "    purpose: Публичный каталог плюс быстрый доступ к сущностям активного профиля.\n",
        "    purpose: Каталог, участия и управление событиями через вкладки Все, Участвую и Управляю.\n",
        "update Play purpose",
    )
    text = replace_once(
        text,
        "    purpose: Чаты событий, групп, клубов, туров и личные сообщения.\n",
        "    purpose: Чаты игр, тренировок, турниров, сезонов, клубов, туров и личные сообщения.\n",
        "remove social groups from chat purpose",
    )
    text = replace_once(
        text,
        "    purpose: Записи игрока, занятия и группы тренера или организации.\n",
        "    purpose: Записи игрока и управляемые тренировки тренера или организации.\n",
        "remove groups from profile trainings purpose",
    )

    players_screen = """  - id: profile.players
    title: Мои игроки
    route: /profile/players
    section: profile
    spec: docs/screens/profile/my-players.md
    purpose: Односторонний список игроков активного профиля и быстрый выбор для приглашений.
    variants: [player, trainer, organization]
    back_fallback: /profile

"""
    marker = "  - id: profile.trips\n"
    if "  - id: profile.players\n" not in text:
        text = replace_once(text, marker, players_screen + marker, "insert profile.players screen")

    text = replace_once(
        text,
        "    purpose: Создание разовой тренировки или занятия группы.\n",
        "    purpose: Создание тренировки, приглашение игроков и настройка публичности.\n",
        "update training create purpose",
    )

    if "  - id: training.group\n" in text:
        text = regex_replace_once(
            text,
            r"\n  - id: training\.group\n.*?(?=\n  - id: training\.attendance\n)",
            "\n",
            "remove training.group screen",
        )

    write(path, text)


def update_routes() -> None:
    path = "docs/ROUTES.yaml"
    text = read(path)

    players_route = """  - path: /profile/players
    screen: profile.players
    navigator: profile_stack
    parent: /profile
    accepts_query: [mode, entityType, entityId, actorId]
    back_fallback: /profile

"""
    marker = "  - path: /profile/trips\n"
    if "  - path: /profile/players\n" not in text:
        text = replace_once(text, marker, players_route + marker, "insert profile.players route")

    text = replace_once(
        text,
        "    accepts_query: [returnTo, actorId, draftId, groupId]\n",
        "    accepts_query: [returnTo, actorId, draftId, templateId]\n",
        "remove groupId from training create",
    )

    if "  - path: /training-groups/:groupId\n" in text:
        text = regex_replace_once(
            text,
            r"\n  - path: /training-groups/:groupId\n.*?(?=\n  - path: /trainings/:trainingId/attendance\n)",
            "\n",
            "remove training group route",
        )

    write(path, text)


def update_actions() -> None:
    path = "docs/ACTIONS.yaml"
    text = read(path)

    nav_action = """  - id: nav.open_profile_players
    label: Мои игроки
    source: profile.main
    destination: profile.players
    permission: authenticated

"""
    marker = "  - id: nav.open_profile_trips\n"
    if "  - id: nav.open_profile_players\n" not in text:
        text = replace_once(text, marker, nav_action + marker, "insert profile players navigation action")

    player_actions = """  # Player directory and event invitations
  - id: players.add
    label: Добавить игрока
    source: profile.players
    destination: system.player_search
    permission: authenticated

  - id: players.remove
    label: Удалить из моих игроков
    source: profile.players
    destination: system.remove_saved_player_confirmation
    permission: saved_player_list_owner

  - id: players.open_public_profile
    label: Открыть профиль игрока
    source: profile.players
    destination: dynamic.player_public_profile
    permission: authenticated

  - id: players.open_picker
    label: Добавить игроков
    source: dynamic.entity_create_or_manage
    destination: system.player_picker
    permission: entity_inviter

  - id: players.send_invitations
    label: Отправить приглашения
    source: system.player_picker
    destination: system.create_event_invitations
    permission: entity_inviter

  - id: players.add_as_confirmed
    label: Добавить как подтверждённого
    source: system.player_picker
    destination: system.add_confirmed_participant_with_audit
    permission: participant_manager

"""
    actions_marker = "  # Participation actions shared by entities\n"
    if "  - id: players.add\n" not in text:
        text = replace_once(text, actions_marker, player_actions + actions_marker, "insert player directory actions")

    if "  - id: training.open_group\n" in text:
        text = regex_replace_once(
            text,
            r"\n  - id: training\.open_group\n.*?(?=\n  # Tours\n)",
            "\n",
            "remove training group action",
        )

    write(path, text)


def update_audit() -> None:
    path = "docs/ARCHITECTURE_AUDIT.md"
    text = read(path)
    old = """- регистрация `Мои игроки` и player picker в глобальных реестрах экранов, маршрутов и действий;
- окончательное удаление legacy `training.group` после миграционного периода;
"""
    new = """- реализация интерфейса `Мои игроки` и player picker по зарегистрированным screen_id, route и action_id;
"""
    if old in text:
        text = replace_once(text, old, new, "update architecture audit")
    write(path, text)


def main() -> None:
    update_screens()
    update_routes()
    update_actions()
    update_audit()
    print("Player registry migration applied successfully")


if __name__ == "__main__":
    main()
