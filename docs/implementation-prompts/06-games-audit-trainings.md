# Блок 6 — тренировки и турниры

## 050 — Training schema и RLS

```text
Создай Supabase migrations для trainings, training_registrations, attendance_records и минимального program metadata по DATA_MODEL.md, ENTITY_LIFECYCLES.yaml и training specs.

Не переиспользуй game matches/participants там, где семантика тренировки отличается. Храни creator actor context, visibility, enrollment/payment policies, time/place и trainer/organization ownership. Attendance mutation доступна только training_manager; participant видит только разрешённую запись.

Поля программы, материалов или повторяемости, которые definition_pending, оставь nullable/feature-gated и не строй UI-логику вокруг них. Сгенерируй types и repository interface.
Проверки: migration reset, RLS guest/participant/trainer/org negatives и constraints.
Commit: feat: add training domain schema and RLS
```

## 051 — Публичная страница тренировки

```text
Подключи training.details к Supabase projection и реализуй guest, participant, trainer и organization_manager variants.

Покажи overview, time/place, trainer/organizer, enrollment/price, confirmed participants в разрешённой проекции и canonical chat для confirmed members. Join flow использует общий JOIN_FLOW resolver, а не отдельную логику. Program/materials отображай только если реальные данные и contract готовы; иначе честный placeholder.

Public screen остаётся read-only; manage entry показывается по capability. Не создавай второй detail screen из каталога или профиля.

Через iOS-плагин проверь variants, sticky CTA, Dynamic Type и deep links.
Проверки: role projection, join flow reuse и chat permission tests.
Commit: feat: implement canonical training details
```

## 052 — Создание тренировки

```text
Реализуй training.create для trainer и organization actors.

Используй общий wizard infrastructure, но не копируй game.create целиком. Минимальные шаги и поля следуют training-create.md: identity/time/place, trainer/format/program baseline, enrollment/price, review/publish. Player actor без capability получает permission state.

Draft persistence, actorId, returnTo, idempotent publish и server revalidation обязательны. Не добавляй recurring schedule, package pricing или lesson plans без утверждённого решения; оставь compatible fields/feature flags.

Через iOS-плагин проверь keyboard, native date/time, dirty draft back и role switch.
Проверки: permission, validation, publish transaction и offline draft tests.
Commit: feat: implement training creation flow
```

## 053 — Управление тренировкой и посещаемость

```text
Реализуй training.manage и training.attendance по существующим routes.

Manage sections подключают overview, registrations/participants, program shell, attendance, payments summary и canonical chat в объёме контракта. Attendance поддерживает present/late/absent, optimistic local draft и explicit save; server создаёт audit event. Offline может хранить unsent draft, но не показывать его authoritative другим пользователям.

Delegate permissions отделены от trainer/owner. Manual online payment status запрещён. Program editor, если definition_pending, остаётся placeholder с стабильным API.

Через iOS-плагин проверь длинный attendance list, keyboard/menus и save feedback.
Проверки: audit, offline reconciliation, RLS и role negatives.
Commit: feat: add training management and attendance
```

## 054 — Tournament schema и engine boundary

```text
Создай Supabase migrations и domain interfaces для tournaments, tournament_entries, teams/pairs, rounds, competition_matches, result_events и published_versions.

Утверждены только formats single_elimination и full_placement. Format strategy отвечает за progression; отдельный match result model не смешивается с генератором. Published round immutable без explicit rollback; correction создаёт audit/version. Final places вычисляются из matches и не вводятся вручную.

Не добавляй round_robin, swiss, groups_then_playoff, separate king tournament, seasons или double elimination. Сгенерируй TypeScript types и property-test harness.
Проверки: migration/RLS и forbidden-format validator.
Commit: feat: establish tournament engine and schema boundary
```

## 055 — Плей-офф на выбывание

```text
Реализуй single_elimination strategy по COMPETITION_FORMATS.yaml.

Поддержи participant/team count >=2, power-of-two bracket, byes для других размеров, manual/rating/random seeding и optional bronze match только при включённой настройке. Total championship matches без bronze = N-1. Next match создаётся/открывается только после authoritative result предыдущего.

Bracket публикация фиксирует seed/version. Correction уже сыгранного матча требует rollback plan и audit, а не silent rewrite. Technical result должен проходить тот же event pipeline.

Через iOS-плагин проверь mobile round columns, horizontal pan и linear fallback.
Проверки: property tests N=2..32, byes, no duplicate participant per round.
Commit: feat: implement single-elimination tournament strategy
```

## 056 — Полное распределение мест

```text
Реализуй full_placement strategy для N=4,8,16,32.

Каждый participant играет ровно log2(N) матчей, один в каждом раунде; winner и loser переходят в соответствующие placement halves. Total matches = N/2 * log2(N). Для 32: 5 раундов, 5 матчей каждой команде, 16 матчей в раунде, 80 всего и уникальные места 1..32.

Round N+1 нельзя публиковать до завершения required results N. Final places derived, immutable without rollback. Добавь path labels для accessible linear representation.

Через iOS-плагин проверь placement map на телефоне без unreadable shrink.
Проверки: property tests всех N, unique places и winner/loser destinations.
Commit: feat: implement full-placement tournament strategy
```

## 057 — Публичная карта турнира

```text
Реализуй tournament.details для guest/participant/organizer на основе TOURNAMENT_VISUAL_MAP.yaml.

Sections: overview, matches, competition map, places, participants, chat. Single elimination использует horizontal bracket; full placement — placement path map с winner/loser paths. На телефоне не уменьшай всю схему до нечитаемого масштаба: round columns/stage carousel плюс обязательный linear list fallback. Participant action «Мой путь» фокусирует связанные matches.

Chat доступен только подтверждённым members. Public data projection не раскрывает private registration/payment fields.

Через iOS-плагин проверь pan, focus, VoiceOver text equivalents и 320/430 pt.
Проверки: map/list parity и role projection tests.
Commit: feat: build accessible tournament details map
```

## 058 — Управление турниром

```text
Реализуй tournament.manage для двух утверждённых форматов.

Подключи registration/teams, seeding/draw, preview, publish round, court/time assignment, result entry, correction/rollback, places и canonical chat. Любой override требует reason и actor context. Только authorized tournament manager меняет progression; result owner policy следует tournament contract.

Не показывай выбор удалённых formats. Full-placement review заранее показывает расчёт нагрузки, включая 32 → 5 раундов → 80 матчей. Publishing mutation idempotent и проверяет incomplete results.

Через iOS-плагин проверь dense tables, bracket preview, confirmation sheets и keyboard.
Проверки: progression integration, audit/version и RLS.
Commit: feat: implement tournament management workflow
```

## 059 — Аудит тренировок и турниров

```text
Audit-only. Не добавляй training/tournament features.

Проверь 050–058: clean migrations, training join/manage/attendance, single elimination, full placement, public maps, linear fallback, result correction, RLS и canonical chat. Для турниров автоматически подтверди: N-1 single-elimination matches без bronze; full-placement 4=4, 8=12, 16=32, 32=80.

Убедись, что удалённые round_robin/swiss/groups/season/king formats отсутствуют в UI, schema enum и tests. Через iOS-плагин пройди training details/attendance и две tournament maps.

Исправляй только доказанные ошибки блока.
Проверки: property/integration suite, validators и accessibility report.
Commit: test: audit trainings and approved tournaments
```
