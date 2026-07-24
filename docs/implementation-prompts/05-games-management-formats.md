# Блок 5 — управление игрой и игровые форматы

## 033 — Manage shell и обзор игры

```text
Реализуй game.manage shell и вкладку Обзор.

Прочитай game-manage.md, GAME_MVP.yaml, CAPABILITIES.yaml и ENTITY_SECTIONS.yaml.

Сделай:
1. Server permission guard для entity_manager.
2. Верхнюю панель: back в management catalog, статус, actor-владелец, preview participant page, overflow actions по правам.
3. Ровно четыре раздела: Обзор, Участники, Матчи, Чат.
4. Overview показывает readiness, дату/время, место, формат, заполненность, policies и состояние матчей.
5. Для Тунисской лестницы — площадки, игроков, матчи/цикл, текущий цикл и pending movements.
6. Редактирование общих параметров открывается отдельным action/flow; не превращай overview в форму.
7. Delegated manager видит manage shell, но это не даёт owner-only score commands.

Тесты: owner/manager/no permission, cancelled/completed, stale capability и preview link.

Commit: feat: implement game management overview
```

## 034 — Управление участниками игры

```text
Реализуй вкладку Участники game.manage.

Сделай:
1. Списки confirmed, requests, waitlist и invitations в соответствии со статусами.
2. Имя, фамилия, participation status, payment display и назначение pair/team/court.
3. Add/remove через единый player picker и permission entity_inviter.
4. Approve/decline requests с capacity revalidation.
5. Promote from waitlist authoritative command.
6. Организатор не меняет online payment status вручную.
7. Другие строки показывают только Оплачено/Не оплачено/Бесплатно; чужой Pay action отсутствует.
8. Удаление игрока после генерации матчей показывает impact и следует утверждённой lifecycle policy; не перестраивает матчи молча.

Тесты: duplicate participant, full capacity race, remove with matches, permission loss и payment immutability.

Commit: feat: implement game participant management
```

## 035 — Общая таблица матчей и owner-only ввод счёта

```text
Реализуй reusable GameMatchTable и вкладку Матчи · Статистика без логики конкретного генератора.

Сделай:
1. Mobile compact rows и wide table по контракту.
2. Поля: №, площадка/время, сторона A, счёт, сторона B, статус.
3. Participant, captain и delegated manager получают read-only view.
4. Только entity_owner_actor получает inline score fields, Save, Correct, Generate games и Add game.
5. Save идемпотентен; correction требует причины и audit event.
6. Result status не определяется только цветом.
7. При offline сохранение не показывается как успешное; можно сохранить local draft ввода с явной маркировкой, если архитектура storage это поддерживает.
8. Не реализуй pairing algorithms здесь.

Тесты: permission matrix, validation счёта, double submit, correction audit и 200% text scaling.

Commit: feat: add owner controlled game match table
```

## 036 — Фиксированные пары 2×2

```text
Реализуй domain strategy standard_2x2 и её управление.

Правила продукта: пары фиксированы, по очереди играют друг с другом, результаты сохраняет владелец.

Сделай:
1. Pair assignment из confirmed players; один игрок не может быть в двух парах.
2. При нечётном числе игроков generation блокируется с понятной ошибкой, если запасные не утверждены контрактом.
3. Для трёх пар пример даёт три уникальных матча.
4. Поддержи organizer-defined one or more rounds только если GAME_FORMATS это разрешает; иначе один круг.
5. Ручное добавление матча валидирует стороны и дубликаты, но owner может подтвердить допустимый повтор с явным reason, если контракт допускает.
6. Statistics: played, wins, losses, points for/against/difference; tie-break order только из контракта.

Property tests: N pairs → N(N-1)/2 matches для одного круга, симметрия, уникальность, no self-match.

Commit: feat: implement fixed pair 2x2 games
```

## 037 — Фиксированные команды 4×4 и ручная серия

```text
Реализуй standard_4x4/fixed_team_match без добавления новых правил замен.

Сделай:
1. Team builder с уникальным membership.
2. Для двух команд — один матч или organizer-configured series, если поле существует в контракте.
3. Для большего количества — утверждённый ordered/round-robin match list только внутри разовой игры, не tournament entity.
4. Неполный состав блокирует публикацию/генерацию согласно min team size.
5. Запасные и замены: если definition_pending, сохрани typed optional roster slots и UI placeholder без фактической substitution logic.
6. Match table и owner-only result flow переиспользуются из 035.
7. Statistics по командам; player individual statistics не выдумывать.

Тесты: duplicate player, min roster, series count, manual team edit impact и no tournament bracket.

Commit: feat: implement fixed team game format
```

## 038 — Тунисская лестница: генератор одной площадки

```text
Реализуй чистый domain generator rotation_five для 1 площадки и 5 игроков.

Сделай:
1. Сгенерируй все 15 уникальных match compositions: один отдыхает, остальные делятся на две пары.
2. Для полного 15-match cycle каждый играет 12 матчей, отдыхает 3 раза и является партнёром каждого другого 3 раза.
3. При planned count <15 выбери детерминированный balanced subset.
4. При >15 добавляй seeded shuffled repeated cycles и возвращай warning о повторах.
5. Генератор получает stable player IDs и seed; UI names не участвуют.
6. Не добавляй movement, несколько площадок или сезон.
7. Возвращай explainable metadata для preview fairness.

Property tests для всех перестановок пяти IDs и counts 1,14,15,16,30; никакого игрока дважды в одном матче.

Commit: feat: implement five player tunisian generator
```

## 039 — Тунисская лестница: 2–3 площадки, циклы и переходы

```text
Расширь Тунисскую лестницу на 2/3 площадки, сохраняя generator 038 независимым.

Сделай:
1. Конфигурации только 10→2 и 15→3, ровно 5 на площадке.
2. Initial distribution: manual/rating/random только если перечислено в контракте; иначе manual + deterministic random foundation.
3. Матчи генерируются отдельно по каждой пятёрке и циклу.
4. После завершённого нефинального цикла rank 1 нижней площадки идёт вверх, rank 5 верхней вниз.
5. Все границы рассчитываются одновременно; top leader и bottom last остаются.
6. Owner видит preview и подтверждает movements; delegated manager read-only.
7. Следующий цикл создаётся только после confirmation и получает новые составы.
8. Финальный цикл показывает final positions и не создаёт новый.
9. One date/single event window; season fields запрещены.

Тесты: 2/3 courts, simultaneous swap, tie-break, correction before/after movement и no duplicate player across courts.

Commit: feat: implement multi court tunisian ladder
```

## 040 — Статистика разовой игры

```text
Реализуй derived statistics layer для всех утверждённых игровых форматов.

Источником являются только сохранённые result events; ручной ввод totals запрещён.

Сделай:
1. Общий read model played/wins/losses/points for/against/difference.
2. Для fixed pairs/teams — team standings.
3. Для Тунисской лестницы — individual standings per court/cycle и итоговые positions.
4. Tie-break order берётся из GAME contracts и отображается пользователю.
5. Correction пересчитывает статистику детерминированно.
6. Partial results дают provisional status.
7. Не добавляй глобальный рейтинг игрока или сезонную статистику.
8. Оптимизируй через memoized/read projection только после correctness tests.

Tests: empty, partial, ties, corrections, movement ranks и reproducibility.

Commit: feat: derive one off game statistics
```