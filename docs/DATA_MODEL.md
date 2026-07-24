# Модель данных

Рекомендуемая база — PostgreSQL / Supabase с Row Level Security. Названия ниже концептуальные и могут уточняться при реализации.

## 1. Аккаунт и профили

- `user_accounts` — auth user, email, статус;
- `auth_identities` — Google, email и будущие провайдеры;
- `actor_profiles` — общий реестр player, trainer, organization;
- `player_profiles` — личные спортивные поля;
- `trainer_profiles` — профессиональные поля и проверка;
- `organizations` — компании, клубы и проекты;
- `organization_memberships` — user / actor, роль, статус;
- `actor_verifications` — документы и статусы;
- `active_actor_preferences` — последний активный профиль;
- `player_trainer_relationships` — активные и завершённые связи player profile с trainer actor;
- `player_trainer_relationship_events` — аудит создания, завершения и блокировки связи.

`player_trainer_relationships` хранит `player_profile_id`, `trainer_actor_id`, status, source, created_at, ended_at и audit actors. Активная пара уникальна, но игрок может иметь несколько тренеров, а тренер — несколько игроков. Создание сразу устанавливает `active`; отдельного requested/approval состояния нет.

Ключевой принцип: `user_account` отвечает за вход, `actor_profile` — от чьего имени пользователь действует. Каждый человек имеет player profile, даже когда активен trainer или organization actor.

## 2. Организация, площадки и административный кабинет

### Организация и права

- `organizations` — публичные и юридические поля организации;
- `organization_settings` — операционные значения по умолчанию, уведомления и политики;
- `organization_memberships` — сотрудник, роль, статус и срок доступа;
- `organization_role_permissions` — серверная матрица разрешений;
- `organization_staff_assignments` — назначение сотрудника на площадку, сущность или функцию;
- `organization_invitations` — приглашения сотрудников;
- `organization_ownership_transfers` — процесс передачи владения;
- `organization_documents` — проверка и срок действия документов.

`actor_profile` организации определяет контекст бренда, но доступ сотрудника всегда проверяется через активный `organization_membership` и permission.

### Площадки и ресурсы

- `clubs`;
- `venues`;
- `courts`;
- `venue_opening_hours`;
- `venue_availability_rules`;
- `court_availability_rules`;
- `court_blocks`;
- `venue_maintenance_windows`;
- `court_bookings`;
- `trainer_specializations`;
- `trainer_venue_links`.

Регулярное правило доступности задаёт базовое расписание. Конкретная блокировка или обслуживание имеет приоритет и может создавать конфликт с опубликованными событиями.

### Операционные задачи

- `organization_tasks` — рабочая задача, severity, срок, ответственный, статус и deep link;
- `organization_task_events` — история создания, назначения, snooze, выполнения и устаревания;
- `organization_task_sources` — связь задачи с заявкой, платежом, результатом, кортом, сотрудником или документом.

Задача создаётся из доменного события и не закрывается простым просмотром. Она становится `resolved` после выполнения либо `obsolete`, когда источник потерял актуальность.

### Клиенты и коммуникация организации

- `organization_client_links` — разрешённая связь пользователя с организацией;
- `organization_client_tags` — внутренние операционные теги без чувствительных спортивных данных;
- `organization_announcements` — массовые сообщения и аудит аудитории;
- `organization_message_templates` — шаблоны уведомлений;
- `organization_exports` — история экспорта персональных и финансовых данных.

Организация не получает право на всю личную спортивную статистику пользователя. Доступ определяется контекстом участия, согласием и ролью сотрудника.

## 3. Общая основа сущностей

Возможны отдельные таблицы сущностей, но общие поля должны быть одинаковыми:

```text
id
created_by_user_id
created_by_actor_id
status
visibility
title
description
starts_at
ends_at
timezone
venue_id
created_at
updated_at
```

Основные таблицы:

- `games`;
- `trainings`;
- `tournaments`;
- `tournament_days` — игровые дни сезонного турнира;
- `tournament_series_configs` — правила накопительной таблицы сезонного турнира;
- `tours`.

`training_groups` не входят в MVP и не должны создаваться новыми сценариями.

## 4. Мои игроки и приглашения

Источник истины: `docs/PLAYER_DIRECTORY.yaml`.

- `actor_player_links` — односторонняя связь активного actor с сохранённым player profile;
- `player_link_events` — аудит добавления, удаления и источника связи;
- `event_invitation_batches` — массовая операция приглашения выбранных игроков;
- `event_invitations` — приглашение конкретного игрока в конкретную сущность;
- `invitation_delivery_attempts` — push, email, in-app и повторные попытки.

`actor_player_links` содержит:

```text
id
owner_actor_id
player_profile_id
source
added_by_user_id
created_at
removed_at
```

Правила:

- связь не взаимная и не требует подтверждения;
- связь не является дружбой, ученичеством, партнёрством или участием;
- сохранение игрока не раскрывает закрытые данные;
- удаление связи не удаляет прошлые события, сообщения, платежи и результаты;
- приглашение всегда относится к конкретной сущности;
- принятая заявка или приглашение создаёт либо изменяет `participation`.

### Запрос игрока тренеру

Источник истины: `docs/TRAINER_RELATIONSHIPS.yaml`.

- `trainer_relationship_requests` — player profile, trainer actor, status `pending / accepted / declined / cancelled`, timestamps and optional message;
- `player_trainer_relationships` — active or ended confirmed relationship created only after trainer acceptance;
- `trainer_relationship_events` — audit of request, message, accept, decline, cancel and end actions.

Pending-запрос не создаёт `actor_player_link`. После `Добавить` создаётся или восстанавливается `actor_player_link` trainer actor → player profile с source `trainer_accepted_request`, а запрос становится `accepted`.

