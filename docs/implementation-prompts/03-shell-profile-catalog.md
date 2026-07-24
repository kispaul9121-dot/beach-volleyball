# Блок 3 — оболочка, профиль и каталог

## 017 — Профиль как корневая вкладка

```text
Реализуй home.main как компактный корневой экран active actor.

Прочитай PROFILE_ACTIVITY.yaml, PROFILE_CONNECTIONS.yaml и home/main.md.

Сделай:
1. Header active actor с открытием actor.switcher.
2. Ближайшие подтверждённые участия и переход ко всей активности.
3. Компактные связи: мои игроки, тренерские/организационные контексты только когда разрешены.
4. Никакой кнопки +, создания или управления событиями.
5. Не показывай нерешённое приглашение как участие.
6. Для trainer/organization адаптируй данные, но не меняй структуру нижней навигации.
7. Состояния empty, loading, error, offline cached и actor unavailable.

Тесты: no create action, canonical entity link, actor switch preservation и invitation exclusion.

Commit: feat: implement profile home tab
```

## 018 — Единая личная активность и совместимые фильтры

```text
Реализуй profile.activity и совместимые route views profile.my_games, competitions, trainings и trips без копирования четырёх отдельных списков.

Сделай один ActivityFeed engine с параметрами type/status/timeframe. Root показывает Предстоящие/Прошедшие; совместимые маршруты передают preset и сохраняют back_fallback.

Правила:
- участие, заявка, payment_required и waitlist отображаются с разными status labels;
- unresolved invitation не входит в activity;
- управление здесь отсутствует;
- завершённые события открывают canonical details/archive state;
- фильтры восстанавливаются после возврата;
- пагинация не смешивает active actor ownership с личным участием человека.

Тесты: presets, empty per filter, duplicate suppression, timezone/date boundaries и deep links.

Commit: feat: implement unified personal activity feed
```

## 019 — Настройки root и appearance preference

```text
Реализуй profile.main и минимальную навигацию настроек.

Область: account summary, actor profiles link, payments link, security/privacy placeholders и appearance selector light/dark/system.

Не реализуй глубокие security или notification settings без соответствующего отдельного промта/контракта. Для definition_pending разделов используй строки с честным статусом «Будет доступно позже», но только если маршрут зарегистрирован; иначе не показывай кликабельность.

Appearance изменяет runtime theme из промта 006 и сохраняется. Основной default — light.

Тесты: theme persistence, unavailable route has no press action, actor-specific finance visibility и no archives in Settings.

Commit: feat: implement settings root and appearance
```

## 020 — Управление actor-профилями

```text
Реализуй profile.actor_profiles поверх actor service промта 015.

Сделай:
1. Список player/trainer/organization profiles со статусами.
2. Добавление optional actor через onboarding continuation.
3. Редактирование только утверждённых полей.
4. Отключение optional actor с impact preview; player удалить нельзя.
5. Нельзя отключить actor при незавершённых обязательствах без authoritative server resolution.
6. После изменения active actor корректно пересчитывается.
7. Не добавляй staff membership в этот экран: это не actor profile.

Тесты: player protection, active actor removal fallback, pending obligations и stale response.

Commit: feat: implement actor profile management
```

## 021 — Мои игроки и единый player picker

```text
Реализуй profile.players и инфраструктуру player.picker.

Прочитай PLAYER_DIRECTORY.yaml и shared/player-picker.md.

Profile screen:
- односторонний список сохранённых игроков active actor;
- поиск/добавление без подтверждения дружбы;
- открытие public player profile;
- trainer requests показывай только по утверждённому контракту.

Picker modal:
- вкладки Мои игроки, Недавние, Поиск;
- single/multi select по контексту;
- обязательные entity/draft context и returnTo;
- не даёт доступ к закрытым данным;
- не создаёт участие до подтверждённого действия вызывающего сценария.

Тесты: duplicate selection, context isolation, permission revoked, cancel preserves draft.

Commit: feat: implement player directory and picker
```

## 022 — Каталог Игры: discovery, категории и приглашения

```text
Реализуй discovery-состояние play.main.

Сделай:
1. Категории Игры, Тренировки, Турниры.
2. Публичный каталог с сортировкой ближайшее сначала.
3. Приоритетный блок `Вас пригласили · N` над категориями, максимум две карточки.
4. Invitation card: semantic green emphasis, badge ПРИГЛАШЕНИЕ, action только Открыть.
5. Accept/decline внутри invitation.details, не inline.
6. Турниры имеют только Все · Классика и два формата.
7. `Король пляжа` в поиске ведёт к разовой Тунисской лестнице.
8. Search/filter shell использует зарегистрированные actions; сложные фильтры могут остаться placeholder при definition_pending.

Тесты: invitation count, public visibility, search alias, category restoration и guest access.

Commit: feat: implement play discovery catalog
```

## 023 — Режим управления и pull-down архив

```text
Реализуй management mode play.main по MANAGEMENT_CENTER.yaml.

Сделай:
1. Явное переключение `Режим управления`.
2. Категории games/trainings/tournaments и фильтры Все, Черновики, Требуют действий, Опубликованы, Идут.
3. Показывай только сущности, которыми active actor реально может управлять.
4. Creation entry находится здесь, а не в Профиле.
5. Archive открывается overscroll pull-down: reveal 24dp, armed 72dp, утверждённые подписи.
6. Pull-to-refresh в management mode отключён; accessibility action `Открыть архив` обязателен.
7. Reduce Motion использует статичную индикацию.
8. Route `/play?mode=archive` read-only и не показывает create controls.

Тесты: gesture thresholds, refresh conflict, permission loss fallback, category preserved, completed excluded from active.

Commit: feat: implement contextual management and archive
```

## 024 — Контрольный аудит оболочки, профиля и каталога

```text
Audit-only. Проверь промты 017–023 и не добавляй новые разделы.

Проверь:
- ровно одна нижняя навигация;
- Профиль не содержит create/manage;
- Settings не содержит личные архивы;
- activity не содержит unresolved invitations;
- invitation block не принимает приглашение inline;
- player picker не создаёт участие;
- management mode фильтруется capabilities;
- archive не имеет постоянной кнопки и доступен screen reader;
- возврат восстанавливает category/filter/scroll;
- 320px и 200% text scaling не ломают chips/header/tab bar.

Добавь navigation integration tests и исправь только дефекты блока. Обнови IMPLEMENTATION_STATUS.

Commit: test: audit shell profile and catalog flows
```