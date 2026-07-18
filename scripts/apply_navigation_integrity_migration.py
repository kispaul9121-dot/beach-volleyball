from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def update(path: str, transform) -> None:
    file_path = ROOT / path
    old = file_path.read_text(encoding="utf-8")
    new = transform(old)
    if new == old:
        print(f"No change: {path}")
        return
    file_path.write_text(new, encoding="utf-8")
    print(f"Updated: {path}")


def replace(text: str, old: str, new: str) -> str:
    return text.replace(old, new)


def update_ui_rules(text: str) -> str:
    text = replace(
        text,
        "Ровно пять пунктов: Главная, Играть, Чаты, Клубы, Профиль. Набор вкладок не меняется при переключении actor-профиля; меняются приоритеты и содержимое.",
        "Ровно пять пунктов: Главная, События, Чаты, Клубы, Профиль. Набор, порядок, названия и маршруты вкладок не меняются при переключении actor-профиля; меняются только приоритеты и содержимое.",
    )
    text = replace(text, "- На Главной и в верхней части Играть", "- На Главной и в верхней части Событий")
    text = replace(text, "- В Играть: игры", "- В Событиях: игры")
    return text


def update_app_map(text: str) -> str:
    replacements = {
        "Главная · Играть · Чаты · Клубы · Профиль": "Главная · События · Чаты · Клубы · Профиль",
        "## 4. Играть": "## 4. События",
        "\nИграть\n├── Управляю — закреплённый блок": "\nСобытия\n├── Все — публичный каталог\n├── Участвую — участия, заявки и приглашения\n├── Управляю — созданные события и задачи",
        "├── Группы\n├── Управляю": "├── Мои игроки\n├── Управляю",
        "├── Тренировки и группы": "├── Тренировки",
        "├── Партнёры\n├── Мои профили": "├── Мои игроки\n├── Мои профили",
        "│   └── Группы\n├── Игры": "│   └── Архив\n├── Игры",
        "├── Ученики\n├── Статистика тренера": "├── Мои игроки\n├── Статистика тренера",
        "├── Тренировки и группы\n├── Туры": "├── Тренировки\n├── Туры",
        "Мои тренировки\n├── Записан\n├── Провожу / Организую\n└── Группы": "Мои тренировки\n├── Участвую\n└── Управляю",
        "├── Оплаты / абонементы": "├── Оплаты",
        "├── Тренер: занятия, ученики, посещаемость": "├── Тренер: занятия, игроки, посещаемость",
        "Играть ──┤": "События ─┤",
    }
    for old, new in replacements.items():
        text = replace(text, old, new)

    text = re.sub(
        r"\nТренировочная группа\n├── Участники\n├── Расписание\n├── Абонементы\n├── Посещаемость\n├── Прогресс\n├── Чат\n└── Настройки",
        "",
        text,
    )
    return text


def update_screens(text: str) -> str:
    text = replace(text, "  - global.create_menu\n  - global.search_filters", "  - system.create_menu\n  - system.search_filters")
    text = replace(
        text,
        "purpose: Принятие или отклонение приглашения в событие, группу или организацию.",
        "purpose: Принятие или отклонение приглашения в событие или организацию.",
    )

    marker = "  - id: trainer.public_profile\n"
    if "  - id: player.public_profile\n" not in text:
        snippet = (
            "  - id: player.public_profile\n"
            "    title: Игрок\n"
            "    route: /players/:playerId\n"
            "    section: clubs\n"
            "    spec: docs/screens/clubs/player-details.md\n"
            "    purpose: Публичный спортивный профиль игрока с учётом приватности.\n"
            "    variants: [stranger, saved_player, owner]\n"
            "    back_fallback: /profile/players\n\n"
        )
        if marker not in text:
            raise RuntimeError("trainer.public_profile marker not found in SCREENS.yaml")
        text = text.replace(marker, snippet + marker, 1)

    trainer_block = (
        "  - id: trainer.public_profile\n"
        "    title: Тренер\n"
        "    route: /trainers/:trainerId\n"
        "    section: clubs\n"
        "    spec: docs/screens/clubs/trainer-details.md\n"
        "    purpose: Публичный профиль, расписание и отзывы тренера.\n"
        "    back_fallback: /clubs?category=trainers"
    )
    trainer_block_with_variants = (
        "  - id: trainer.public_profile\n"
        "    title: Тренер\n"
        "    route: /trainers/:trainerId\n"
        "    section: clubs\n"
        "    spec: docs/screens/clubs/trainer-details.md\n"
        "    purpose: Публичный профиль, расписание и отзывы тренера.\n"
        "    variants: [guest, authenticated_player, owner, organization_manager]\n"
        "    back_fallback: /clubs?category=trainers"
    )
    text = replace(text, trainer_block, trainer_block_with_variants)
    return text


