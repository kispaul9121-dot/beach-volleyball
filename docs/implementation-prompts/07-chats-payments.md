# Блок 7 — чаты, уведомления и платежи

## 060 — Conversation schema и RLS

```text
Создай Supabase migrations для conversations, conversation_members, messages и entity conversation links.

Для каждой опубликованной сущности существует максимум один canonical conversation. Membership создаётся только для разрешённых участников/организаторов; unresolved invitation и pending request не получают access. Сообщение хранит sender user/actor context, client idempotency key, created_at и optional edited/deleted metadata по контракту.

Добавь indexes для conversation timeline/unread queries и RLS на read/insert/update. Не создавай social groups или отдельные match chats.
Проверки: migration reset, unique entity conversation constraint и RLS guest/pending/participant/manager negatives.
Commit: feat: add canonical conversation schema and policies
```

## 061 — Список чатов из Supabase

```text
Подключи chats.main из промта 003 к реальным conversations.

Создай paginated read model: title/avatar/type, last message, timestamp, unread count и linked entity. Сортировка по последней активности стабильна; realtime update не создаёт duplicate row. Active actor влияет на presentation/actions, но account membership остаётся источником доступности.

Empty/error/offline states сохраняют нижнюю вкладку. Tap открывает canonical chat.details; muted/archive, если не утверждены, остаются definition_pending.

Через iOS-плагин проверь list performance, unread badges, actor switch и deep link.
Проверки: query pagination, RLS и duplicate conversation tests.
Commit: feat: connect chat list to Supabase
```

## 062 — Chat details и отправка сообщений

```text
Подключи chat.details к messages repository.

Реализуй cursor pagination назад, stable message order, optimistic send с client idempotency key, retry/error state и server acknowledgement. Пустой текст не отправляется; repeated tap не создаёт duplicate. Link в header открывает связанную сущность. Permission revoked переводит экран в read-denied state.

KeyboardAvoiding behavior, input accessory и scroll-to-latest должны корректно работать на iOS. Не добавляй attachments, reactions или edit UI — они отдельные decisions/prompts.

Вызови iOS-плагин: keyboard show/hide, long multiline input, background/foreground и VoiceOver.
Проверки: optimistic reconciliation, duplicate prevention и RLS.
Commit: feat: implement canonical chat messaging flow
```

## 063 — Supabase Realtime для чата

```text
Подключи Realtime subscription к открытым conversations и list summaries.

Обработай INSERT/UPDATE events, reconnect, app foreground/background, duplicate event после optimistic send и invalidated membership. Subscription создаётся один раз на scope и освобождается при смене conversation/account. При потере realtime UI остаётся usable через refresh/retry.

Не подписывай пользователя на conversations без membership и не помещай private payload в logs. Unread count обновляется authoritative read marker mutation с idempotency.

Через iOS-плагин проверь два simulator/session сценария или задокументируй недоступную multi-client проверку.
Проверки: event reducer tests, reconnect integration и no duplicate messages.
Commit: feat: add resilient Supabase Realtime chat updates
```

## 064 — Вложения чата — безопасный каркас

```text
Подготовь Storage и кодовую границу для будущих chat attachments без полного UX.

Создай private bucket/policies, attachment metadata type, upload service interface, size/type validation и signed URL read flow. Реальный picker/upload UI включай только если спецификация утверждена; иначе оставь feature flag и disabled action с accessible explanation.

Service-role не используется клиентом. Failed upload не создаёт message attachment record; cleanup orphan выполняется server-side job/Edge Function contract.

Через iOS-плагин проверь disabled/feature-on draft UI, permission prompt только при явном действии.
Проверки: Storage RLS, malicious file metadata и orphan rollback tests.
Commit: feat: scaffold secure chat attachment boundary
```

## 065 — Уведомления внутри приложения

```text
Реализуй global.notifications как Supabase-backed inbox.

Notification хранит type, recipient account, linked entity/action, created/read timestamps и deduplication key. Tap использует canonical deep-link resolver; malformed или удалённая сущность показывает safe unavailable state. Mark-read mutation idempotent.

Push delivery остаётся отдельным adapter: создай interface/token table только если contract готов, но не подключай случайный provider. Не дублируй invitation block логикой уведомлений.

Через iOS-плагин проверь list, unread state, deep links и permission-neutral behavior.
Проверки: recipient RLS, duplicate key и route resolution tests.
Commit: feat: implement in-app notification inbox
```

## 066 — Checkout boundary без привязки к провайдеру

```text
Создай payment checkout domain по FINANCE_ARCHITECTURE.yaml и JOIN_FLOW.yaml.

Мобильный клиент формирует только payment intent request для собственной participation/order и открывает provider adapter. Amount/currency/owner/entity повторно вычисляются server-side; клиентские значения не авторитетны. Secrets, signing keys и provider webhooks запрещены в Expo code.

Если provider не выбран, payment.checkout остаётся functional placeholder: order summary, blocked reason и adapter contract. Не симулируй успешную оплату и не разрешай платить за другого.

Через iOS-плагин проверь summary, loading/error, safe area и return to participant row.
Проверки: ownership, amount tampering и idempotency tests.
Commit: feat: define secure mobile checkout boundary
```

## 067 — Payment events и Supabase Edge Function

```text
Подготовь server-side payment lifecycle через Supabase Edge Function/webhook boundary.

Состояния: created, processing, paid, failed, cancelled, refunded в объёме контракта. Webhook проверяет signature, deduplication event id и authoritative order amount/owner. Повторный event не меняет результат дважды. Client получает status из базы/realtime, а не подтверждает оплату локально.

Если provider credentials отсутствуют, реализуй тестовый contract и local fixture только в server test environment, пометь production blocked. Service secrets хранятся в Supabase secrets.

Проверки: webhook signature failure, duplicate event, out-of-order event и RLS.
Commit: feat: add idempotent payment event backend
```

## 068 — Платёжные экраны и статусы

```text
Реализуй payment.details и завершённые states checkout.

Покажи order, связанную сущность, amount/currency ru-RU, processing/success/failed/refund status, receipt link при наличии и безопасный retry для owner. После paid собственная participant row обновляется на «Оплачено» без layout jump. Чужой paymentId должен вернуть permission denied, не masked partial data.

External organizer payment остаётся «Не оплачено · оплата организатору» без platform mutation. Manual paid toggle для online запрещён.

Через iOS-плагин проверь provider return deep link, cold start, status transitions и accessibility.
Проверки: payment projection, own-owner permissions и UI state tests.
Commit: feat: implement payment status and details screens
```

## 069 — Аудит чатов, уведомлений и платежей

```text
Audit-only. Не добавляй новые messaging/payment features.

Проверь 060–068: one-conversation invariant, membership RLS, send idempotency, realtime reconnect, attachment feature flag, notification dedup/deep links, checkout ownership, Edge Function secret boundary и payment status propagation. Убедись, что unresolved invitation не читает chat и что клиент не может отметить online payment вручную.

Через iOS-плагин пройди chat keyboard/background, notification deep link и provider-return simulation. Запусти secret scan и Supabase policy tests.

Исправляй только доказанные дефекты блока.
Проверки: integration suite и отчёт passed/failed/blocked provider setup.
Commit: test: audit chat notifications and payment security
```
