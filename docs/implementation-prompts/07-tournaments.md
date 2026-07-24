# Блок 7 — турниры

## 049 — Tournament engine boundary

```text
Создай tournament domain boundary по COMPETITION_FORMATS.yaml и TOURNAMENT_VISUAL_MAP.yaml.

Поддерживаются только:
- single_elimination;
- full_placement.

Сделай strategy interface: validate config, seed participants, generate initial structure, accept immutable result event, derive next round/path, calculate final places и produce public read model.

Раздели tournament progression и правила отдельного volleyball match. Published round versioned; correction создаёт audit. Не добавляй round robin, Swiss, groups, seasons, King tournament или double elimination.

Тесты: unsupported format rejection, stable participant IDs, incomplete-result blocking и deterministic seeded output.

Commit: feat: add tournament strategy engine boundary
```

## 050 — Создание турнира: сокращённый мастер

```text
Реализуй tournament.create с максимально ясным мастером, используя существующий spec, но показывая только два формата.

Рекомендуемые логические шаги: Основное; Участники и формат; Площадки и расписание; Регистрация и цена; Проверка и публикация. Не меняй route.

Сделай:
1. Create as и capabilities.
2. Fixed pairs/teams participant unit.
3. Format cards с expected rounds/matches.
4. Для full placement разрешены только 4/8/16/32; 32 показывает 5 раундов, 5 матчей на команду, 80 всего.
5. Seeding manual/rating/random по контракту.
6. Venue/court slots и schedule feasibility check.
7. Enrollment/payment shared flow.
8. Definition_pending advanced referees/streaming оставь typed placeholders.

Тесты: unsupported formats hidden/rejected server-side, count validation, draft resume и publish idempotency.

Commit: feat: implement two format tournament creation
```

## 051 — Single elimination algorithm

```text
Реализуй чистую strategy single_elimination.

Сделай:
1. Participant count minimum 2.
2. Power-of-two bracket; non-power counts получают byes по выбранной seeding policy.
3. Каждый проигравший выбывает из championship path.
4. Total matches без bronze = N-1.
5. Optional third-place match только если config разрешает.
6. Следующий match не готов до обязательного результата.
7. Published bracket не перестраивается без rollback.
8. Technical result/withdrawal обрабатываются через result event, не прямое перемещение.

Property tests для counts 2–64: один champion, no duplicate in round, all paths terminate, byes do not create fake played match.

Commit: feat: implement single elimination strategy
```

## 052 — Single elimination UI и управление

```text
Реализуй tournament.details/manage presentation для single elimination.

Public/participant:
- overview, matches, bracket, participants, chat;
- Мой следующий матч и `Мой путь` для participant;
- horizontal round columns или stage carousel;
- линейный accessible fallback всегда доступен.

Manage:
- registration, seeding preview, draw publish, round lifecycle, result entry по tournament roles, correction/audit и finalization.

Не уменьшай всю сетку до нечитаемого размера. Не копируй интерфейс Google. Unpublished preview визуально отделён.

Тесты: mobile pan, screen reader path text, bye display, match result advances once, correction updates downstream preview safely.

Commit: feat: implement single elimination tournament experience
```

## 053 — Full placement algorithm

```text
Реализуй strategy full_placement для N=4,8,16,32.

Инварианты:
- rounds = log2(N);
- каждый участник играет ровно один матч в каждом раунде;
- matches per round = N/2;
- total = N/2 * log2(N);
- победитель идёт в upper placement half, проигравший — в lower;
- в конце каждый получает уникальное место 1..N.

Для 32: 5 раундов, 16 матчей/раунд, 80 матчей.

Сделай explainable path IDs и validation before publish. Другие counts отклоняются в MVP, не создавай preliminary rounds.

Property/generative tests для всех supported N, random result combinations, correction rollback и no duplicate participant.

Commit: feat: implement full placement strategy
```

## 054 — Full placement карта на мобильном

```text
Реализуй tournament map для full_placement по TOURNAMENT_VISUAL_MAP.yaml.

Покажи раунды, match cards, winner/loser destination, placement matches и final places. Используй горизонтальные колонки/карусель и focus `Мой путь`; линейный список обязателен.

Для 32 команд интерфейс не должен пытаться показать все 80 карточек одновременно. Используй progressive disclosure по раунду и участнику, sticky round header и summary progress.

Color не единственный признак upper/lower path; добавь текст/иконки. Поддержи live, delayed, completed, technical, disputed и cancelled.

Тесты: 320px, 200% text, Reduce Motion, keyboard/screen-reader navigation и path consistency с engine.

Commit: feat: implement mobile full placement map
```

## 055 — Competition match details и result commands

```text
Реализуй competition.match как canonical экран турниров.

Покажи participant/team composition, round/stage, court/time, score, status, next destination и result history. Participant видит read-only; tournament-specific authorized role получает result entry/correction actions.

Не применяй owner-only rule разовой игры автоматически к турниру: используй tournament role capabilities. Result confirmation/conflict flow добавляй только если прямо указан контрактом; иначе не выдумывай.

Correction требует reason и пересчитывает downstream paths с audit. Если downstream match уже начался, применяй rollback/block policy и объясняй impact.

Тесты: role matrix, deep link, stale result version, correction impact, technical result и canonical back.

Commit: feat: implement competition match details
```

## 056 — Контрольный аудит турниров

```text
Audit-only. Проверь create, single elimination, full placement, match details и management.

Обязательные assertions:
- UI/API принимают только два format ID;
- 32 full placement всегда 80 матчей и 32 уникальных места;
- single elimination N участников даёт N-1 матч без bronze;
- participant не встречается дважды в раунде;
- unpublished changes не попадают public read model;
- next round blocked при missing results;
- correction имеет audit и безопасный downstream handling;
- tournament map имеет линейный fallback;
- Tunisian ladder не появляется как tournament.

Добавь cross-strategy property tests и исправь только дефекты. Обнови IMPLEMENTATION_STATUS.

Commit: test: audit tournament strategies and ui
```