def update_routes(text: str) -> str:
    marker = "  - path: /trainers/:trainerId\n"
    if "  - path: /players/:playerId\n" not in text:
        snippet = (
            "  - path: /players/:playerId\n"
            "    screen: player.public_profile\n"
            "    navigator: entity_stack\n"
            "    access: public_preview_or_authenticated\n"
            "    back_fallback: /profile/players\n\n"
        )
        if marker not in text:
            raise RuntimeError("trainer route marker not found in ROUTES.yaml")
        text = text.replace(marker, snippet + marker, 1)

    text = replace(
        text,
        "accepts_query: [category, managed, date, actorId]",
        "accepts_query: [category, managed, date, actorId, trainerId]",
    )
    return text


def update_actions(text: str) -> str:
    text = replace(text, "destination: dynamic.player_public_profile", "destination: player.public_profile")

    text = replace(
        text,
        "  - id: my_games.continue_draft\n    label: Продолжить создание\n    source: profile.my_games\n    destination: game.create\n    permission: draft_owner",
        "  - id: my_games.continue_draft\n    label: Продолжить создание\n    source: profile.my_games\n    destination: game.create\n    permission: draft_owner\n    context:\n      returnTo: /profile/games?tab=created\n      actorId: draft_actor",
    )

    text = replace(
        text,
        "  - id: players.open_picker\n    label: Добавить игроков\n    source: dynamic.entity_create_or_manage\n    destination: player.picker\n    permission: entity_inviter",
        "  - id: players.open_picker\n    label: Добавить игроков\n    source: dynamic.entity_create_or_manage\n    destination: player.picker\n    permission: entity_inviter\n    context:\n      entityType: current_entity_type\n      entityId: current_entity_id_or_null\n      draftId: current_draft_id_or_null\n      actorId: active_actor\n      returnTo: current_create_or_manage_route",
    )

    if "  - id: notifications.open_target\n" not in text:
        marker = "  - id: nav.open_profile_calendar\n"
        snippet = (
            "  - id: notifications.open_target\n"
            "    label: Открыть уведомление\n"
            "    source: global.notifications\n"
            "    destination: dynamic.notification_target\n"
            "    permission: authenticated\n\n"
        )
        text = text.replace(marker, snippet + marker, 1)

    if "  - id: chats.open_chat\n" not in text:
        marker = "  # Chat\n"
        snippet = (
            "  - id: chats.open_chat\n"
            "    label: Открыть чат\n"
            "    source: chats.main\n"
            "    destination: chat.details\n"
            "    permission: conversation_member\n\n"
        )
        text = text.replace(marker, marker + snippet, 1)

    if "  - id: clubs.open_club\n" not in text:
        marker = "  # Home and Play visibility\n"
        snippet = (
            "  # Club directory cards\n"
            "  - id: clubs.open_club\n"
            "    label: Открыть клуб\n"
            "    source: clubs.main\n"
            "    destination: club.details\n"
            "    permission: public\n\n"
            "  - id: clubs.open_venue\n"
            "    label: Открыть площадку\n"
            "    source: clubs.main\n"
            "    destination: venue.details\n"
            "    permission: public\n\n"
            "  - id: clubs.open_trainer\n"
            "    label: Открыть тренера\n"
            "    source: clubs.main\n"
            "    destination: trainer.public_profile\n"
            "    permission: public\n\n"
            "  - id: clubs.open_tour\n"
            "    label: Открыть тур\n"
            "    source: clubs.main\n"
            "    destination: tour.details\n"
            "    permission: public\n\n"
        )
        text = text.replace(marker, snippet + marker, 1)

    if "  - id: players.save_from_public_profile\n" not in text:
        marker = "  # Participation actions shared by entities\n"
        snippet = (
            "  - id: players.save_from_public_profile\n"
            "    label: Добавить в Мои игроки\n"
            "    source: player.public_profile\n"
            "    destination: system.save_player_to_directory\n"
            "    permission: authenticated\n\n"
            "  - id: players.remove_from_public_profile\n"
            "    label: Удалить из Моих игроков\n"
            "    source: player.public_profile\n"
            "    destination: system.remove_saved_player_confirmation\n"
            "    permission: saved_player_list_owner\n\n"
            "  - id: players.invite_from_public_profile\n"
            "    label: Пригласить в событие\n"
            "    source: player.public_profile\n"
            "    destination: system.event_picker_for_invitation\n"
            "    permission: entity_inviter\n\n"
            "  - id: player.open_shared_event\n"
            "    label: Открыть общее событие\n"
            "    source: player.public_profile\n"
            "    destination: dynamic.entity_details\n"
            "    permission: authenticated\n\n"
            "  - id: player.share_profile\n"
            "    label: Поделиться профилем\n"
            "    source: player.public_profile\n"
            "    destination: system.share_sheet\n"
            "    permission: public\n\n"
            "  - id: player.report_profile\n"
            "    label: Пожаловаться\n"
            "    source: player.public_profile\n"
            "    destination: system.report_profile\n"
            "    permission: authenticated\n\n"
        )
        text = text.replace(marker, snippet + marker, 1)

    if "  - id: trainer.open_training\n" not in text:
        marker = "  # Calendar\n"
        snippet = (
            "  # Public trainer profile\n"
            "  - id: trainer.open_training\n"
            "    label: Открыть тренировку\n"
            "    source: trainer.public_profile\n"
            "    destination: training.details\n"
            "    permission: public\n\n"
            "  - id: trainer.open_schedule\n"
            "    label: Посмотреть расписание\n"
            "    source: trainer.public_profile\n"
            "    destination: play.main\n"
            "    context: {category: trainings, trainerId: selected_trainer}\n"
            "    permission: public\n\n"
            "  - id: trainer.open_tour\n"
            "    label: Открыть тур\n"
            "    source: trainer.public_profile\n"
            "    destination: tour.details\n"
            "    permission: public\n\n"
            "  - id: trainer.open_club\n"
            "    label: Открыть клуб\n"
            "    source: trainer.public_profile\n"
            "    destination: club.details\n"
            "    permission: public\n\n"
            "  - id: trainer.message\n"
            "    label: Написать\n"
            "    source: trainer.public_profile\n"
            "    destination: system.open_or_create_direct_chat\n"
            "    permission: trainer_allows_messages\n\n"
            "  - id: trainer.share\n"
            "    label: Поделиться\n"
            "    source: trainer.public_profile\n"
            "    destination: system.share_sheet\n"
            "    permission: public\n\n"
            "  - id: trainer.owner_edit_profile\n"
            "    label: Редактировать публичный профиль\n"
            "    source: trainer.public_profile\n"
            "    destination: profile.settings\n"
            "    context: {section: trainer-public-profile}\n"
            "    permission: profile_owner\n\n"
        )
        text = text.replace(marker, snippet + marker, 1)
    return text


update("docs/UI_RULES.md", update_ui_rules)
update("docs/APP_MAP.md", update_app_map)
update("docs/SCREENS.yaml", update_screens)
update("docs/ROUTES.yaml", update_routes)
update("docs/ACTIONS.yaml", update_actions)
