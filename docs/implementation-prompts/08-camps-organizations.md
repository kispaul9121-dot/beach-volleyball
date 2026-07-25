# Блок 8 — кэмпы и организации

## 070 — Camps schema и RLS

```text
Создай Supabase migrations для tours/camps, tour_participants, booking_drafts, options и organizer relations по DATA_MODEL.md и tour specs.

Разделяй базовую сущность кэмпа, варианты участия/размещения и конкретное бронирование. Храни creator actor context, visibility, time range, place, capacity и payment policy. Документы, транспорт и сложные packages добавляй только как nullable/feature-gated fields, если продуктовый контракт не завершён.

RLS: public catalog видит только public published camp projection; booking/participant data — только owner и authorized managers. Сгенерируй TypeScript types и repositories.
Проверки: migration reset, constraints, guest/participant/manager RLS negatives.
Commit: feat: add camps booking schema and RLS
```

## 071 — Каталог кэмпов из Supabase

```text
Подключи camps.main из промта 004 к Supabase read models.

Реализуй public/participating/managing scopes, filters только из спецификации, pagination и archive mode. Не переиспользуй game query с условными полями; используй общий catalog shell и отдельный CampsRepository. Непубличный camp не попадает в public catalog, но доступен по relation.

Карточка показывает ключевые даты, место, organizer, format/price summary и одно primary action. Незавершённые housing/document indicators отображай только при реальных данных.

Через iOS-плагин проверь list, filters, management/archive transitions и actor switch.
Проверки: query/RLS, pagination и duplicate suppression.
Commit: feat: connect camps catalog to Supabase
```

## 072 — Публичная страница кэмпа

```text
Реализуй tour.details как канонический экран guest/participant/organizer.

Sections подключаются по доступным данным: overview, program, accommodation, participants, price/payments summary, documents, transport и canonical chat. Не показывай пустые «богатые» разделы как будто они готовы: definition_pending блок скрывается или получает честный placeholder. Join/booking entry использует единое основное действие.

Public projection не раскрывает booking documents, room selection или payment details. Organizer получает переход в /manage, а не inline editor.

Через iOS-плагин проверь длинный экран, sticky CTA, section navigation и deep link.
Проверки: role projection, privacy и canonical route tests.
Commit: feat: implement canonical camp details
```

## 073 — Бронирование кэмпа

```text
Реализуй tour.booking как отдельный draft flow.

Пользователь выбирает участников бронирования, доступные варианты/размещение и видит authoritative price summary. Capacity/option availability повторно проверяются сервером при confirm. Payment handoff использует общий checkout boundary; offline может сохранять draft, но не резервирует место без server response.

Документы и персональные данные добавляй только по утверждённому набору и храни в private Storage/table projection. Не сохраняй паспортные поля «на будущее».

Через iOS-плагин проверь multi-step keyboard, back/draft restore, price summary и payment return.
Проверки: capacity race, price tampering, booking ownership и RLS.
Commit: feat: implement secure camp booking flow
```

## 074 — Создание кэмпа

```text
Реализуй tour.create для player, trainer и organization с role-aware полями.

Используй общий draft/wizard infrastructure, но отдельную domain form model. Минимум: identity/dates/place, format/program baseline, participation/options, price/publish review. Player может создать informal camp только в разрешённом объёме; commercial fields доступны trainer/organization по capabilities.

Не придумывай accommodation inventory, transport packages или document requirements без контракта. Сохраняй feature flags и compatible nullable schema.

Через iOS-плагин проверь actor switch, native dates, dirty draft back и conditional fields.
Проверки: role matrix, validation, idempotent publish и offline draft.
Commit: feat: implement role-aware camp creation
```

## 075 — Управление кэмпом

```text
Реализуй tour.manage по утверждённым sections.

Подключи overview, applications/participants, booking options, program shell, payments summary, documents/transport placeholders и canonical chat. Manager может approve/remove в пределах capabilities; каждое sensitive действие создаёт audit event. Online payment status не редактируется вручную.

Незавершённые modules не получают fake CRUD: оставь stable route/component boundary и definition_pending state. Summary queries должны быть агрегированными и paginated для больших списков.

Через iOS-плагин проверь tabs/sections, confirmation sheets, long lists и permission revocation.
Проверки: RLS, audit, booking consistency и no manual paid toggle.
Commit: feat: implement camp management foundation
```

## 076 — Публичная страница клуба

```text
Подключи club.details к Supabase public projection.

Покажи identity, contacts в пределах privacy, venues, upcoming public events и approved staff/trainers. Не раскрывай memberships, finance, private calendar или internal notes. Каждая event card ведёт на canonical detail screen; venue — на venue.details.

Owner/organization member получает отдельный manage entry после capability check. Reviews/ratings, если не утверждены, остаются definition_pending без фиктивных stars.

Через iOS-плагин проверь hero/header, lists, maps placeholder и deep links.
Проверки: public/private projection, organization role и no duplicate event screens.
Commit: feat: implement privacy-safe club public page
```

## 077 — Кабинет организации — shell

```text
Реализуй club.manage shell без попытки закончить все административные модули.

Навигация использует один organization workspace и sections из ORGANIZATION_ADMIN.yaml: overview, people/staff, venues, calendar/events, finance, settings, audit/more в разрешённом составе. Не создавай вторую нижнюю навигацию; это stack внутри приложения. Membership/capability resolver проверяется на каждом module route.

Для partial/definition_pending modules создай typed route boundary, permission state и честный placeholder. Existing working screens не переписывай.

Через iOS-плагин проверь compact navigation на телефоне, back fallback и revoked membership.
Проверки: route/capability matrix и no second tab bar.
Commit: feat: establish organization management shell
```

## 078 — Площадки, сотрудники и роли — основа

```text
Создай Supabase schema/repositories для venues, courts, organization_memberships и staff role assignments в объёме контрактов.

Добавь safe CRUD interfaces, constraints и audit actor context. UI реализуй только для утверждённых полей: venue identity/address/courts и member identity/role/status. Payroll, work schedules, access packages и finance permissions не придумывай; оставь feature boundaries.

RLS гарантирует, что organization member видит/меняет только разрешённую организацию и роль не повышается client mutation. Invite/role change требуют server validation и audit.

Через iOS-плагин проверь forms/lists, keyboard и destructive confirmation.
Проверки: privilege escalation negative tests и schema constraints.
Commit: feat: add organization venue and staff foundations
```

## 079 — Аудит кэмпов и организаций

```text
Audit-only. Не добавляй modules организации или booking options.

Проверь 070–078: schema/RLS, catalog scopes, camp details privacy, booking capacity/price, role-aware creation, management audit, club public projection, organization shell, venue/staff privilege boundaries. Убедись, что partial screens сохранены, а placeholders не выдают себя за работающие CRUD flows.

Через iOS-плагин пройди Camps tab → details → booking draft → manage и Club → organization shell. Проверь 320/430 pt, keyboard, VoiceOver и actor switch.

Исправляй только доказанные дефекты блока.
Проверки: integration/RLS suite, route validators и privacy report.
Commit: test: audit camps and organization foundations
```
