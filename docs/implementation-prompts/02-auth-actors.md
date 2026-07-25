# Блок 2 — Supabase, авторизация и actor-профили

## 010 — Supabase project и миграционный baseline

```text
Работай по runbook и IMPLEMENTATION_RUNTIME.yaml. Используй подключённый Supabase plugin/MCP; если он недоступен, останови только backend mutation и выведи blocked_by_connection.

Создай или свяжи Supabase project, добавь supabase/config.toml, migrations directory, .env.example и разделение local/preview/production. Не помещай service-role key, database password или access token в клиент и Git. Первая migration создаёт только необходимые extension/schema baseline и audit metadata, без полной продуктовой модели.

Сделай команды bootstrap/reset/status повторяемыми и задокументируй их. Существующий Expo app не пересоздавай.

Проверки: Supabase local start или remote connection, migration up/down where supported, secret scan, architecture validators.
Commit: chore: initialize Supabase project and migration workflow
```

## 011 — Supabase client для Expo

```text
Подключи официальный Expo-compatible Supabase client через npx expo install. Создай один typed client module, env validation и session storage через Expo SQLite/localStorage adapter согласно текущей совместимой документации.

Auth options: persistSession, autoRefreshToken, detectSessionInUrl=false для native, корректный AppState lifecycle. Клиент использует только URL и publishable key. Не создавай второй client в features и не смешивай query code с UI.

Добавь DataSource/Repository boundary, network error mapping и безопасное состояние «backend не настроен» для dev build. Не маскируй неверные env fixtures.

Через iOS-плагин проверь cold launch и foreground/background без crash.
Проверки: unit tests env/client singleton, typecheck, no service key, iOS smoke.
Commit: feat: add Expo Supabase client and session storage
```

## 012 — Email-регистрация и вход

```text
Реализуй auth.welcome, auth.sign_in и auth.email_registration через Supabase Auth, сохраняя screen_id, routes и action_id.

Поддержи email/password, form validation, loading без layout jump, ошибки неверных данных, rate limit и offline. Google/Apple sign-in не реализуй без утверждённого контракта: оставь feature flag или definition_pending. После успеха переходи через auth resolver, а не напрямую в случайную вкладку.

Не создавай профиль игрока в UI-компоненте; это выполняется отдельным onboarding flow. Повторная отправка формы должна быть idempotent на клиентском уровне.

Через iOS-плагин проверь keyboard avoidance, autofill hints, secure text entry, Dynamic Type и VoiceOver.
Проверки: auth repository tests, component tests success/error/offline, deep link guard.
Commit: feat: implement Supabase email authentication screens
```

## 013 — Подтверждение email и восстановление пароля

```text
Реализуй auth.verify_email и auth.reset_password на канонических маршрутах.

Обработай resend verification с cooldown, expired token, already verified, invalid/used reset link и успешную установку нового пароля. Настрой native deep-link callback через Expo Router; не помещай session tokens в logs или analytics. Cold start по ссылке должен восстановить нужный экран и безопасно отклонить malformed params.

Если provider/dashboard redirect URL требует ручной настройки, запиши точный шаг в IMPLEMENTATION_RUNTIME.yaml и не выдавай сценарий за готовый.

Через iOS-плагин проверь открытие universal/custom scheme link, back fallback, keyboard и системный Password AutoFill.
Проверки: parser/unit tests, expired-link integration tests, iOS cold-link smoke.
Commit: feat: add email verification and password recovery
```

## 014 — Восстановление сессии и auth guards

```text
Добавь единый auth bootstrap перед показом защищённых routes.

Реализуй session restore, token refresh на foreground, signed-out/signed-in/pending-verification guards и отсутствие redirect loops. UI не должен мигать приватным экраном до разрешения session state. При revoked session очисти только auth state и верни пользователя в sign-in с понятным сообщением.

Все guards используют один auth store/service. Не дублируй getSession calls в каждом экране. Offline при валидной локальной сессии даёт read-only shell, но не разрешает server mutations оптимистично.

Через iOS-плагин проверь kill/relaunch, background/foreground и revoked-session flow.
Проверки: state-machine tests и route integration tests.
Commit: feat: add session bootstrap and route guards
```

