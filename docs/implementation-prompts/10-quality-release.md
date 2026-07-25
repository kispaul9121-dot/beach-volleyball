# Блок 10 — качество, builds и release candidate

## 090 — Полная unit и component test suite

```text
Закрой критический автоматический test baseline без изменения UX.

Сопоставь domain engines, capability/join resolvers, repositories, format generators и screen state components. Добавь unit/component tests там, где отсутствует защита: auth/session, actor switch, catalog scopes, creation drafts, game formats, tournament strategies, chat reducer, payments, booking и cache. Удали или перепиши flaky tests с доказанной причиной; не маскируй их retry-only настройкой.

Определи минимальные coverage thresholds по критическим модулям, а не искусственные 100% для generated/boilerplate. Test data берётся из semantic fixtures.
Проверки: deterministic repeated runs, no network in unit tests, CI time report.
Commit: test: complete critical unit and component coverage
```

## 091 — Производительность списков и Supabase-запросов

```text
Профилируй реальные bottlenecks, не делай преждевременный массовый refactor.

Проверь play/camps catalogs, profile activity, participants, chat messages и tournament maps. На backend изучи query plans/indexes/pagination; на mobile — renders, list virtualization, image sizes и cache. Добавляй FlashList или другие оптимизации только после измерения и совместимости с Expo.

Установи budgets для initial screen data, repeated query count и scroll responsiveness. Избегай N+1 queries и full-table realtime subscriptions. Сохрани accessibility и stable item keys.

Через iOS-плагин выполни scroll/interaction smoke на large seed.
Проверки: before/after measurements, query plans и regression tests.
Commit: perf: optimize measured mobile and Supabase bottlenecks
```

## 092 — Полная доступность

```text
Проведи accessibility pass по всем implemented screens, не завершая definition_pending features.

Проверь VoiceOver labels/roles/hints, focus order, announcements loading/error/success, Dynamic Type 200%, contrast, Reduce Motion, touch targets 48×48, keyboard navigation where applicable и text alternatives для bracket/placement paths. Статусы не обозначаются одним цветом.

Используй iOS-плагин для фактического VoiceOver/render review и зафиксируй manual findings. Исправь clipping, inaccessible icon-only actions, hidden focus и keyboard-obscured inputs. Не отключай font scaling для сохранения макета.

Проверки: component accessibility queries, screenshot matrix и manual checklist.
Commit: a11y: complete mobile accessibility pass
```

## 093 — iOS regression через плагин

```text
Audit-only для iOS. Используй точный @mention из IMPLEMENTATION_RUNTIME.yaml и фактический simulator/device host.

Пройди cold launch, registration/login, пять tabs, actor switch, game create/join/manage, fixed pairs, Tunisian 3 courts, training attendance, single elimination, full placement, chat keyboard/realtime, camp booking draft и settings appearance. Проверь background/foreground, deep links, safe area, system back gestures, memory warnings where observable и offline transitions.

Не исправляй Android-only или продуктовые пробелы. iOS defects исправляй минимально и добавляй regression test/report.
Проверки: build/launch result, screenshots, routes and failed step evidence.
Commit: test: run Codex iOS plugin regression suite
```

## 094 — Android parity smoke

```text
Проведи Android smoke для критической parity, сохраняя iOS-first процесс и общий React Native codebase.

Пройди пять tabs, auth, game join/create/manage, tournament map, chat keyboard, camp details и settings. Проверь edge-to-edge, hardware back, permissions, keyboard resize и touch feedback. Не вводи отдельный Android visual language и не ломай iOS fixes.

Если Android environment отсутствует, сформируй blocked report и CI/device instructions, не заявляя success. Platform-specific adapter допустим только при доказанной системной разнице.

Проверки: Android build/typecheck, route smoke и parity issue list.
Commit: test: verify Android parity for critical flows
```

## 095 — EAS build profiles и environments

```text
Настрой EAS development, preview и production profiles для существующего Expo app.

Раздели bundle/package identifiers, app variants, environment variables и Supabase project refs. Secrets не хранятся в eas.json или Git; public variables явно перечислены. Добавь development build для iOS plugin/simulator workflow, preview build для QA и production build без автоматической публикации.

Проверь app.config validation, icons/splash references, deep-link schemes и native permission descriptions. Не запускай платный/production build без явного разрешения, если среда требует внешнего действия.

Проверки: config inspect, local/prebuild validation и documented commands.
Commit: build: configure EAS development preview and production profiles
```

## 096 — TestFlight beta readiness

```text
Подготовь iOS beta checklist без отправки в App Store Connect.

Проверь bundle id, version/build strategy, signing responsibility, privacy usage descriptions, icons, splash, supported orientations, deep links, data collection disclosure inputs и test accounts/seed plan. Создай release notes template и список ручных сценариев TestFlight.

Через iOS-плагин или EAS development/preview result проверь production-like launch. Не публикуй build, не принимай agreements и не меняй certificates без отдельной команды пользователя.

Definition_pending функции должны быть скрыты feature flags или честно исключены из beta scope.
Проверки: metadata/config audit и no missing permission strings.
Commit: docs: prepare TestFlight beta readiness checklist
```

## 097 — Backup, recovery и migration plan

```text
Подготовь operational plan для Supabase data без разрушительных действий.

Опиши backup availability текущего plan, migration forward/rollback strategy, restore verification, point-in-time expectations where available, Storage backup considerations и incident ownership. Добавь safe pre-deploy migration checklist и recovery drill для local/preview. Production restore не запускай.

Для irreversible migration требуй explicit backup/approval и staged rollout. Seed scripts блокируются в production. Audit/result/payment event tables сохраняют историю по retention policy, а не удаляются случайным cleanup.

Проверки: dry-run migration, local restore simulation и documentation consistency.
Commit: docs: add database backup and recovery plan
```

## 098 — Финальный архитектурный и продуктовый аудит

```text
Audit-only. Сопоставь фактический код с AGENTS.md, YAML-контрактами, screen specs, DECISIONS.md, IMPLEMENTATION_STATUS.yaml и 000–097.

Найди duplicate canonical screens/chats/tab bars, routes без action, action без destination, permission gaps, schema drift, forbidden formats/seasons, placeholders mislabeled as implemented, hard-coded colors, service secrets и missing tests. Проверь, что approved formats ровно соответствуют текущему MVP.

Исправляй только доказанные несоответствия; product decisions не принимай самостоятельно. Dead code удаляй только при подтверждённых references/tests. Обнови screen readiness из фактических свидетельств.

Проверки: все validators, Supabase reset/RLS, typecheck/lint/tests и architecture report.
Commit: test: complete final architecture and product audit
```

## 099 — Release candidate и итоговый отчёт

```text
Собери release candidate состояния проекта без merge, store publication или production migration.

Запусти clean install, Supabase local reset/seed, generated types check, validators, unit/component/integration suites, iOS regression through plugin, Android smoke where available и EAS config validation. Сформируй один итоговый отчёт: implemented, partial, placeholder, definition_pending, blocked; known risks; manual setup; beta scope; exact commands and commit SHAs.

Release candidate считается готовым только при отсутствии critical security/data-loss/permission defects. Низкоприоритетные unfinished screens остаются честно deferred с compatible foundations.

Не merge PR и не публикуй build без явной команды пользователя.
Проверки: reproducible RC checklist and artifact references.
Commit: chore: assemble VolleyPlay release candidate report
```
