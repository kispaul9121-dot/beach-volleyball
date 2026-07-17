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


def update_player_directory() -> None:
    path = "docs/PLAYER_DIRECTORY.yaml"
    text = read(path)
    text = replace_once(
        text,
        "  - invitation-first publication\n",
        "  - event visibility and enrollment\n",
        "player directory source scope",
    )
    new_block = """visibility_and_enrollment:
  visibility_modes:
    private:
      catalog_visibility: hidden
      discovery: invitation_or_private_link
    public:
      catalog_visibility: visible_in_events_all
      discovery: events_catalog
  rules:
    - Видимость выбирается для всей сущности, а не для отдельных свободных мест.
    - Приглашения можно отправлять и для публичной, и для непубличной сущности.
    - Публичная сущность целиком появляется в `События → Все` после публикации.
    - Непубличная сущность не появляется в `События → Все`, но доступна по приглашению или приватной ссылке.
    - Смена видимости не удаляет приглашения, заявки, подтверждённые участия и платежи.
    - Способ набора настраивается отдельно от видимости.
  enrollment_modes:
    - open
    - request
    - invitation_only
  full_capacity_behavior:
    - close_registration
    - enable_waitlist

"""
    text = regex_replace_once(
        text,
        r"visibility_and_fill:\n.*?(?=chat_access:)",
        new_block,
        "replace visibility and fill model",
    )
    write(path, text)


def update_training_create() -> None:
    path = "docs/screens/shared/training-create.md"
    text = read(path)
    text = replace_once(
        text,
        "Создать отдельную тренировку, выбрать игроков из списка `Мои игроки`, отправить приглашения и при необходимости открыть оставшиеся места публично. Тренировочная группа как отдельная сущность в MVP не используется.",
        "Создать отдельную тренировку, выбрать игроков из списка `Мои игроки`, отправить приглашения и выбрать публичность всей тренировки. Тренировочная группа как отдельная сущность в MVP не используется.",
        "training create purpose",
    )
    visibility = """## Видимость и набор

Видимость и способ набора являются независимыми настройками.

### Непубличная

- вся тренировка не показывается в `События → Все`;
- открыть её можно по приглашению, приватной ссылке или через личный статус участия;
- приглашённый видит её в `События → Участвую`;
- создатель и разрешённые сотрудники видят её в `События → Управляю`.

### Публичная

- вся тренировка после публикации показывается в `События → Все`;
- карточка содержит вместимость и свободные места;
- приглашения из `Мои игроки` по-прежнему можно отправлять напрямую;
- при заполнении регистрация закрывается или включается лист ожидания.

### Способ набора

Отдельно выбирается:

- `open` — игрок записывается сразу;
- `request` — игрок подаёт заявку;
- `invitation_only` — участие только по приглашению, даже если публичная карточка используется как информационный анонс.

В MVP нет режима `Сначала приглашения, потом публично` и действия `Открыть оставшиеся места`. Изменение публичности относится ко всей тренировке.
"""
    text = regex_replace_once(
        text,
        r"## Видимость и набор\n.*?(?=\n## Правила игрока)",
        visibility,
        "training visibility section",
    )
    text = replace_once(
        text,
        "Черновик сохраняет actorId, режим, назначенного тренера, выбранных игроков, видимость, enrollment mode и момент открытия оставшихся мест. После публикации открывается канонический экран или `returnTo`.",
        "Черновик сохраняет actorId, режим, назначенного тренера, выбранных игроков, видимость всей тренировки и enrollment mode. После публикации открывается канонический экран или `returnTo`.",
        "training autosave visibility",
    )
    write(path, text)


