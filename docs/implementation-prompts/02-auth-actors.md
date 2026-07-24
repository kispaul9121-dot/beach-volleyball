# Блок 2 — аутентификация и actor-профили

## 009 — Типы данных и service contracts без привязки к backend

```text
Цель: превратить DATA_MODEL.md и YAML-контракты в типизированные TypeScript-модели, не изобретая API.

Прочитай DATA_MODEL.md, ACTORS.yaml, ROLES.yaml, CAPABILITIES.yaml, ENTITY_LIFECYCLES.yaml и FINANCE_ARCHITECTURE.yaml.

Сделай:
1. Создай branded ID types для user, actor, entity, participant, match, conversation, payment и invitation.
2. Раздели user_account и actor_profile.
3. Опиши discriminated unions для actor type, entity lifecycle, participation, payment и permission result.
4. Создай service interfaces для auth, actors, catalog, entities, chat, payment и notifications без конкретного transport.
5. Добавь runtime validation на внешней границе; не дублируй domain types отдельными screen types.
6. Не моделируй сезоны, удалённые турнирные форматы или социальные friends/groups.
7. Оставь extension points для пока не реализованных полей, но не используй untyped dictionaries.

Тесты: invalid payload rejection, stable serialization, actor/user separation и exhaustive switches.

Commit: feat: add typed domain and service contracts
```

## 010 — Детерминированные fixtures и mock adapters

```text
Цель: дать незавершённым экранам реалистичные данные, не выдавая mock за backend.

Создай src/testing fixtures и development adapters для user/actor, игр, тренировок, турниров, кэмпов, приглашений, чатов и платежных статусов.

Требования:
1. Fixtures детерминированы через seed.
2. Сценарии включают guest, participant, owner, delegated manager, no permission, loading, empty, offline и error.
3. Тунисская лестница: 1/2/3 площадки и 5/10/15 игроков.
4. Турниры: только single elimination и full placement; fixture 32 команд даёт 80 матчей в full placement.
5. Mock adapter включается только development/test конфигурацией и явно помечается в debug UI.
6. Не добавляй fake success для платежа или auth в production build.
7. Добавь reset fixtures и helper для component tests.

Проверки: одинаковый seed даёт одинаковые ID и порядок; production bundle не импортирует development adapter.

Commit: test: add deterministic development fixtures
```

## 011 — Auth welcome и вход

```text
Реализуй auth.welcome и auth.sign_in по onboarding spec.

Область: только публичные signed-out экраны, auth service calls и их тесты.

Сделай:
1. Welcome с Google и email entry actions из ACTIONS.yaml.
2. Email/password sign-in с validation, password visibility и reset link.
3. Сохрани returnTo для deep link, но не разрешай open redirect.
4. Состояния: idle, submitting, provider unavailable, invalid credentials, offline, rate limited и unexpected error.
5. После успешного входа resolver решает onboarding или app shell.
6. Не реализуй регистрацию, verification или reset form в этом промте.
7. Не создавай второй auth store рядом с service/session provider.

Тесты: actions IDs, submit once, keyboard, autofill semantics, invalid returnTo и signed-in redirect.

Commit: feat: implement welcome and sign in
```

## 012 — Регистрация, email verification и reset password

```text
Реализуй auth.email_registration, auth.verify_email и auth.reset_password, сохранив auth shell промта 011.

Сделай:
1. Registration validation и явное согласие только для реально требуемых документов.
2. Verification screen с resend cooldown и обработкой уже подтверждённой ссылки.
3. Reset request и установка нового пароля с token expiry.
4. Не хранить пароль, reset token или provider error details в analytics/logs.
5. Состояния для каждого шага: submitting, sent, expired, invalid, offline, rate limited, success.
6. Добавь отсутствующие action_id только через синхронное обновление ACTIONS/ROUTES/spec, если они действительно отсутствуют.
7. Не переходи к actor onboarding до authoritative session refresh.

Тесты: one-time token, repeated resend, expired link deep link, accessibility announcements.

Commit: feat: complete email auth recovery flows
```

## 013 — Onboarding обязательного профиля игрока

```text
Реализуй onboarding.profile_selection и onboarding.player.

Правила:
1. Player profile создаётся всегда.
2. Trainer и organization выбираются как дополнительные профили, не роли аккаунта.
3. Минимальные обязательные поля брать только из AUTH_AND_ONBOARDING.md/ACTORS.yaml.
4. Черновик onboarding восстанавливается после перезапуска.
5. Назад не удаляет уже сохранённый user account.
6. Не требуй спортивный рейтинг, фото или публичность, если контракт не делает их обязательными.
7. Покажи progress без ложного количества шагов при разных выбранных профилях.
8. После player step route resolver ведёт к выбранным optional steps или permissions.

Тесты: player-only, player+trainer, player+organization, all profiles и interrupted resume.

Commit: feat: implement player onboarding foundation
```

## 014 — Optional onboarding тренера и организации

```text
Реализуй onboarding.trainer и onboarding.organization только в пределах утверждённых полей.

Статус-зависимое правило: если verification, legal documents или organization finance ещё definition_pending, создай честный pending block и typed draft field; не симулируй проверку.

Сделай:
1. Trainer professional data и verification status representation.
2. Organization identity, display name и минимальные реквизиты без автоматического открытия финансовых функций.
3. Возможность пропустить optional profile и создать его позже.
4. created_by_user_id сохраняется отдельно от actor id.
5. Ошибка одного optional шага не уничтожает player profile.
6. Не создавай club.manage автоматически, пока organization actor не создан authoritative service response.

Тесты: skip/resume, validation, duplicate organization prevention и partial server failure.

Commit: feat: add optional actor onboarding
```

## 015 — Actor store, switcher и capability resolver

```text
Реализуй единый actor context и actor.switcher.

Сделай:
1. Active actor хранится как preference, но проверяется против доступных профилей session.
2. Переключение не меняет user account и auth session.
3. Capability resolver принимает actor, relation, entity и server grants; actor type сам по себе не даёт чужих прав.
4. После переключения invalidate только actor-dependent queries.
5. Switcher показывает player всегда, optional trainer/organization и действие управления профилями.
6. При удалённом actor безопасно откатывается на player с уведомлением.
7. Modal сохраняет returnTo и не создаёт второй navigation shell.

Тесты: permission recalculation, stale actor, deep link under wrong actor, organization member without ownership.

Commit: feat: implement actor switching and capabilities
```

## 016 — Контрольный аудит auth и actor boundary

```text
Это audit-only промт. Не добавляй новые auth или actor возможности.

Проверь промты 009–015:
- user_account нигде не смешан с actor_profile;
- secure tokens не находятся в AsyncStorage в открытом виде;
- signed-out routes закрыты после входа и наоборот;
- returnTo ограничен известными внутренними маршрутами;
- active actor не даёт доступа без capability;
- optional onboarding действительно можно пропустить;
- loading/error/offline состояния не подтверждают действие оптимистично;
- fixtures не попадают в production.

Добавь отрицательные integration tests для доступа к чужому manage route и для подмены actorId. Исправляй только подтверждённые дефекты этого блока. Обнови IMPLEMENTATION_STATUS.yaml.

Commit: test: audit auth and actor boundaries
```