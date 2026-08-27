# Блок 3 — профиль и личные разделы

## 020 — Profile repository на Supabase

```text
Подключи базовый home.main из промта 001 к реальным Supabase read models.

Создай ProfileRepository и один агрегированный query/view для active actor: header, counts, ближайшая активность и доступные переходы. Не выполняй много независимых запросов из каждого компонента. Fixtures сохрани только для tests/Storybook/dev fallback и никогда не смешивай их с production response.

Проверь RLS: account видит собственный private projection и только разрешённые public данные других actors. Добавь loading, stale, empty, error и offline read-only state.

Через iOS-плагин проверь переход от skeleton к данным, длинные имена и refresh.
Проверки: repository integration tests, query count, RLS negatives.
Commit: feat: connect profile home to Supabase read model
```

## 021 — Шапка профиля и actor context

```text
Доработай ProfileHeaderCard без изменения маршрутов.

Покажи avatar, display name, actor type, verification/status badge и безопасный вход в actor.switcher. Для player/trainer/organization используй общий компонент и разные read projections, а не три копии. Privacy-sensitive поля не выводятся без разрешения.

Avatar upload пока использует Storage adapter interface; если UX crop/upload не утверждён, оставь display-only placeholder и отдельное future action. Поддержи длинные русские названия, отсутствие фото и 200% text.

Через iOS-плагин проверь VoiceOver order, touch target switcher и light/dark.
Проверки: component variants и privacy projection tests.
Commit: feat: refine profile header and actor context
```

## 022 — Лента личной активности

```text
Реализуй profile.activity как единую личную ленту участий, заявок, ожидания и завершённых событий.

Создай Supabase view/query с cursor pagination и фильтрами по типу/периоду. Экран не показывает управление: карточка ведёт на канонический detail screen. Unresolved invitation отображается в утверждённом месте и не считается participation до принятия.

Сохрани разделение Предстоящие/Прошедшие, loading/empty/error/offline и stable sorting. Не создавай отдельные copies game/training/tournament rows.

Через iOS-плагин проверь длинный список, filters, scroll restoration и deep link.
Проверки: pagination, status mapping и no-manage-controls tests.
Commit: feat: implement unified personal activity feed
```

## 023 — Раздел «Мои игроки»

```text
Реализуй profile.players и общий player picker на основе PLAYER_DIRECTORY.yaml.

Мои игроки — односторонний сохранённый список active actor; добавление не требует подтверждения и не создаёт участие. В player.picker доступны Мои игроки, Недавние и Поиск, обязательны entity/draft context и returnTo. Не создавай сущности друзья, подписчики, ученики или социальные группы.

Добавь Supabase tables/indexes/RLS только если их нет. Search должен быть debounced, paginated и privacy-safe. Full-screen modal скрывает bottom tabs.

Через iOS-плагин проверь search keyboard, selection, dismiss и returnTo.
Проверки: duplicate save, unauthorized private fields и picker context tests.
Commit: feat: implement player directory and canonical picker
```

## 024 — Мой календарь

```text
Реализуй profile.calendar как read-only agenda из личных участий и управляемых событий account.

Сначала сделай список по датам с timezone-safe boundaries; month grid и системная Calendar integration остаются definition_pending, если не утверждены. Одна сущность не должна дублироваться из-за нескольких actor relations. Tap открывает канонический detail route.

Подключи Supabase query/view, pagination по диапазону дат и offline cached last-success snapshot. Не сохраняй события в системный календарь без отдельного разрешения пользователя.

Через iOS-плагин проверь locale ru-RU, timezone change, Dynamic Type и date navigation.
Проверки: date boundary/unit tests и duplicate suppression.
Commit: feat: add personal agenda calendar
```

## 025 — Фильтры «Мои игры/тренировки/турниры/кэмпы»

```text
Реализуй profile.my_games, profile.trainings, profile.competitions и profile.trips как совместимые filtered views поверх profile.activity repository.

Не создавай отдельные таблицы данных и не копируй карточки. Каждый экран задаёт только тип фильтра, пользовательские подписи и back_fallback. Управление здесь запрещено; manage routes остаются в контекстном management mode соответствующего каталога.

Поддержи Предстоящие/Прошедшие или утверждённые статусы, empty/error/offline и direct deep links.

Через iOS-плагин проверь четыре экрана, back gesture и сохранение filter state.
Проверки: shared repository tests и отсутствие manage actions.
Commit: feat: add typed personal activity filters
```

## 026 — Публичный профиль игрока

```text
Реализуй player.public_profile по privacy policy и relationship variant stranger/saved_player/owner.

Покажи только разрешённые спортивные данные, общие события/статистику если контракт позволяет, и действие сохранить/убрать из Моих игроков. Закрытые контакты, платежи, memberships и private activity не должны попадать даже в client response.

Создай отдельный public Supabase projection/view с RLS, а не фильтрацию полной private модели в UI. Owner получает переход к настройкам, но не второй профильный экран.

Через iOS-плагин проверь variants, длинный контент, VoiceOver и deep link.
Проверки: public/private field leakage tests.
Commit: feat: implement privacy-safe public player profile
```

## 027 — Публичный профиль тренера как безопасная основа

```text
Реализуй trainer.public_profile только в объёме утверждённой спецификации.

Покажи identity, verification state, краткую professional information и канонические переходы. Расписание, reviews и request-to-trainer используют typed placeholders/feature flags, если схемы или moderation rules definition_pending. Не создавай фиктивные оценки и доступность.

Supabase public projection не раскрывает private trainer/account data. Organization manager variant получает только разрешённые действия.

Через iOS-плагин проверь guest/authenticated/owner/organization variants и accessibility.
Проверки: role projection tests и no invented data.
Commit: feat: add safe trainer public profile foundation
```

## 028 — Статистика и платежи профиля — каркас

```text
Подключи profile.statistics и profile.payments к typed read model boundaries без изобретения финансовой аналитики.

Статистика показывает только метрики, уже определённые контрактами и доступные из данных; неизвестные графики остаются definition_pending. Платежи разделяют личные orders/refunds и organization payouts по active actor permissions. Не смешивай собственную оплату участия с ручным управлением чужими платежами.

Добавь loading/empty/error/offline и deep links к payment.details. Реальный provider будет подключаться в блоке платежей.

Через iOS-плагин проверь tables/cards, ru-RU currency formatting и 200% text.
Проверки: permission projections и no fabricated totals.
Commit: feat: scaffold profile statistics and payments views
```

## 029 — Аудит категории профиля

```text
Audit-only. Не добавляй новые секции профиля.

Проверь 020–028: количество запросов home, activity pagination, player directory, picker returnTo, calendar date boundaries, filtered views, public privacy projections, trainer placeholders, statistics/payments permissions. Убедись, что Профиль не содержит создание/управление событиями, а Настройки не подменяют личную активность.

Через iOS-плагин пройди root Profile и все вложенные routes при light/dark, 320/430 pt, 200% text и VoiceOver. Запусти RLS negative tests на public/private fields.

Исправляй только доказанные ошибки категории.
Проверки: integration suite, navigation validators, privacy report.
Commit: test: audit profile and personal activity category
```
