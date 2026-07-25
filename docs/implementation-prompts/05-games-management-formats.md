# Блок 5 — страница игры, управление и форматы

## 040 — Game details shell и обзор

```text
Подключи game.details к Supabase projection и сохрани канонический route /games/:gameId.

Собери hybrid navigation: Обзор, Участники, Матчи, Чат. Верхняя часть показывает title, format, organizer, date/time, place/court, capacity и price. Role resolver выбирает guest, invited/requested/waitlisted, participant и organizer presentation без создания отдельных экранов.

Обзор может содержать previews, но не дублирует полные списки. Loading/removed/cancelled/rescheduled/error/offline имеют явные состояния. Публичная страница остаётся read-only даже для owner; управление открывается отдельным action.

Через iOS-плагин проверь tabs, sticky CTA, safe area и deep link.
Проверки: role projection tests и canonical route invariant.
Commit: feat: connect canonical game details shell
```

## 041 — Game details для гостя

```text
Реализуй guest variant game.details по JOIN_FLOW.yaml.

Покажи public preview, формат и правила, свободные места, цену, organizer и единое основное действие «Вступить». Resolver после нажатия определяет immediate/request/payment/waitlist/unavailable. Не показывай полный participant payment status, закрытые данные, chat messages или owner controls.

Для invitation-only без active invitation действие скрыто или заменено понятным статусом. Capacity и policy повторно проверяются сервером перед mutation; offline не подтверждает участие оптимистично.

Через iOS-плагин проверь CTA, no-places/registration-closed states и VoiceOver.
Проверки: join resolver component/integration tests и RLS.
Commit: feat: implement guest game details and join entry
```

## 042 — Game details для приглашённого

```text
Реализуй состояние active unresolved invitation на game.details.

В верхней части покажи restrained success/green block с label ПРИГЛАШЕНИЕ, inviter/organizer и действием «Открыть приглашение». Оно ведёт на invitation.details; accept/decline на game.details запрещены. До принятия пользователь не считается participant, не появляется в Profile activity и не получает chat access.

Invitation details использует authoritative status, expiry и separate accept/decline mutations. Принятие не означает оплату автоматически; после accept resolver применяет payment policy.

Через iOS-плагин проверь блок, expiry state, back и переход после accept.
Проверки: invitation lifecycle и no premature participation/chat tests.
Commit: feat: add invited game details state
```

## 043 — Game details для участника

```text
Реализуй confirmed/payment-required participant variant.

Открой полный список участников в разрешённой проекции, матчи/статистику read-only и canonical conversation. В собственной participant row online_unpaid показывай «Оплатить»; после processing/success заменяй статус без layout jump. За другого участника платить нельзя. Чужие строки показывают только Оплачено/Не оплачено/Бесплатно.

Добавь useful summary «Ваш следующий матч» при наличии данных. Для Тунисской лестницы показывай текущую площадку, цикл и confirmed movements. Editable score controls отсутствуют.

Через iOS-плагин проверь participant tabs, own payment row, chat access и 200% text.
Проверки: own-row permission tests и read-only match UI.
Commit: feat: implement participant game details state
```

## 044 — Game details для организатора

```text
Реализуй organizer/owner presentation на публичной странице без превращения её в editor.

Покажи status «Вы организатор» и primary action «Управлять», ведущий на /games/:gameId/manage после permission revalidation. Preview participant view остаётся доступным из manage header. На game.details не должно быть inline score, add/remove player, regenerate или settings forms.

Delegate manager также может получить manage entry согласно capability, но owner-only result distinction сохраняется. При revoked permission вернуть public details с notice.

Через iOS-плагин проверь organizer/manager variants, deep link к manage и back fallback.
Проверки: no editable controls on public page и permission redirects.
Commit: feat: add organizer entry to game management
```

## 045 — Участники, заявки, waitlist и собственная оплата