def update_training_manage() -> None:
    path = "docs/screens/shared/training-manage.md"
    text = read(path)
    text = replace_once(
        text,
        "- момент открытия оставшихся мест;\n",
        "- способ набора;\n",
        "training dashboard visibility",
    )
    section = """## Видимость и набор

Менеджер управляет двумя независимыми параметрами:

- видимость всей тренировки: `Публичная` или `Непубличная`;
- способ набора: `Открытая запись`, `По заявке` или `Только по приглашению`.

Публичная тренировка целиком показывается в `События → Все`. Непубличная тренировка скрыта из общего каталога, но остаётся доступна приглашённым по приглашению или приватной ссылке, участникам — в `События → Участвую`, а менеджерам — в `События → Управляю`.

Смена видимости не отменяет существующие приглашения, заявки, участия и платежи. Изменение после публикации создаёт audit event и при необходимости системное сообщение участникам.

При заполненной вместимости система закрывает регистрацию или включает лист ожидания согласно настройке тренировки. Отдельного действия `Открыть оставшиеся места` нет.
"""
    text = regex_replace_once(
        text,
        r"## Заполнение мест\n.*?(?=\n## Посещаемость)",
        section,
        "training manage visibility section",
    )
    write(path, text)


def update_training_details() -> None:
    path = "docs/screens/shared/training-details.md"
    text = read(path)
    text = replace_once(
        text,
        "- свободные места ещё не открыты публично;\n- публичная запись открыта;\n",
        "- непубличная тренировка, доступная по приглашению или приватной ссылке;\n- публичная тренировка в `События → Все`;\n- открытая запись;\n- запись по заявке;\n- участие только по приглашению;\n",
        "training detail states",
    )
    write(path, text)


def update_my_trainings() -> None:
    path = "docs/screens/profile/my-trainings.md"
    text = read(path)
    text = replace_once(
        text,
        "- режим видимости;\n- оставшиеся места открыты публично или нет.\n",
        "- видимость всей тренировки: публичная или непубличная;\n- способ набора: открытая запись, заявка или приглашение.\n",
        "my trainings card visibility",
    )
    text = replace_once(
        text,
        "Действия: Управлять, Добавить игроков, Посещаемость, Открыть чат, Открыть оставшиеся места, Дублировать.",
        "Действия: Управлять, Добавить игроков, Посещаемость, Открыть чат, Дублировать. Видимость и способ набора меняются внутри управления тренировкой.",
        "my trainings actions",
    )
    write(path, text)


def update_audit() -> None:
    path = "docs/ARCHITECTURE_AUDIT.md"
    text = read(path)
    text = replace_once(
        text,
        "- режим `Сначала приглашения, потом публично` открывает оставшиеся места вручную или по времени;\n",
        "- публичность относится ко всей тренировке: публичная появляется в `События → Все`, непубличная остаётся доступна только по отношению пользователя к событию;\n- способ набора `open / request / invitation_only` настраивается отдельно от публичности;\n",
        "architecture audit visibility",
    )
    write(path, text)


def update_test_scenarios() -> None:
    path = "docs/TEST_SCENARIOS.md"
    text = read(path)
    replacement = """## A-13 — Тренер приглашает игроков в тренировку

1. Активен trainer actor.
2. Тренер создаёт тренировку и задаёт вместимость 8 мест.
3. Нажимает `Добавить игроков` и открывает `player.picker` без глобального нижнего меню.
4. Выбирает трёх игроков из `Мои игроки` и одного из `Недавние`.
5. Отправляет приглашения и возвращается на тот же шаг создания.
6. Выбирает для всей тренировки видимость `Публичная` и способ набора `По заявке`.
7. Публикует тренировку; она целиком появляется в `События → Все` и в `События → Управляю` у тренера.
8. Два приглашённых игрока принимают приглашение; для платного события получают `payment_required`, а тренировка появляется у них в `События → Участвую`.
9. Подтверждённые игроки получают доступ к чату тренировки.
10. При смене видимости на `Непубличная` карточка исчезает из `События → Все`, но остаётся доступна участникам, приглашённым и менеджерам по их отношению к событию.

Ожидание: публичность применяется ко всей тренировке; отдельной публикации свободных мест нет; способ набора не смешивается с видимостью; `Мои игроки` остаётся profile stack-экраном; picker является отдельным modal; выбор не создаёт участие до отправки; приглашённые не видят чат до подтверждения; постоянная тренировочная группа не создаётся.
"""
    text = regex_replace_once(
        text,
        r"## A-13 — Тренер приглашает игроков в тренировку\n.*?(?=\n## A-14)",
        replacement,
        "A-13 training visibility scenario",
    )
    write(path, text)


