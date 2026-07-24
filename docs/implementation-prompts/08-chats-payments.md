# Блок 8 — чаты, уведомления и платежи

## 057 — Canonical conversation model и список чатов

```text
Реализуй chat domain и chats.main.

Правила:
1. У каждой опубликованной сущности один canonical conversationId.
2. Встроенный чат сущности и глобальная вкладка Чаты — одна история, не две копии.
3. Membership выдаётся confirmed participants, owner и authorized staff; guest/invited/requested без confirmation не имеют доступа.
4. Список группируется/сортируется по последней активности и показывает entity context, unread count и archived/read-only state.
5. Active actor влияет на доступ и presentation, но account-owned personal conversation не дублируется.
6. Не создавай социальные группы вне сущности.
7. Realtime transport за интерфейсом; при отсутствии backend оставь adapter boundary и mock only in development.

Тесты: duplicate conversation prevention, membership revoke, unread consistency и actor switch.

Commit: feat: implement canonical chat list
```

## 058 — Детали чата и embedded event chat

```text
Реализуй chat.details и reusable embedded chat section.

Сделай:
1. Message list с pagination, send state, retry и stable IDs.
2. System messages для утверждённых entity events.
3. Header ведёт к canonical related entity.
4. Embedded section использует тот же repository/conversationId и unread state.
5. Archived/read-only conversation блокирует send с текстовым объяснением.
6. Offline queued message явно помечается unsent; не отображай server-delivered до подтверждения.
7. Не реализуй attachments, reactions, voice или moderation tools, если они definition_pending; оставь интерфейс расширения.
8. Accessibility: author/time/status, focus после send и screen-reader order.

Тесты: duplicate send idempotency, reconnect, membership revoked, entity link и embedded/global identity.

Commit: feat: implement canonical event chat details
```

## 059 — Уведомления и deep-link resolver

```text
Реализуй global.notifications и notification service boundary.

Сделай:
1. Список уведомлений с unread state, type, actor context, entity context и timestamp.
2. Tap использует NAVIGATION_RESOLVERS и ведёт на canonical details/invitation/chat/payment/manage только после permission recheck.
3. Opening не всегда означает read; применяй утверждённую policy.
4. Push permission request не показывается автоматически до onboarding/контекстного шага.
5. Если push provider не подключён, создай local/in-app adapter и честный status; не симулируй доставку.
6. Удалённая/закрытая сущность показывает безопасный unavailable state.
7. Не включай sensitive payment/message body в push preview без privacy policy.

Тесты: deep links, stale notification, wrong actor, unread badges и denied permission.

Commit: feat: implement notification center and routing
```

## 060 — Payment checkout boundary

```text
Реализуй payment.checkout как provider-agnostic flow.

Прочитай FINANCE_ARCHITECTURE.yaml и payment specs.

Сделай:
1. Order summary: entity, participant owner, amount, currency, refund policy summary.
2. Только payment_owner может открыть checkout.
3. Server создаёт provider session; client не считает redirect успехом.
4. Success определяется authoritative webhook/status refresh и idempotency key.
5. States: creating, redirecting, pending, succeeded, failed, cancelled, expired, offline.
6. External payment не открывает checkout.
7. Если provider не выбран/не настроен, оставь adapter interface и blocked implementation status; не делай fake production payment.
8. Не логируй card/provider secrets.

Тесты: pay another user forbidden, repeated return link, pending webhook, amount changed и stale order.

Commit: feat: add secure payment checkout boundary
```

## 061 — Детали платежа и личный ledger

```text
Реализуй payment.details и profile.payments поверх finance read models.

Player видит собственные charges/refunds и связанные сущности. Trainer/organization видят только разрешённые payouts/reports своего actor, не данные чужого actor автоматически.

Payment details: status, amount, timestamps, receipt reference, refund history и canonical entity link. Sensitive provider payload не показывается.

Сделай filters/status empty/error/offline cached. Refund action добавляй только при существующем action/capability; иначе read-only foundation.

Участник всё равно запускает оплату из своей строки Participants, а ledger — история, не альтернативный pay-for-others экран.

Тесты: actor data isolation, pending→paid refresh, refund projection, deleted entity link и currency formatting.

Commit: feat: implement payment history and details
```

## 062 — Payment cells во всех сущностях

```text
Внедри единый ParticipantPaymentCell в game/training/tournament/tour participant lists.

Правила:
- другие строки: Оплачено, Не оплачено или Бесплатно без action;
- собственная online unpaid строка: Оплатить;
- processing: Оплата обрабатывается;
- failed: Повторить оплату;
- external: Не оплачено + helper про оплату организатору;
- success заменяет кнопку без layout jump;
- guests/unconfirmed не видят payment statuses;
- manual edit online status запрещён.

Не переделывай participant lists целиком; интегрируй общий компонент минимально. Добавь accessibility label с именем владельца собственной записи.

Тесты: all states, role visibility, layout stability, stale refresh и no action on others.

Commit: refactor: unify participant payment cells
```

## 063 — Сквозной аудит чатов, уведомлений и финансов

```text
Audit-only. Проверь canonical identities и security boundaries.

Убедись:
- одно событие → один conversationId;
- invite/request не даёт chat access;
- removal/revocation закрывает future messages;
- notification deep link повторно проверяет permission;
- payment success только authoritative;
- нельзя платить за другого;
- actor finance data изолирована;
- external payment не создаёт provider order;
- retries идемпотентны;
- offline statuses честные.

Добавь integration tests между invitation acceptance, participant payment cell, checkout, webhook refresh, chat membership и notification link. Не добавляй новые provider features.

Commit: test: audit messaging notification and finance boundaries
```

## 064 — Наблюдаемость ошибок и privacy-safe telemetry

```text
Добавь общий слой error reporting/analytics interfaces без привязки к конкретному vendor, если vendor не утверждён.

Сделай:
1. Typed events только для ключевых funnel/actions и failures.
2. Запрет на пароль, token, message body, payment provider secret, полный адрес или private profile data.
3. Correlation ID для network command и audit event.
4. User-facing error code mapping без раскрытия backend details.
5. Development logger и production no-op/vendor adapter.
6. Consent/privacy hooks по существующим settings; не показывай ложный consent screen.
7. Добавь тест, запрещающий известные sensitive keys в telemetry payload.

Не меняй UX экранов, кроме единообразного error presentation через существующий ErrorState.

Commit: feat: add privacy safe observability foundation
```