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
- `active_actor_preferences` — последний активный профиль.

Ключевой принцип: `user_account` отвечает за вход, `actor_profile` — от чьего имени пользователь действует.

## 2. Площадки и профессиональные сущности

- `clubs`;
- `venues`;
- `courts`;
- `venue_opening_hours`;
- `court_blocks`;
- `court_bookings`;
- `trainer_specializations`;
- `trainer_venue_links`.

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
- `training_groups`;
- `tournaments`;
- `seasons`;
- `season_game_days`;
- `tours`.

## 4. Участие

- `participations` — единый статус участия;
- `participation_requests`;
- `waitlist_entries`;
- `invitations`;
- `check_ins`;
- `attendance_records`.

`participations` хранит user и actor-контекст, но личная спортивная статистика всегда связывается с player profile человека.

## 5. Одноразовые игры и игровые дни

- `game_format_configs`;
- `game_courts`;
- `game_rounds`;
- `round_assignments`;
- `round_results`;
- `game_day_participants`;
- `game_day_courts`.

Для ротации пяти игроков `round_assignments` хранит корт, раунд, игрока, команду / партнёра и статус отдыха.

Количество кортов хранится у конкретной игры или `season_game_day`, а не у формата сезона.

## 6. Соревновательный движок

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

## 7. Тренировки

- `training_programs`;
- `training_group_members`;
- `training_group_schedules`;
- `subscriptions` / `passes`;
- `attendance_records`;
- `trainer_notes`;
- `training_materials`.

## 8. Туры

- `tour_program_days`;
- `tour_packages`;
- `tour_accommodation_options`;
- `tour_bookings`;
- `booking_travelers`;
- `tour_documents`;
- `tour_staff`;
- `tour_transport_options`.

Неформальная поездка может не использовать коммерческие packages, но остаётся той же сущностью `tour`.

## 9. Деньги

- `orders`;
- `order_items`;
- `payments`;
- `payment_transactions`;
- `refunds`;
- `payout_accounts`;
- `payouts`;
- `financial_reports`.

Платёж не является статусом участия. Order связывает участие / бронирование и конкретную цену на момент создания.

## 10. Коммуникация

- `conversations`;
- `conversation_contexts`;
- `conversation_members`;
- `messages`;
- `message_attachments`;
- `announcements`;
- `notifications`;
- `notification_actions`.

Чат содержит контекстную ссылку на сущность. Уведомление содержит `action_id` и параметры перехода.

## 11. Статистика

- `player_rating_events`;
- `player_stat_snapshots`;
- `trainer_stat_snapshots`;
- `organization_stat_snapshots`;
- `analytics_jobs`.

Снапшоты ускоряют чтение, но источником истины остаются результаты, посещаемость и транзакции.

## 12. Контроль и безопасность

- `audit_log`;
- `moderation_reports`;
- `blocked_users`;
- `device_sessions`;
- `data_export_requests`;
- `account_deletion_requests`.

RLS проверяет не только user_id, но actor ownership, entity relationship и organization membership.
