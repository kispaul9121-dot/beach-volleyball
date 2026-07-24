# Блок 10 — качество, безопасность и выпуск

## 073 — Аудит полноты состояний экранов

```text
Audit-only. Сопоставь SCREENS.yaml, SCREEN_READINESS.yaml, specs и фактический код.

Для каждого реализованного/partial экрана проверь применимые состояния: loading, empty, error, offline, permission denied, cancelled/closed и stale data. Не создавай универсальный экран, если состояние требует контекста; переиспользуй общие primitives.

Definition_pending экраны не повышай до implemented из-за placeholder. Исправь IMPLEMENTATION_STATUS evidence и добавь тесты для отсутствующих состояний только в уже реализованных областях.

Сгенерируй отчёт по screen_id: missing state, риск, файл и тест. Не расширяй бизнес-функции.

Commit: test: audit screen state completeness
```

## 074 — Навигация, actions и canonical screens

```text
Audit-only. Запусти/расширь validators для SCREENS.yaml, ROUTES.yaml, ACTIONS.yaml и реального Expo Router tree.

Найди:
- route без screen_id или наоборот;
- pressable без action_id/явного local UI action;
- action с несуществующим destination;
- stack screen без back_fallback;
- duplicated canonical details;
- create/manage route без actor/permission handling;
- returnTo/open redirect risk;
- второй tab bar;
- stale route из удалённых seasons/formats.

Добавь automated route registry test и deep-link smoke suite. Исправь только навигационные дефекты.

Commit: test: validate implementation navigation graph
```

## 075 — Accessibility аудит

```text
Проведи accessibility audit без изменения продуктового scope.

Проверь iOS VoiceOver и Android TalkBack semantics:
- доступные имена/роли/состояния;
- 48×48 targets;
- порядок focus;
- modal focus trap/return;
- status не только цветом;
- формы имеют labels/errors;
- charts/brackets/ladders имеют текстовый эквивалент;
- 200% text scaling;
- Reduce Motion;
- announcement после submit/payment/result.

Добавь automated accessibility/component checks, но не полагайся только на snapshots. Составь ручной checklist по ключевым flows и исправь подтверждённые проблемы.

Commit: fix: complete mobile accessibility audit
```

## 076 — Responsive, safe areas и клавиатура

```text
Audit-only для widths 320, 360, 390, 430, tablet max width, iOS safe areas и Android edge-to-edge.

Проверь:
- bottom tab и sticky CTA не перекрываются;
- keyboard не закрывает active input/action;
- chips используют horizontal scroll без wrap;
- tournament map scroll не конфликтует с vertical screen;
- long Russian names, locations и prices;
- landscape/split screen не ломают critical actions;
- cards не имеют бессмысленных fixed heights.

Добавь visual/component tests там, где tooling позволяет, и исправь layout без изменения navigation/content hierarchy.

Commit: fix: harden responsive mobile layouts
```

## 077 — Offline, retry и stale data

```text
Проведи сквозной resilience audit.

Классифицируй operations:
- read cached;
- reversible local draft;
- authoritative mutation;
- external provider flow.

Правила:
- join, publish, payment success, result save и movement confirmation не подтверждаются оптимистично offline;
- local unsynced drafts имеют явный status;
- retries используют idempotency keys;
- stale server version вызывает conflict UI;
- cache не раскрывает данные после permission revoke/logout;
- reconnect invalidates только нужные queries.

Добавь network fault integration tests и исправь ложные success states. Не внедряй сложный offline-first sync для всего приложения.

Commit: fix: harden offline and retry behavior
```

## 078 — Security и permission penetration review

```text
Audit-only с отрицательными тестами на клиентском и service/API contract уровне.

Проверь:
- подмена actorId/entityId/participantId/paymentId;
- доступ к чужим manage routes;
- delegated manager вводит game result;
- participant платит за другого;
- invited/requested читает chat;
- organization member видит finance без grant;
- private entity через guessed deep link;
- stale cached sensitive data после logout/actor revoke;
- client-only permission checks;
- logging secrets/PII.

UI hiding не считается защитой. Зафиксируй server enforcement requirements, если backend отсутствует. Исправь только реальные уязвимости/контракты.

Commit: security: audit permissions and data isolation
```

## 079 — Производительность и устойчивость списков

```text
Проведи performance audit на типичных и крайних fixtures.

Проверь catalogs, participants, chats, notifications, 80-match tournament и activity feed.

Сделай:
- profile renders и query waterfalls;
- stable keys/memoization только по измерениям;
- FlatList virtualization и pagination;
- image sizing/cache policy;
- no full 80-match render одновременно;
- no repeated derived statistics on every row;
- cleanup subscriptions/timers;
- startup bundle dependency review.

FlashList добавляй только после доказанного bottleneck. Добавь performance budgets/benchmarks, которые стабильны в CI, и исправь критические проблемы без premature rewrite.

Commit: perf: optimize measured mobile bottlenecks
```

## 080 — Финальный MVP audit и честный backlog

```text
Финальный audit-only промт. Не добавляй новую функцию.

1. Запусти полный verify и все e2e/property tests.
2. Сопоставь IMPLEMENTATION_STATUS со всеми 54 screen_id и инфраструктурными блоками.
3. Проверь основные flows: auth/onboarding; actor switch; discovery/invitation; game create/details/manage; 2x2/4x4/Tunisian; training; two tournament formats; chat; own payment; camps; organization shell.
4. Убедись, что deleted product features нигде не доступны.
5. Составь docs/MVP_RELEASE_REPORT.md: completed, partial, blocked, known risks, manual test matrix и release prerequisites.
6. Создай приоритизированный backlog только из реально незавершённого; не называй placeholder готовым.
7. Обнови README с командами запуска/проверки и фактическим scope.
8. Не публикуй в stores, не включай auto-merge и не меняй production credentials.

Release candidate считается готовым только если critical security/data-loss issues отсутствуют; остальные ограничения явно перечислены.

Commit: docs: finalize mvp implementation audit
```