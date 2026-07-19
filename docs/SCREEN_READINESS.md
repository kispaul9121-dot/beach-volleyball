# Готовность экранов VolleyPlay

Таблица автоматически проверяет каждый экран из `SCREENS.yaml` по десяти архитектурным критериям и сверяет `ROUTES.yaml`, `ACTIONS.yaml` и соответствующий файл в `docs/screens/`.

> Это аудит полноты документации, а не доказательство UX-удобства. UX подтверждается только прототипом и тестированием с пользователями.

## Итог

- Экранов проверено: **54**.
- Средняя архитектурная готовность: **86%**.
- Готово: **29**.
- Частично: **25**.
- Слабо описано: **0**.

## Десять критериев

1. **ID и маршрут**.
2. **Профили и права**.
3. **Назначение и данные**.
4. **Блоки**.
5. **Действия**.
6. **Состояния**.
7. **Варианты ролей**.
8. **Навигация**.
9. **Интеграции**.
10. **Спецификация**.

Обозначения: `✅` — подтверждено; `◐` — частично; `○` — отсутствует; `—` — не применяется.

## Матрица

| Экран | Route | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | Итог |
|---|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|---:|
| **Добро пожаловать**<br><code>auth.welcome</code> | <code>/auth</code> | ✅ | ✅ | ✅ | ◐ | ✅ | ◐ | — | ✅ | — | ✅ | **88% · готово** |
| **Вход**<br><code>auth.sign_in</code> | <code>/auth/sign-in</code> | ✅ | ✅ | ✅ | ◐ | ✅ | ◐ | — | ✅ | — | ✅ | **88% · готово** |
| **Регистрация по email**<br><code>auth.email_registration</code> | <code>/auth/register</code> | ✅ | ✅ | ✅ | ◐ | ✅ | ◐ | — | ✅ | — | ✅ | **88% · готово** |
| **Подтверждение email**<br><code>auth.verify_email</code> | <code>/auth/verify</code> | ✅ | ✅ | ✅ | ◐ | ✅ | ◐ | — | ✅ | ✅ | ✅ | **89% · готово** |
| **Восстановление пароля**<br><code>auth.reset_password</code> | <code>/auth/reset-password</code> | ✅ | ✅ | ✅ | ◐ | ◐ | ◐ | — | ✅ | — | ✅ | **81% · частично** |
| **Выбор профилей**<br><code>onboarding.profile_selection</code> | <code>/onboarding/profiles</code> | ✅ | ✅ | ✅ | ◐ | ✅ | ◐ | — | ✅ | ✅ | ✅ | **89% · готово** |
| **Профиль игрока**<br><code>onboarding.player</code> | <code>/onboarding/player</code> | ✅ | ✅ | ✅ | ◐ | ✅ | ◐ | — | ✅ | ✅ | ✅ | **89% · готово** |
| **Профиль тренера**<br><code>onboarding.trainer</code> | <code>/onboarding/trainer</code> | ✅ | ✅ | ✅ | ◐ | ✅ | ◐ | — | ✅ | ✅ | ✅ | **89% · готово** |
| **Профиль организации**<br><code>onboarding.organization</code> | <code>/onboarding/organization</code> | ✅ | ✅ | ✅ | ◐ | ✅ | ◐ | — | ✅ | ✅ | ✅ | **89% · готово** |
| **Разрешения**<br><code>onboarding.permissions</code> | <code>/onboarding/permissions</code> | ✅ | ✅ | ✅ | ◐ | ◐ | ◐ | — | ✅ | ✅ | ✅ | **83% · частично** |
| **Переключить профиль**<br><code>actor.switcher</code> | <code>system://actor-switcher</code> | ✅ | ✅ | ◐ | ✅ | ✅ | ◐ | — | ◐ | ✅ | ✅ | **83% · частично** |
| **Добавить игроков**<br><code>player.picker</code> | <code>system://player-picker</code> | ✅ | ✅ | ✅ | ◐ | ✅ | ✅ | — | ✅ | ✅ | ✅ | **94% · готово** |
| **Уведомления**<br><code>global.notifications</code> | <code>/notifications</code> | ✅ | ✅ | ✅ | ✅ | ✅ | ◐ | — | ◐ | ✅ | ✅ | **89% · готово** |
| **Профиль**<br><code>home.main</code> | <code>/</code> | ✅ | ✅ | ✅ | ◐ | ✅ | ◐ | ✅ | ✅ | ✅ | ✅ | **90% · готово** |
| **Вся моя активность**<br><code>profile.activity</code> | <code>/activity</code> | ✅ | ✅ | ✅ | ✅ | ✅ | ◐ | ✅ | ✅ | ✅ | ✅ | **95% · готово** |
| **Игры**<br><code>play.main</code> | <code>/play</code> | ✅ | ✅ | ✅ | ✅ | ✅ | ◐ | ✅ | ✅ | ✅ | ✅ | **95% · готово** |
| **Чаты**<br><code>chats.main</code> | <code>/chats</code> | ✅ | ✅ | ✅ | ✅ | ✅ | ○ | ✅ | ✅ | ◐ | ✅ | **85% · частично** |
| **Чат**<br><code>chat.details</code> | <code>/chats/:chatId</code> | ✅ | ✅ | ✅ | ◐ | ✅ | ✅ | ✅ | ◐ | ✅ | ✅ | **90% · готово** |
| **Кэмпы**<br><code>camps.main</code> | <code>/camps</code> | ✅ | ✅ | ✅ | ✅ | ✅ | ◐ | ✅ | ✅ | ◐ | ✅ | **90% · готово** |
| **Клуб**<br><code>club.details</code> | <code>/clubs/:clubId</code> | ✅ | ✅ | ◐ | ✅ | ◐ | ◐ | ✅ | ◐ | ✅ | ✅ | **80% · частично** |
| **Управление клубом**<br><code>club.manage</code> | <code>/clubs/:clubId/manage</code> | ✅ | ✅ | ✅ | ✅ | ◐ | ✅ | ✅ | ✅ | ✅ | ✅ | **95% · готово** |
| **Площадка**<br><code>venue.details</code> | <code>/venues/:venueId</code> | ✅ | ✅ | ◐ | ✅ | ◐ | ○ | ◐ | ◐ | ◐ | ◐ | **60% · частично** |
| **Игрок**<br><code>player.public_profile</code> | <code>/players/:playerId</code> | ✅ | ✅ | ◐ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | **95% · готово** |
| **Тренер**<br><code>trainer.public_profile</code> | <code>/trainers/:trainerId</code> | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | **100% · готово** |
| **Найти тренера**<br><code>trainer.search</code> | <code>/trainers/search</code> | ✅ | ✅ | ✅ | ✅ | ✅ | ◐ | ✅ | ✅ | ✅ | ✅ | **95% · готово** |
| **Настройки**<br><code>profile.main</code> | <code>/profile</code> | ✅ | ✅ | ✅ | ✅ | ✅ | ◐ | ✅ | ✅ | ✅ | ✅ | **95% · готово** |
| **Мои профили**<br><code>profile.actor_profiles</code> | <code>/profile/actors</code> | ✅ | ◐ | ◐ | ✅ | ◐ | ◐ | ✅ | ◐ | ✅ | ✅ | **75% · частично** |
| **Мой календарь**<br><code>profile.calendar</code> | <code>/profile/calendar</code> | ✅ | ✅ | ◐ | ✅ | ✅ | ◐ | ✅ | ✅ | ✅ | ✅ | **90% · готово** |
| **Мои игры**<br><code>profile.my_games</code> | <code>/profile/games</code> | ✅ | ◐ | ✅ | ✅ | ✅ | ○ | ◐ | ✅ | ✅ | ◐ | **75% · частично** |
| **Мои турниры**<br><code>profile.competitions</code> | <code>/profile/competitions</code> | ✅ | ◐ | ✅ | ✅ | ✅ | ○ | ◐ | ✅ | ✅ | ◐ | **75% · частично** |
| **Мои тренировки**<br><code>profile.trainings</code> | <code>/profile/trainings</code> | ✅ | ◐ | ✅ | ✅ | ✅ | ○ | ◐ | ✅ | ✅ | ◐ | **75% · частично** |
| **Мои игроки**<br><code>profile.players</code> | <code>/profile/players</code> | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | **100% · готово** |
| **Мои кэмпы**<br><code>profile.trips</code> | <code>/profile/trips</code> | ✅ | ◐ | ✅ | ✅ | ◐ | ○ | ◐ | ✅ | ✅ | ◐ | **70% · частично** |
| **Статистика**<br><code>profile.statistics</code> | <code>/profile/statistics</code> | ✅ | ✅ | ✅ | ◐ | ◐ | ◐ | ✅ | ✅ | ◐ | ✅ | **80% · частично** |
| **Платежи**<br><code>profile.payments</code> | <code>/profile/payments</code> | ✅ | ✅ | ✅ | ◐ | ✅ | ◐ | ✅ | ✅ | ✅ | ✅ | **90% · готово** |
| **Аккаунт и приложение**<br><code>profile.settings</code> | <code>/profile/settings</code> | ✅ | ◐ | ✅ | ◐ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | **90% · готово** |
| **Игра**<br><code>game.details</code> | <code>/games/:gameId</code> | ✅ | ✅ | ✅ | ◐ | ◐ | ✅ | ✅ | ✅ | ✅ | ✅ | **90% · готово** |
| **Создание игры**<br><code>game.create</code> | <code>/games/create</code> | ✅ | ◐ | ✅ | ✅ | ◐ | ◐ | ✅ | ◐ | ✅ | ✅ | **80% · частично** |
| **Управление игрой**<br><code>game.manage</code> | <code>/games/:gameId/manage</code> | ✅ | ✅ | ✅ | ✅ | ◐ | ◐ | ✅ | ✅ | ✅ | ✅ | **90% · готово** |
| **Тренировка**<br><code>training.details</code> | <code>/trainings/:trainingId</code> | ✅ | ✅ | ✅ | ✅ | ◐ | ◐ | ✅ | ✅ | ✅ | ✅ | **90% · готово** |
| **Создание тренировки**<br><code>training.create</code> | <code>/trainings/create</code> | ✅ | ✅ | ✅ | ✅ | ◐ | ○ | ✅ | ✅ | ✅ | ✅ | **85% · частично** |
| **Управление тренировкой**<br><code>training.manage</code> | <code>/trainings/:trainingId/manage</code> | ✅ | ✅ | ✅ | ✅ | ✅ | ◐ | ✅ | ✅ | ✅ | ✅ | **95% · готово** |
| **Посещаемость**<br><code>training.attendance</code> | <code>/trainings/:trainingId/attendance</code> | ✅ | ✅ | ✅ | ✅ | ✅ | ◐ | ✅ | ✅ | ✅ | ✅ | **95% · готово** |
| **Турнир**<br><code>tournament.details</code> | <code>/tournaments/:tournamentId</code> | ✅ | ✅ | ✅ | ✅ | ✅ | ○ | ✅ | ✅ | ✅ | ✅ | **90% · частично** |
| **Создание турнира**<br><code>tournament.create</code> | <code>/tournaments/create</code> | ✅ | ◐ | ✅ | ✅ | ✅ | ○ | ✅ | ✅ | ✅ | ✅ | **85% · частично** |
| **Управление турниром**<br><code>tournament.manage</code> | <code>/tournaments/:tournamentId/manage</code> | ✅ | ✅ | ✅ | ✅ | ✅ | ○ | ✅ | ✅ | ✅ | ✅ | **90% · частично** |
| **Матч**<br><code>competition.match</code> | <code>/matches/:matchId</code> | ✅ | ◐ | ✅ | ✅ | ✅ | ○ | ◐ | ◐ | ✅ | ✅ | **75% · частично** |
| **Кэмп**<br><code>tour.details</code> | <code>/tours/:tourId</code> | ✅ | ✅ | ◐ | ✅ | ✅ | ○ | ✅ | ✅ | ✅ | ✅ | **85% · частично** |
| **Создание кэмпа**<br><code>tour.create</code> | <code>/tours/create</code> | ✅ | ◐ | ◐ | ✅ | ✅ | ○ | ✅ | ✅ | ✅ | ◐ | **75% · частично** |
| **Управление кэмпом**<br><code>tour.manage</code> | <code>/tours/:tourId/manage</code> | ✅ | ✅ | ◐ | ✅ | ○ | ○ | ✅ | ✅ | ✅ | ✅ | **75% · частично** |
| **Бронирование кэмпа**<br><code>tour.booking</code> | <code>/tours/:tourId/booking</code> | ✅ | ◐ | ◐ | ✅ | ◐ | ○ | ✅ | ✅ | ✅ | ✅ | **75% · частично** |
| **Оплата**<br><code>payment.checkout</code> | <code>/payments/checkout/:orderId</code> | ✅ | ◐ | ◐ | ◐ | ◐ | ◐ | ◐ | ✅ | ✅ | ✅ | **70% · частично** |
| **Детали платежа**<br><code>payment.details</code> | <code>/payments/:paymentId</code> | ✅ | ✅ | ◐ | ◐ | ✅ | ◐ | ◐ | ✅ | ✅ | ✅ | **80% · частично** |
| **Приглашение**<br><code>invitation.details</code> | <code>/invitations/:invitationId</code> | ✅ | ◐ | ✅ | ✅ | ◐ | ◐ | ◐ | ◐ | ✅ | ✅ | **75% · частично** |