## 015 — Профиль игрока при onboarding

```text
Создай Supabase migrations для player_profiles и минимального actor_profile игрока по DATA_MODEL.md и ACTORS.yaml. Включи RLS и уникальные ограничения, чтобы один обязательный player actor не создавался дважды.

Реализуй onboarding.player: обязательные поля, avatar placeholder, validation и transactional save через repository. При повторном входе незавершённый onboarding продолжается, а уже завершённый не создаёт новую запись. Не добавляй спортивные поля, которых нет в контракте.

После успешного сохранения active actor становится player и resolver ведёт в приложение.

Через iOS-плагин проверь форму, image placeholder, keyboard, 200% text и interrupted resume.
Проверки: migration/RLS tests, duplicate prevention и component tests.
Commit: feat: create player onboarding and profile schema
```

## 016 — Модель actor-профилей и memberships

```text
Реализуй таблицы/типы actor_profiles, trainer_profiles, organization_profiles и memberships только в объёме утверждённых документов.

Каждая создаваемая сущность в будущем должна хранить created_by_user_id, created_by_actor_id и created_by_actor_type. Actor type сам по себе не даёт право управлять чужими данными. Добавь constraints и RLS helpers для owner/member relationships.

Trainer и organization onboarding, если поля ещё definition_pending, получают schema-compatible minimal records и честные placeholders, а не выдуманные анкеты.

Сгенерируй TypeScript types из схемы и подключи domain mappers.
Проверки: migration tests, RLS negative cases, generated types compile.
Commit: feat: establish actor profiles and membership model
```

## 017 — Переключатель actor-профилей

```text
Реализуй actor.switcher поверх реальных actor_profiles текущего account.

Покажи player, trainer и organization profiles, статус доступности и active marker. Переключение сохраняет active_actor_id локально, пересчитывает capabilities и возвращает пользователя в безопасный route без повторного входа. Нельзя переключиться на actor, к которому account не имеет membership.

Экранные данные после switch должны инвалидироваться централизованно; не перезагружай приложение полностью без необходимости. При удалённом или отозванном actor выбери player fallback.

Через iOS-плагин проверь modal/sheet behavior, focus, long organization names и возврат.
Проверки: unauthorized actor negative test, cache invalidation и navigation tests.
Commit: feat: implement secure actor profile switching
```

## 018 — Capability resolver и RLS permissions

```text
Собери единый capability resolver по CAPABILITIES.yaml, ROLES.yaml, ACTORS.yaml и organization memberships.

UI получает canView/canManage/canInvite/canEnterResult/canPayOwn и другие утверждённые capabilities, но server/RLS остаётся окончательным источником права. Добавь policy helpers и отрицательные тесты: чужой owner route, delegate без owner-only result, participant attempting management, revoked member.

Не кодируй права через видимость кнопки בלבד: mutation repository обязан проверять server response. Permission denied имеет отдельное состояние и безопасный back fallback.

Через iOS-плагин проверь скрытие/disabled actions в пяти базовых вкладках после actor switch.
Проверки: resolver matrix и RLS policy tests.
Commit: feat: centralize actor capabilities and permission enforcement
```

## 019 — Аудит Supabase Auth и actor-модели

```text
Audit-only. Не добавляй новые способы входа, профили или роли.

Пройди 010–018: чистая миграция, регистрация, подтверждение email, reset password, session restore, player onboarding, actor switch, revoked membership и permission denied. Проверь, что publishable key допустим в клиенте, а service-role/DB secrets отсутствуют.

Через iOS-плагин выполни cold launch, deep-link verification/reset, keyboard, background refresh и actor switch. Запусти RLS negative tests и generated TypeScript compile.

Исправь только доказанные ошибки этого блока. Отчёт должен разделять passed, failed и manual dashboard setup.
Проверки: full auth integration suite, secret scan, architecture validators.
Commit: test: audit Supabase authentication and actor security
```
