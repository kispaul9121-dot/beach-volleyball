# Модель данных

Рекомендуемая база — PostgreSQL/Supabase.

## Идентичность и роли

- users
- profiles
- organizations
- organization_members
- organizer_permissions

## Места и профессиональные сущности

- clubs
- venues
- courts
- coaches

## Активности

- games
- trainings
- tournaments
- seasons
- tours

## Сезоны и игровые дни

- season_members
- season_game_days
- game_day_courts
- game_day_participants
- rotation_rounds
- rotation_assignments

Ключевой принцип: количество кортов хранится у `season_game_days`, а не у формата сезона.

## Соревнования

- competition_formats
- teams
- team_members
- rounds
- matches
- match_participants
- results
- standings
- placements
- ranking_rules

Формат полного распределения мест 1–32 хранит 5 раундов, 80 матчей и итоговый placement для каждой команды.

## Регистрации и деньги

- registrations
- waitlist_entries
- payments
- refunds
- payouts

## Коммуникация

- conversations
- conversation_members
- messages
- notifications

Каждый чат содержит контекстную ссылку на игру, сезон, тренировку, клуб или тур.

## Контроль

- audit_log
- moderation_reports