def update_play() -> None:
    path = "docs/screens/play/main.md"
    text = read(path)
    text = replace_once(
        text,
        "Публичный каталог доступных событий. Показывает также статус текущего пользователя или активного actor-профиля.",
        "Публичный каталог доступных событий. Здесь показываются только сущности с публичной видимостью целиком. Непубличные игры, тренировки, турниры, сезоны и туры во вкладку `Все` не попадают, даже когда у них есть свободные места. Карточка также показывает статус текущего пользователя или активного actor-профиля.",
        "Events All visibility",
    )
    text = replace_once(
        text,
        "3. группы и тренерские события;\n",
        "3. тренировки и другие тренерские события;\n",
        "remove group wording from Events",
    )
    text = replace_once(
        text,
        "События, где человек является участником, приглашённым, заявителем или находится в листе ожидания. Спортивное участие человека связывается с player profile, даже когда активен профиль тренера или организации.",
        "События, где человек является участником, приглашённым, заявителем или находится в листе ожидания. Здесь отображаются и непубличные события, когда у человека есть соответствующее отношение или приглашение. Спортивное участие связывается с player profile, даже когда активен профиль тренера или организации.",
        "Events Participating visibility",
    )
    write(path, text)


def update_data_model() -> None:
    path = "docs/DATA_MODEL.md"
    text = read(path)
    text = replace_once(
        text,
        "- `training_visibility_rules` — private, public, invite_then_public;\n- `training_enrollment_rules` — open, request, invitation_only;\n- `training_public_open_schedules` — момент открытия оставшихся мест;\n",
        "- `training_visibility_rules` — private или public для всей тренировки;\n- `training_enrollment_rules` — open, request, invitation_only независимо от видимости;\n- `training_visibility_events` — аудит публикации, скрытия и повторного открытия всей тренировки;\n",
        "training data visibility",
    )
    write(path, text)


def update_chat_details() -> None:
    path = "docs/screens/chats/details.md"
    text = read(path)
    text = replace_once(
        text,
        "- открыт публичный набор;\n",
        "- изменена видимость события;\n",
        "chat visibility system event",
    )
    write(path, text)


def update_agents() -> None:
    path = "AGENTS.md"
    text = read(path)
    marker = "- Приглашение всегда относится к конкретному событию.\n"
    addition = (
        "- Видимость применяется ко всей сущности: `Публичная` или `Непубличная`; не публиковать отдельно свободные места.\n"
        "- Публичная сущность появляется в `События → Все`; непубличная скрыта из `Все`, но доступна в `Участвую` и `Управляю` по отношению пользователя.\n"
        "- Способ набора `open / request / invitation_only` не смешивать с видимостью.\n"
    )
    if addition not in text:
        text = replace_once(text, marker, addition + marker, "AGENTS visibility rules")
    write(path, text)


def update_decisions() -> None:
    path = "docs/DECISIONS.md"
    text = read(path)
    if "## D-025 — Публичность относится ко всей тренировке" not in text:
        text = text.rstrip() + """

## D-025 — Публичность относится ко всей тренировке

Статус: принято.

Создатель выбирает для всей тренировки одно из двух состояний: `Публичная` или `Непубличная`.

Публичная тренировка после публикации целиком появляется в `События → Все`. Непубличная тренировка не появляется в общем каталоге, но доступна по приглашению или приватной ссылке и показывается во вкладке `Участвую` приглашённым, заявителям и участникам, а во вкладке `Управляю` — создателю и разрешённым сотрудникам.

Способ набора (`open`, `request`, `invitation_only`) является отдельной настройкой. В MVP нет режима `Сначала приглашения, потом публично` и действия публикации только оставшихся мест. Смена публичности не удаляет существующие приглашения, участия и платежи.
""" + "\n"
    write(path, text)


def main() -> None:
    update_player_directory()
    update_training_create()
    update_training_manage()
    update_training_details()
    update_my_trainings()
    update_audit()
    update_test_scenarios()
    update_play()
    update_data_model()
    update_chat_details()
    update_agents()
    update_decisions()
    print("Training visibility migration applied successfully")


if __name__ == "__main__":
    main()
