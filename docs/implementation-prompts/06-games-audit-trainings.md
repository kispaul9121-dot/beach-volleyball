# Блок 6 — аудит игр и тренировки

## 041 — Коррекция результатов, reset и аудит игры

```text
Реализуй безопасный lifecycle изменения матчей после начала игры.

Сделай:
1. Correction сохранённого результата доступна только owner и требует reason.
2. Audit record содержит actor, user, old/new result, timestamp и causation ID.
3. Повторная генерация после первого сохранённого результата блокируется до явного full reset.
4. Reset preview показывает удаляемые results/statistics/movements и требует подтверждения.
5. Для Тунисской лестницы коррекция результата, повлиявшего на уже подтверждённый movement, не перестраивает историю молча: применяй утверждённую rollback policy или блокируй с понятной причиной.
6. Completed game не редактируется без отдельного reopen permission, если оно существует.
7. Delegated manager не получает эти commands.

Тесты: concurrent correction, stale version, rollback chain, audit immutability и permission negatives.

Commit: feat: secure game result corrections and reset
```

## 042 — Сквозной аудит игр

```text
Audit-only. Пройди создание → публикацию → вступление → оплату собственного участия → управление составом → генерацию → ввод результатов → статистику → завершение → архив.

Отдельно проверь:
- 2×2 fixed pairs;
- 4×4/fixed teams;
- Tunisian 1, 2 и 3 courts;
- owner, delegated manager, participant и guest;
- invitation, request, waitlist, online/external/free payment;
- direct deep links и permission loss.

Добавь e2e/integration tests с deterministic fixtures. Не добавляй новые возможности. Любая найденная архитектурная неоднозначность оформляется как TODO/blocked status, а не самовольное правило.

Проверь validators, 320px, 200% text scaling, offline и canonical chat identity. Обнови IMPLEMENTATION_STATUS.

Commit: test: complete one off game audit
```

## 043 — Training domain boundary и honest placeholders

```text
Подготовь training feature по training specs, не копируя game feature.

Сделай типы Training, ProgramItem, AttendanceRecord, TrainingParticipant и permissions; repository/use-case interfaces details/create/manage/attendance.

Переиспользуй enrollment/payment/chat infrastructure, но не match generation. Если программа, материалы или attendance rules definition_pending, зафиксируй typed extension points и status placeholders без fake logic.

Trainer и organization могут создавать training только по capability. Player не получает create route.

Тесты: schema, permission matrix, lifecycle и separation from Game/Tournament.

Commit: feat: add training domain boundary
```

## 044 — Создание тренировки

```text
Реализуй training.create по утверждённой спецификации и существующим действиям.

Сделай step flow только из spec: create as, basics/time, venue, capacity, enrollment/payment, optional program, participants/invitations и review/publish.

Правила:
- player actor не может создать training;
- одно временное окно, без сезона;
- visibility и enrollment разделены;
- online payment требует payout readiness;
- player picker не создаёт участие до publish/explicit add;
- definition_pending advanced program fields сохраняются как unsupported, не показываются рабочими.

Тесты: trainer/organization, draft resume, publish validation, invite-only и unavailable finance.

Commit: feat: implement training creation flow
```

## 045 — Страница тренировки по ролям

```text
Реализуй training.details variants guest, participant, trainer owner и organization manager.

Общие данные: organizer, trainer, date/time, venue, capacity, price, enrollment, program preview и participants visibility.

Guest: join action и без chat/payment statuses.
Participant: own status/payment, full allowed participants, program/materials по контракту, event chat.
Owner/manager: view mode + Управлять, без inline manage fields.

Не добавляй match table. Attendance после события показывается только если контракт разрешает участнику.

Тесты: role variants, private visibility, cancelled/moved, own payment и chat access.

Commit: feat: implement canonical training details
```

## 046 — Управление тренировкой

```text
Реализуй training.manage shell и утверждённые разделы: overview, participants, program, attendance entry, payments summary, chat/announcements — только если они перечислены spec/ENTITY_SECTIONS.

Переиспользуй participant/payment components, но не позволяй ручную подмену online payment status.

Сделай request/waitlist/invitation management, program editing с version-safe save и link на отдельный attendance screen. Delegated staff capabilities проверяются по command, а не по видимости вкладки.

Definition_pending materials/recurrence/advanced packages оставь extension slots.

Тесты: owner/authorized staff/no permission, program conflict, participant removal и completed state.

Commit: feat: implement training management
```

## 047 — Посещаемость тренировки

```text
Реализуй training.attendance как отдельный screen с permission training_manager.

Сделай:
1. Список confirmed participants.
2. Статусы present, late, absent и unmarked только если утверждены контрактом; не добавляй медицинские причины.
3. Batch save с optimistic UI только при reversible local state и authoritative confirmation.
4. История изменений/audit для corrections.
5. Offline draft допустим с явным unsynced status; он не считается сохранённой attendance.
6. Participant self-marking отсутствует, если не утверждено.
7. Completed training поддерживает allowed correction policy.

Тесты: batch partial failure, duplicate records, permission loss, offline sync и accessibility list actions.

Commit: feat: implement training attendance
```

## 048 — Контрольный аудит тренировок

```text
Audit-only. Проверь training create/details/manage/attendance и shared join/payment/chat.

Критические проверки:
- player не создаёт training;
- trainer/organization actor не получают чужое управление;
- программа не превращается в match schedule;
- attendance records уникальны per participant/training;
- guest не видит chat/payment statuses;
- online payment immutable manually;
- definition_pending блоки честно помечены;
- canonical routes/back fallbacks;
- screen states и accessibility.

Добавь integration tests и исправь только training defects. Обнови IMPLEMENTATION_STATUS.

Commit: test: audit training flows
```