## 5. Участие

- `participations` — единый статус участия;
- `participation_requests`;
- `waitlist_entries`;
- `invitations` — legacy alias, новые реализации используют `event_invitations`;
- `check_ins`;
- `attendance_records`.

`participations` хранит user и actor-контекст, но личная спортивная статистика всегда связывается с player profile человека.

Добавление в `Мои игроки` не создаёт participation. Приглашённый игрок до принятия не считается подтверждённым участником и не получает доступ к чату события.

## 6. Одноразовые игры и игровые дни

- `game_format_configs`;
- `game_courts`;
- `game_rounds`;
- `round_assignments`;
- `round_results`;
- `game_day_participants`;
- `game_day_courts`.

Для ротации пяти игроков `round_assignments` хранит корт, раунд, игрока, команду / партнёра и статус отдыха.

Количество кортов хранится у конкретной игры или `tournament_day`, а не у режима сезонного турнира.

## 7. Соревновательный движок

- `competition_configs` — формат и версия правил;
- `competition_participants` — игрок, пара или команда;
- `teams`;
- `team_members`;
- `competition_rounds`;
- `pairing_versions`;
- `matches`;
- `match_sides`;
- `result_events`;
- `standings_snapshots`;
- `placements`;
- `tiebreak_rules`;
- `competition_overrides`.

### Важные правила

- итоговые таблицы рассчитываются из `result_events`;
- исправление создаёт новое событие, а не переписывает историю;
- опубликованная жеребьёвка имеет версию;
- override содержит причину, acting_user_id и acting_actor_id;
- полный placement 32 хранит 5 раундов, 80 матчей и место 1–32 для каждой команды.

## 8. Тренировки

- `training_programs`;
- `training_templates` — повторяемые настройки без постоянного членства;
- `training_visibility_rules` — private или public для всей тренировки;
- `training_enrollment_rules` — open, request, invitation_only независимо от видимости;
- `training_visibility_events` — аудит публикации, скрытия и повторного открытия всей тренировки;
- `training_invitation_batches` — выбранные игроки и результат отправки;
- `attendance_records`;
- `trainer_notes`;
- `training_materials`.

Тренировка является отдельным событием. Для повторения используется template или дублирование. Постоянная социальная группа, group membership и отдельный group chat не создаются.

Если позднее появятся пакеты посещений, они должны быть финансовым продуктом, применимым к набору тренировок, а не причиной создавать социальную группу.

## 9. Туры

- `tour_program_days`;
- `tour_packages`;
- `tour_accommodation_options`;
- `tour_bookings`;
- `booking_travelers`;
- `tour_documents`;
- `tour_staff`;
- `tour_transport_options`.

Неформальная поездка может не использовать коммерческие packages, но остаётся той же сущностью `tour`.

## 10. Деньги

Источник истины: `docs/FINANCE_ARCHITECTURE.yaml`.

- `orders`;
- `order_items`;
- `payments`;
- `payment_transactions`;
- `refunds`;
- `seller_accounts`;
- `payout_accounts`;
- `payouts`;
- `platform_fees`;
- `provider_fees`;
- `receipts`;
- `financial_ledger_entries`;
- `financial_reports`.

Платёж не является статусом участия. Order связывает участие / бронирование и конкретную цену на момент создания. Один order содержит одного seller actor.

## 11. Коммуникация

Источник истины: `docs/ENTITY_SECTIONS.yaml`.

- `conversations`;
- `conversation_contexts`;
- `conversation_members`;
- `messages`;
- `message_attachments`;
- `announcements`;
- `notifications`;
- `notification_actions`.

Каждая опубликованная игра, тренировка, турнир, сезон и тур имеет один основной conversation context. Подтверждённые участники и организаторы получают доступ согласно политике. Отдельные социальные group conversations не создаются.

Чат содержит контекстную ссылку на сущность. Уведомление содержит `action_id` и параметры перехода.

## 12. Статистика

- `player_rating_events`;
- `player_stat_snapshots`;
- `trainer_stat_snapshots`;
- `organization_stat_snapshots`;
- `analytics_jobs`.

Снапшоты ускоряют чтение, но источником истины остаются результаты, посещаемость и транзакции. Статистика не рассчитывается по членству в несуществующей группе.

## 13. Контроль и безопасность

- `audit_log`;
- `moderation_reports`;
- `blocked_users`;
- `device_sessions`;
- `data_export_requests`;
- `account_deletion_requests`.

Для административных действий audit event дополнительно хранит `organization_id`, `membership_id`, роль на момент действия, `acting_user_id`, `acting_actor_id`, `action_id`, объект, diff, причину и correlation ID.

RLS проверяет не только user_id, но actor ownership, entity relationship, organization membership и конкретный permission. Player directory не является основанием для доступа к закрытым данным игрока.

## 14. Связь игрока и тренера

Источник истины: `docs/TRAINER_RELATIONSHIPS.yaml`.

- `player_trainer_relationships` — player profile, trainer actor, status, initiator and timestamps;
- `player_trainer_relationship_events` — request, message permission, accept, decline and end audit;
- `trainer_relationship_message_grants` — ограниченный контекст прямого диалога после запроса;
- `trainer_search_documents` — поисковое представление публичных полей тренера.

Статусы: `requested`, `active`, `declined`, `cancelled`, `ended_by_player`, `ended_by_trainer`. Надпись `Тренируется у` разрешена только для `active`. Один player profile может иметь несколько активных trainer relationships. Принятие обеспечивает наличие игрока в рабочем списке `Мои игроки` тренера, но сама связь остаётся отдельной подтверждаемой сущностью.
