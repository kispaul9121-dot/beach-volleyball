# Блок 9 — кэмпы и организации

## 065 — Каталог кэмпов и management mode

```text
Реализуй camps.main по тому же navigation contract, но не копируй play.main целиком.

Сделай:
1. Discovery catalog кэмпов с invitation priority block.
2. Public/private visibility и nearest-first ordering.
3. Contextual management mode для manageable tours.
4. Create action по active actor capabilities.
5. Pull-down archive с теми же 24/72 thresholds, accessibility action и отключённым pull-to-refresh.
6. Сохрани собственные category/filter needs кэмпов из spec; не добавляй игры/турниры как tabs.
7. Возврат сохраняет mode/filter/scroll.

Переиспользуй общие catalog, invitation и archive primitives, а не fork компонентов.

Тесты: actor variants, archive gesture, invitation exclusion from participation и private tour visibility.

Commit: feat: implement camps catalog and management
```

## 066 — Canonical details и booking foundation кэмпа

```text
Реализуй tour.details variants informal, training_camp и organization_package только по утверждённым данным.

Покажи: organizer, dates, location, program, trainers, included services, capacity, price, participants policy и canonical chat для confirmed participants.

Booking action ведёт на tour.booking. Если accommodation/documents/package variants definition_pending, создай typed presentation slots и честные unavailable states; не выдумывай номера, трансферы или договоры.

Guest не видит chat/payment statuses. Participant видит свой booking/payment status. Organizer видит Управлять, но details остаётся read-only.

Тесты: variant-specific blocks, invitation, private access, sold out/waitlist и incomplete package.

Commit: feat: implement canonical camp details
```

## 067 — Создание кэмпа

```text
Реализуй tour.create статус-зависимо.

Actor variants:
- player — informal совместная поездка/игровой кэмп только в разрешённом scope;
- trainer — training camp;
- organization — commercial package.

Сделай общий draft shell и variant-specific steps из tour-create.md. Не показывай коммерческие finance/accommodation fields игроку. Для непринятых booking/legal rules создай foundation types и feature flags.

Обязательны единый date range кэмпа, location, capacity, enrollment/payment, program summary, participants/invitations и review/publish. Это tour, а не season и не повторяющаяся игра.

Тесты: actor capability, variant switching impact, payout readiness, draft resume и publish validation.

Commit: feat: implement actor aware camp creation
```

## 068 — Управление кэмпом и бронирование

```text
Реализуй tour.manage и tour.booking без симуляции travel provider.

Manage: overview, requests/waitlist/invitations, confirmed participants, program, booking records, payment summary, announcements/chat и settings/audit только по spec.

Booking: booking participants, выбранный approved package/accommodation option, required documents status, price summary и own payment action. Один пользователь не оплачивает чужой booking без отдельного утверждённого payer contract.

Если размещение/документы не определены, экран сохраняет booking draft и показывает блокирующую причину, а не fake confirmation.

Тесты: capacity race, booking owner, package changed, document missing, payment pending и manager permission.

Commit: feat: implement camp management and booking foundation
```

## 069 — Публичные страницы клуба и площадки

```text
Реализуй club.details и venue.details как discovery screens.

Club: identity, description, venues, trainers, ближайшие public activities, contacts/links по privacy contract и save/follow action если оно зарегистрировано.

Venue: address, courts, amenities, opening info и public schedule. Booking action добавляй только если backend/contract существует; иначе non-clickable future capability.

Не создавай manage controls на public screens; owner/member получает Управлять link после capability check. Не публикуй private events через schedule.

Тесты: public/private data, empty schedules, deleted venue, canonical entity links и organization member permissions.

Commit: feat: implement club and venue public pages
```

## 070 — Публичные профили игрока, тренера и поиск тренера

```text
Реализуй player.public_profile, trainer.public_profile и trainer.search, сохраняя privacy boundary.

Player profile показывает только разрешённые спортивные данные и save/remove from My players. Не вводи friends/followers.

Trainer profile показывает professional info, verification status, public schedule и reviews только если контракт утверждает. Search поддерживает filters из spec и запрос тренеру через registered action.

Owner variant ведёт к settings/actor profile, organization manager не получает редактирование чужого trainer actor без staff grant.

Тесты: stranger/saved/owner, privacy hidden fields, verification pending, empty search и request idempotency.

Commit: feat: implement player and trainer discovery
```

## 071 — Organization admin shell и безопасные placeholders

```text
Реализуй club.manage shell и route guards, не пытаясь закончить все admin-модули одним промтом.

Сделай:
1. Header organization context, role и canonical back.
2. Navigation к зарегистрированным manage-overview/people/staff/venues/calendar/activities/finance/settings/audit/more screens.
3. Каждый незавершённый модуль читает IMPLEMENTATION_STATUS и показывает честный placeholder с описанием доступной основы; не имитирует данные.
4. Один общий organization layout без второй нижней навигации.
5. Permission проверяется server-side по каждому модулю.
6. Не смешивай organization actor profile с organization membership/staff role.

Тесты: module grants, deep links, revoked membership и placeholder accessibility.

Commit: feat: add organization administration shell
```

## 072 — Минимальные organization admin модули и аудит

```text
Реализуй только foundation для модулей, которые имеют завершённый контракт: overview summary, people/staff list, venues list и activities links. Finance/settings/audit/calendar могут остаться partial, если их спецификация или backend не готовы.

Для каждого модуля:
- reuse canonical entities;
- no duplicate event creation screens;
- explicit permission;
- loading/empty/error/offline;
- server pagination;
- action IDs из ACTIONS.yaml.

Затем проведи audit camps + organizations: actor/member separation, private data, canonical routes, payments/chat identities и отсутствие fake booking/finance. Обнови IMPLEMENTATION_STATUS с evidence для каждого manage-* screen.

Commit: feat: add safe organization admin foundations
```