## Сводка по критериям

| № | Критерий | ✅ | ◐ | ○ | — |
|---:|---|---:|---:|---:|---:|
| 1 | ID и маршрут | 54 | 0 | 0 | 0 |
| 2 | Профили и права | 41 | 13 | 0 | 0 |
| 3 | Назначение и данные | 42 | 12 | 0 | 0 |
| 4 | Блоки | 35 | 19 | 0 | 0 |
| 5 | Действия | 37 | 16 | 1 | 0 |
| 6 | Состояния | 8 | 31 | 15 | 0 |
| 7 | Варианты ролей | 32 | 9 | 0 | 13 |
| 8 | Навигация | 45 | 9 | 0 | 0 |
| 9 | Интеграции | 46 | 4 | 0 | 4 |
| 10 | Спецификация | 48 | 6 | 0 | 0 |

## Первые экраны на доработку

Ниже показаны экраны с наименьшей подтверждённой готовностью; причины берутся непосредственно из результатов проверки.

- **Площадка** (`venue.details`, 60%): нет: Состояния; частично: Назначение и данные, Действия, Варианты ролей, Навигация, Интеграции, Спецификация.
- **Мои кэмпы** (`profile.trips`, 70%): нет: Состояния; частично: Профили и права, Действия, Варианты ролей, Спецификация.
- **Оплата** (`payment.checkout`, 70%): частично: Профили и права, Назначение и данные, Блоки, Действия, Состояния, Варианты ролей.
- **Мои турниры** (`profile.competitions`, 75%): нет: Состояния; частично: Профили и права, Варианты ролей, Спецификация.
- **Мои игры** (`profile.my_games`, 75%): нет: Состояния; частично: Профили и права, Варианты ролей, Спецификация.
- **Мои тренировки** (`profile.trainings`, 75%): нет: Состояния; частично: Профили и права, Варианты ролей, Спецификация.
- **Мои профили** (`profile.actor_profiles`, 75%): частично: Профили и права, Назначение и данные, Действия, Состояния, Навигация.
- **Матч** (`competition.match`, 75%): нет: Состояния; частично: Профили и права, Варианты ролей, Навигация.
- **Приглашение** (`invitation.details`, 75%): частично: Профили и права, Действия, Состояния, Варианты ролей, Навигация.
- **Бронирование кэмпа** (`tour.booking`, 75%): нет: Состояния; частично: Профили и права, Назначение и данные, Действия.
- **Создание кэмпа** (`tour.create`, 75%): нет: Состояния; частично: Профили и права, Назначение и данные, Спецификация.
- **Управление кэмпом** (`tour.manage`, 75%): нет: Действия, Состояния; частично: Назначение и данные.
- **Клуб** (`club.details`, 80%): частично: Назначение и данные, Действия, Состояния, Навигация.
- **Статистика** (`profile.statistics`, 80%): частично: Блоки, Действия, Состояния, Интеграции.
- **Создание игры** (`game.create`, 80%): частично: Профили и права, Действия, Состояния, Навигация.

## Как обновлять

После изменения `SCREENS.yaml`, `ROUTES.yaml`, `ACTIONS.yaml` или файлов `docs/screens/` запусти:

```bash
python scripts/generate_screen_readiness.py
```

CI запускает команду с `--check` и сообщает, когда таблица устарела.

Машиночитаемые результаты и объяснение каждой оценки находятся в `docs/SCREEN_READINESS.yaml`.