```text
Реализуй game.manage → Участники и соответствующий read-only participant section.

Owner/разрешённый manager может approve/decline request, move from waitlist, add player через canonical picker и remove player с audit reason. Online payment status нельзя менять вручную. Participant payment action доступно только owner собственного payment record; manager видит status, но не нажимает чужую оплату.

Все mutations idempotent, проверяют capacity и current status на сервере. Concurrent approval последнего места должен дать один success и корректный waitlist result.

Через iOS-плагин проверь длинный список, swipe/menus если используются, confirmation sheets и own payment row.
Проверки: concurrency, RLS и audit event tests.
Commit: feat: implement game participant and request management
```

## 046 — Фиксированные пары 2×2

```text
Реализуй game format fixed_pairs_2v2 как разовую игру, не как tournament round-robin format.

Owner формирует фиксированные пары из confirmed participants, задаёт порядок матчей или генерирует «каждая пара с каждой» внутри одной игры. При трёх парах получается три матча. Пары не меняются автоматически между матчами. Нечётный/неполный состав блокирует generation с понятной ошибкой.

Матчи сохраняются через game match repository; statistics считает played/wins/losses/points/difference по утверждённому порядку. Score editable только actor-owner.

Через iOS-плагин проверь compact match rows и score input keyboard.
Проверки: generator invariants, duplicate match prevention и owner-only mutation.
Commit: feat: implement fixed-pairs 2v2 game format
```

## 047 — Тунисская лестница

```text
Реализуй one-off Tunisian ladder строго по GAME_TUNISIAN_LADDER.yaml.

Конфигурации: 1 площадка/5 игроков, 2/10, 3/15. Organizer задаёт positive match_count_per_court и cycle_count; default 15 матчей. Для каждой пятёрки полный цикл из 15 уникальных compositions обеспечивает 12 игр и 3 отдыха каждому, три партнёрства с каждым другим. При >15 добавляются shuffled repeated cycles с предупреждением.

После завершения цикла одновременно вычисляй leader up и last down по каждой границе, показывай preview и требуй owner confirmation. Следующий цикл генерируется после движения; после последнего — final positions. Сезон не создаётся.

Через iOS-плагин проверь 1/2/3 court UI, cycle/court switchers и readable standings.
Проверки: property tests генератора и simultaneous movement.
Commit: feat: implement one-off Tunisian ladder engine
```

## 048 — Owner-only результаты, correction и audit

```text
Реализуй game.manage → Матчи/Статистика и owner-only result entry.

Только actor-владелец видит editable score, «Сформировать игры», «Добавить игру», save и correction. Delegate manager, captain и participant получают read-only rows. Первый сохранённый result блокирует silent regeneration; reset требует destructive confirmation и audit reason. Correction создаёт immutable result event/version с actor/user/time/reason.

Server mutation повторно проверяет owner capability и match status. Concurrent save обрабатывается version check. Statistics обновляется из authoritative result events, а не локального ввода.

Через iOS-плагин проверь numeric keyboard, row layout, correction sheet и disabled states.
Проверки: permission negative tests, optimistic conflict и audit history.
Commit: feat: enforce owner-only game results and audit trail
```

## 049 — Аудит разовых игр

```text
Audit-only. Не добавляй новые game formats.

Проверь 040–048 для guest, invited, requested, waitlisted, participant, delegate manager и owner. Пройди join/payment visibility, canonical chat, participant management, fixed pairs, Tunisian 1/2/3 courts, owner-only results, correction/reset и offline behavior.

Запусти property tests: fixed pair combinations; Tunisian 15 unique matches, balanced rests/partners, repeated cycles, simultaneous movements. Проверь запрет сезонов и отсутствие tournament bracket на one-off game.

Через iOS-плагин выполни сквозной game flow и screenshot key states.
Проверки: RLS, format validators, navigation/action validators и regression report.
Commit: test: audit one-off game flows and formats
```
