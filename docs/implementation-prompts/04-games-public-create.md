# Блок 4 — база игр, каталог и создание

## 030 — Game schema, registration и RLS

```text
Создай Supabase migrations для games, game_participants, game_invitations, join_requests, waitlist и draft metadata по GAME_MVP.yaml, JOIN_FLOW.yaml и DATA_MODEL.md.

Разделяй visibility, enrollment policy и payment policy. Храни created_by_user_id, created_by_actor_id/type, одно временное окно, venue/court references и status lifecycle. Добавь constraints, indexes и RLS: public catalog видит только public published games; private relation — только разрешённым пользователям; manage mutations — только capabilities.

Не добавляй сезоны, recurring days или tournament tables. Сгенерируй TypeScript types и repository interfaces.
Проверки: migration reset, RLS guest/participant/owner/delegate negatives, schema invariant tests.
Commit: feat: add game registration schema and RLS
```

## 031 — Каталог play.main из Supabase

```text
Подключи основу play.main из промта 002 к Supabase read models.

Сделай paginated queries для категорий Игры/Тренировки/Турниры и scopes Все/Участвую/Управляю согласно GAMES_CATALOG.yaml. В «Все» попадают только public published entities. Участвую строится по relation, Управляю — по capabilities. Не смешивай unresolved invitation с confirmed participation.

Карточки используют общий EntityCard, stable sorting и query cache. Добавь pull-to-refresh только там, где он не конфликтует с management/archive gesture.

Через iOS-плагин проверь scroll, category chips, loading skeleton, empty/error/offline и actor switch refresh.
Проверки: query/RLS integration, pagination и duplicate suppression.
Commit: feat: connect play catalog to Supabase
```

## 032 — Приоритетный блок приглашений

```text
Реализуй invitation discovery block над каталогом по INVITATION_DISCOVERY.yaml.

Показывай заголовок «Вас пригласили · N», максимум две карточки, semantic success/green border/tint, MailPlus и label ПРИГЛАШЕНИЕ. В каталоге единственное действие карточки — «Открыть», ведущее в invitation.details. Accept/decline здесь запрещены.

Supabase query возвращает active unresolved invitations для account, а не active actor только. Нерешённое приглашение не создаёт profile activity participation и не открывает event chat.

Через iOS-плагин проверь zero/one/two/many states, accessibility text и переход.
Проверки: query status mapping, no accidental accept mutation, RLS.
Commit: feat: add priority invitation discovery block
```

## 033 — Режим управления и pull-down архив

```text
Подключи management mode play.main к реальным managed entities и drafts.

Фильтры: Все, Черновики, Требуют действий, Опубликованы, Идут. Completed entities автоматически доступны через архивный mode, а не постоянную вкладку. Реализуй pull-down reveal/armed thresholds из MANAGEMENT_CENTER.yaml, отключи pull-to-refresh в management mode и добавь accessibility action «Открыть архив» и Reduce Motion fallback.

Manage card ведёт на канонический /manage route с permission revalidation. Profile activity не получает эти controls.

Через iOS-плагин проверь gesture conflict, haptics only if approved, scroll и back from archive.
Проверки: state/gesture tests и unauthorized manage route.
Commit: feat: implement contextual management mode and archive gesture
```

## 034 — Мастер создания игры — shell и draft

```text
Реализуй game.create как мастер ровно из четырёх шагов: Что и когда; Место и формат; Участие и цена; Проверка и публикация.

Сохраняй draft в local repository и Supabase drafts только после auth/backend availability. Обязательны actorId, returnTo, «Создать как», resume после закрытия и безопасное удаление draft. UI stepper не создаёт отдельные routes, если контракт их не требует.

Не реализуй поля следующих промтов; добавь typed form model, placeholders и validation boundary. Permission resolver проверяет возможность создания active actor.

Через iOS-плагин проверь keyboard, swipe-back protection при dirty draft, resume и safe area CTA.
Проверки: draft state-machine и navigation tests.
Commit: feat: build four-step game creation shell
```

## 035 — Создание игры: «Что и когда»

```text
Реализуй первый шаг game.create.

Поля: название, короткое описание при наличии контракта, дата, start/end одного временного окна. Используй native date/time controls через совместимые Expo modules и timezone-safe serialization. Запрети end <= start, прошедшую публикацию и пустое название; draft может хранить неполное значение.

Не добавляй recurring rule, сезонный диапазон или несколько игровых дней. Ошибки показываются рядом с полями и в summary для accessibility.

Через iOS-плагин проверь date/time picker, locale ru-RU, keyboard и 200% text.
Проверки: validation/timezone unit tests и resume draft.
Commit: feat: implement game creation timing step
```

## 036 — Создание игры: «Место и формат»

```text
Реализуй второй шаг game.create по GAME_FORMATS.yaml и GAME_TUNISIAN_LADDER.yaml.

Поля: venue/place, court/count where applicable, формат разовой игры и форматные параметры. Показывай только утверждённые режимы: фиксированные пары 2×2, фиксированные команды 4×4 и Тунисская лестница. Для лестницы доступны 1/2/3 площадки и автоматически ожидаются 5/10/15 игроков, но матчи на площадку и циклы вводятся отдельно.

Не показывай удалённые tournament formats и сезоны. Venue picker может быть repository-backed placeholder, если каталог площадок не готов.

Через iOS-плагин проверь conditional fields и keyboard.
Проверки: format validation matrix и no forbidden options.
Commit: feat: implement game venue and format step
```

## 037 — Создание игры: «Участие и цена»

```text
Реализуй третий шаг по JOIN_FLOW.yaml.

Visibility: публичная/непубличная. Enrollment policy: сразу записываются, отправляют заявку, только по приглашению. Payment policy: бесплатно, онлайн, организатору вне приложения. Эти измерения независимы. Добавь capacity, waitlist toggle и price/currency only when applicable.

Online payment publish остаётся blocked/definition_pending, если payout/provider не настроен; не симулируй оплату. External payment не создаёт platform payment record. Сервер повторно проверит policies при публикации.

Через iOS-плагин проверь radios/switches, conditional price field и accessibility.
Проверки: combination matrix и validation tests.
Commit: feat: implement game enrollment and pricing step
```

## 038 — Проверка и публикация игры

```text
Реализуй четвёртый шаг и transactional publish.

Review показывает creator actor, дату/время, место, формат, capacity, join/payment policies и предупреждения. Перед mutation сервер повторно валидирует permission, capacity model, format constraints и payment readiness. Double tap/retry использует idempotency key; при ошибке draft сохраняется.

После успеха создай game, owner participant/manager relation по контракту, canonical conversation при publish policy и переход на game.details. Не создавай матчи автоматически, если формат требует отдельного действия owner.

Через iOS-плагин проверь sticky CTA, loading, error retry и success navigation.
Проверки: integration/idempotency tests и RLS.
Commit: feat: publish validated game drafts
```

## 039 — Аудит каталога и создания игры

```text
Audit-only. Не добавляй новые форматы или поля.

Проверь 030–038: schema/RLS, public/participating/managing queries, invitation block, archive gesture, draft lifecycle, четыре шага, forbidden seasons, payment readiness и transactional publish. Создай smoke seed и пройди создание public free game, private invite-only game и Tunisian ladder draft.

Через iOS-плагин проверь каталог, management gesture, мастер на 320/430 pt, native date/time, keyboard и offline error.

Исправляй только доказанные дефекты категории. Отчёт отдельно перечисляет backend, UI и manual provider blockers.
Проверки: full block integration, validators и secret scan.
Commit: test: audit games catalog and creation flow
```
