# Блок 9 — база, cache, безопасность и интеграция

## 080 — Повторяемые Supabase migrations и окружения

```text
Приведи все Supabase migrations к воспроизводимому состоянию.

Новый разработчик или Codex session должен суметь выполнить local start/reset/seed и получить ту же схему без ручного SQL в Dashboard. Раздели local, preview и production configuration; production mutation никогда не запускается без явного project ref и подтверждения. Добавь migration naming/order policy и CI check clean reset.

Не squash уже применённые remote migrations без отдельного решения. Любая ручная dashboard настройка должна быть экспортирована в migration или записана как explicit external setup.
Проверки: clean database reset, migration status, generated types diff и no secrets.
Commit: chore: make Supabase environments reproducible
```

## 081 — RLS negative test suite

```text
Создай автоматический набор негативных Supabase policy tests для ключевых ролей.

Сценарии: anonymous guest, authenticated stranger, requested/waitlisted user, confirmed participant, delegate manager, actor-owner и organization member. Проверь games, trainings, tournaments, camps, profiles, conversations, payments и organization data. Особое внимание: чужой manage, owner-only game result, чужая payment row, unresolved invitation chat, private public-profile fields и privilege escalation.

Тесты должны работать на локальной базе после reset/seed и завершаться fail при неожиданном доступе. Не заменяй server policy проверкой UI visibility.
Проверки: полный negative suite и понятные policy names в отчёте.
Commit: test: add comprehensive Supabase RLS denial matrix
```

## 082 — Генерация TypeScript типов из базы

```text
Настрой генерацию TypeScript database types из фактической Supabase schema.

Сгенерированный файл не редактируется вручную. Domain models и mappers могут сужать/переименовывать поля, но не дублируют таблицы conflicting interfaces. Добавь script/check, который обнаруживает outdated generated types после migration. Repository implementations используют typed client без pervasive any/casts.

Не протаскивай raw database row напрямую во все UI-компоненты; сохраняй domain/read projection boundaries. Document generated path и команду в runbook/runtime.
Проверки: generation idempotency, typecheck и deliberate schema-change failure test.
Commit: chore: generate and validate Supabase TypeScript types
```

## 083 — Seed и demo-сценарии

```text
Создай детерминированный development seed, покрывающий основные сценарии без production данных.

Нужны accounts/actors, пять вкладок, public/private games, invitation/request/waitlist, fixed pairs, Tunisian 1/2/3 courts, training, single-elimination tournament, full-placement 32 teams/80 matches, chats, payment states, camp и organization roles. Используй stable ids и dates relative к seed anchor.

Seed можно безопасно запускать только local/explicit preview. Production guard должен блокировать его. Fixtures UI и database seed используют общие semantic scenario names, но не обязаны иметь один storage format.

Через iOS-плагин запусти app на seed и проверь доступность ключевых routes.
Проверки: repeat seed, unique constraints и no real PII.
Commit: test: add deterministic end-to-end demo seed
```

## 084 — Локальный read cache через Expo SQLite

```text
Добавь Expo SQLite cache только для read-heavy projections: catalogs, profile activity, chat summaries и event details.

Supabase остаётся source of truth. Cache хранит schema version, fetched_at, actor/account scope и stale marker. Offline показывает last-success data с явной подписью и запрещает security-sensitive mutations. При sign-out/actor permission change очищай или изолируй соответствующий scope.

Не создавай полноценную offline-first синхронизацию, background writes или собственную локальную копию всей Postgres schema. Добавь cache repository decorator, migration и size/TTL policy.

Через iOS-плагин проверь airplane/offline launch и reconnect refresh.
Проверки: cache isolation, stale display и logout cleanup.
Commit: feat: add scoped Expo SQLite read cache
```

## 085 — Сеть, retry, cancellation и idempotency

```text
Стандартизируй сетевой слой поверх repositories.

Добавь request timeout, AbortController/cancellation, retry только для безопасных reads и явно idempotent mutations, exponential backoff with jitter и единое error mapping. Каждая create/publish/send/payment mutation использует idempotency key, где это предусмотрено. UI не должен повторно отправлять запрос после unmount или actor switch.

Не retry authentication failure, permission denied, validation error или non-idempotent destructive mutation автоматически. Offline queue допускается только для явно разрешённых local drafts.

Через iOS-плагин проверь slow network/offline/reconnect states.
Проверки: fake timer/retry tests и duplicate mutation prevention.
Commit: feat: standardize resilient network behavior
```

## 086 — Логи, диагностика и privacy redaction

```text
Создай structured logging interface для client и Edge Functions.

Логи содержат severity, event name, correlation/request id, route/feature и safe metadata. Email, tokens, payment secrets, message text, documents и private profile fields редактируются или не логируются. Development console adapter и production adapter разделены; конкретный analytics/crash vendor остаётся plugin/adapter decision.

Добавь correlation id от mobile mutation до Edge Function/database audit where possible. Пользовательские ошибки остаются понятными и не показывают raw SQL/provider response.

Проверки: redaction unit tests, no console secrets и error boundary integration.
Commit: feat: add privacy-safe structured diagnostics
```

## 087 — Mobile secrets и security hardening

```text
Проведи security implementation pass без изменения продукта.

Проверь .env, Expo public variables, SecureStore/SQLite usage, deep-link validation, auth token lifecycle, screenshot/log/clipboard leakage, Storage signed URLs и Edge Function secrets. Publishable Supabase key допустим только при корректном RLS; service-role и provider secrets запрещены в bundle.

Добавь secret scanning, dependency audit policy, safe external URL opener и input/output validation boundaries. Не обещай jailbreak/root protection как абсолютную безопасность; server policies остаются решающими.

Через iOS-плагин проверь app switcher sensitive screens и malformed deep links, если plugin capabilities позволяют.
Проверки: secret scan, bundle config review и RLS suite.
Commit: security: harden mobile and Supabase secret boundaries
```

## 088 — Матрица скриншотов через iOS-плагин

```text
Используй фактический iOS-плагин из IMPLEMENTATION_RUNTIME.yaml для систематической визуальной проверки, не для нового дизайна.

Сними пять root tabs и ключевые detail states: guest/participant/organizer game, Tunisian 3 courts, training, single elimination, full placement, chat keyboard, camp booking и organization shell. Размеры минимум 320-equivalent и 430-equivalent, light primary и dark secondary, normal и 200% text для выбранных critical screens.

Сохрани screenshots/manifest только если repository policy позволяет; иначе сформируй markdown report с route, seed identity, device/runtime и результатом. Не принимай макет без фактического render.
Проверки: clipping, safe area, contrast, touch targets и unreadable bracket.
Commit: test: capture iOS plugin visual regression matrix
```

## 089 — Интеграционный аудит mobile/backend

```text
Audit-only. Не добавляй features или новые tables.

Проверь 080–088: clean migrations, generated types, deterministic seed, RLS denial matrix, SQLite cache isolation, retry/idempotency, diagnostics redaction, secret boundaries и iOS screenshot matrix. Выполни clean checkout bootstrap по документации настолько, насколько среда позволяет.

Пройди один end-to-end путь с реальным Supabase local/preview: register → profile → create/join game → participant view → chat → sign-out/offline cache. Отдельно проверь actor switch и permission invalidation.

Исправляй только доказанные интеграционные ошибки. Manual/credential blockers перечисляй отдельно.
Проверки: full CI, Supabase reset, iOS smoke и security report.
Commit: test: audit mobile Supabase integration baseline
```
