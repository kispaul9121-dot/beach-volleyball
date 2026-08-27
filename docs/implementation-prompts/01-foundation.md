# Блок 1 — запуск и пять базовых вкладок

## 000 — Базовый запуск Codex, iOS-плагина и backend

```text
Работай по docs/implementation-prompts/README.md. Это нулевой запуск, до него продуктовые экраны не реализуются.

Прочитай AGENTS.md, ARCHITECTURE.md, DATA_MODEL.md, DESIGN_SYSTEM.md, DESIGN_TOKENS.yaml, ROUTES.yaml, SCREENS.yaml и ACTIONS.yaml. Определи точное имя установленного iOS-плагина Codex и фактический способ вызова через @-упоминание. Не угадывай имя. Запиши mention, доступность и обнаруженные возможности в docs/IMPLEMENTATION_RUNTIME.yaml.

Проверь Supabase plugin/MCP. Если он не подключён, не устанавливай и не авторизуй его молча: запиши blocked_by_connection и выведи требуемое действие. Проверь Node, Expo, Xcode, iOS Simulator и запуск существующего проекта. Сохрани текущую реализацию; создавай Expo Router shell только если его нет.

Зафиксируй backend baseline: Supabase Postgres/Auth/Storage/Realtime, Edge Functions для секретных операций, Expo SQLite для сессии и будущего cache. Создай .env.example без секретов и IMPLEMENTATION_STATUS.yaml.

Проверки: architecture validators, typecheck/lint при наличии, один фактический iOS smoke launch через плагин либо честный blocked-отчёт.
Commit: chore: bootstrap Codex iOS runtime and Supabase baseline
```

## 001 — Базовый экран «Профиль»

```text
Работай по runbook и IMPLEMENTATION_RUNTIME.yaml. Реализуй только основу home.main — корневой вкладки «Профиль».

Собери ScreenHeader, вход в actor switcher, компактный header active actor, секции будущей активности и системные loading/empty/error/offline placeholders. Все кликабельные строки свяжи с существующими action_id и маршрутами: активность, Мои игроки, календарь, публичный профиль. Не реализуй содержимое этих разделов и не добавляй создание/управление событиями.

Данные пока идут через typed repository interface с детерминированными fixtures; UI не должен знать, mock это или будущий Supabase adapter. Нижняя навигация единая, активна вкладка «Профиль».

Вызови iOS-плагин: проверь safe area, 320–430 pt, 200% Dynamic Type, VoiceOver labels и переходы назад/deep link.
Проверки: component tests базовых состояний, route/action validation, отсутствие локальных копий shared UI.
Commit: feat: add profile tab foundation and navigation
```

## 002 — Базовый экран «Игры»

```text
Реализуй только основу play.main. Не подключай настоящую базу и не достраивай карточки detail-экранов.

Покажи категории Игры, Тренировки, Турниры, место для приоритетного блока приглашений и переключение обычного/управленческого режима согласно GAMES_CATALOG.yaml и MANAGEMENT_CENTER.yaml. Используй общий EntityCard и horizontal FilterChip row. Карточки и create actions ведут только на канонические маршруты с action_id; незаконченные фильтры и pull-down архив остаются честными placeholders.

Создай PlayRepository interface и fixtures отдельно от компонентов. Не показывай manage actions пользователю без permission.

Через iOS-плагин проверь вертикальный scroll, горизонтальные chips, safe area, нижнюю вкладку «Игры» и все доступные переходы.
Проверки: guest/player/trainer/organization variants, route validation, empty/error/offline states.
Commit: feat: add games tab foundation and canonical transitions
```

## 003 — Базовый экран «Чаты»

```text
Реализуй основу chats.main и минимальную оболочку chat.details без Supabase Realtime.

Список показывает один канонический conversation на сущность, avatar/type marker, unread badge и переход в /chats/:chatId. Не создавай отдельные копии чатов внутри игр, тренировок или кэмпов. Используй ChatRepository interface и fixtures.

В chat.details добавь header, список сообщений placeholder, keyboard-safe поле ввода, disabled send при пустом тексте и переход к связанной сущности. Для гостя или неподтверждённого участника показывай permission state, а не пустую историю.

Вызови iOS-плагин и проверь появление клавиатуры, нижний safe area, scroll-to-bottom, системный back gesture, длинные сообщения и VoiceOver.
Проверки: canonical conversation invariant в тестах, route/action validators, no duplicate chat shell.
Commit: feat: add chats tab and conversation shell
```

## 004 — Базовый экран «Кэмпы»

```text
Реализуй основу camps.main, не копируя play.main целиком.

Переиспользуй общие catalog primitives и EntityCard, но оставь отдельный CampsRepository. Покажи каталог, management mode и placeholders фильтров/архива. Карточка ведёт на tour.details; создание — на tour.create с actorId и returnTo. Бронирование, проживание, документы и программа пока не получают выдуманную бизнес-логику: показывай definition_pending или disabled future entry.

Данные — fixtures за repository boundary. Нижняя навигация единая, активна «Кэмпы».

Через iOS-плагин проверь scroll, safe area, таб, карточки, create transition и возврат.
Проверки: role variants, no duplicated catalog component, loading/empty/error/offline states.
Commit: feat: add camps tab foundation and routes
```

## 005 — Базовый экран «Настройки»

```text
Реализуй основу profile.main для пятой вкладки «Настройки».

Секции: аккаунт, actor-профили, уведомления, приватность, внешний вид, платежи и безопасность. Веди только на существующие ROUTES/ACTIONS. Неутверждённые настройки показывай disabled с понятной подписью «Позже» или как definition_pending; не создавай фиктивное сохранение.

Светлая тема — primary; system и dark поддерживаются архитектурно. Экран использует только semantic tokens, без локальных hex. Сохраняй выбранный appearance через абстрактный settings repository.

Через iOS-плагин проверь переключение appearance, Dynamic Type, safe area, accessibility focus и переходы.
Проверки: theme component tests, route/action validators, отсутствие личных архивов в Настройках.
Commit: feat: add settings tab foundation and actions
```

## 006 — Сине-белая semantic дизайн-система

```text
Синхронизируй DESIGN_SYSTEM.md, DESIGN_TOKENS.yaml, UI_RULES.md, AGENTS.md и scripts/validate_design_system.py с утверждённым light-first направлением.

Значения палитры хранятся только в DESIGN_TOKENS.yaml: белые/светлые surfaces, основной синий action, тёмно-синий text, нейтральные серо-синие borders, success green, warning amber, danger red, info cyan/blue. Экранные файлы используют только semantic tokens. Dark и system остаются полноценными режимами, но primary_mode = light.

Создай или обнови ThemeProvider и tests для token completeness, contrast и запрета hard-coded цветов. Не редизайнь пять экранов из 001–005; они должны автоматически получить новые значения через токены.

Вызови iOS-плагин и сделай light/dark screenshots одного общего component gallery.
Проверки: design validator, contrast, 200% text, no hex outside token source.
Commit: feat: approve light-first blue-white design tokens
```

## 007 — Каталог общих UI-компонентов

```text
Заверши базовый каталог UI без изменения бизнес-сценариев.

Реализуй или нормализуй AppScreen, ScreenHeader, AppTabBar, Button, IconButton, FilterChip, StatusBadge, SurfaceCard, EntityCard, TextField, SearchField, Avatar, InfoRow, EmptyState, ErrorState, Skeleton и BottomSheet. Сохрани публичные API уже используемых компонентов. Новый variant добавляй только при доказанной потребности пяти базовых вкладок.

Для каждого компонента нужны default/pressed/focused/disabled/loading/error состояния, accessibility role/label и preview при 200% text. Не подключай крупный внешний UI-kit и вторую icon library.

Через iOS-плагин проверь component gallery, touch targets 48×48 и keyboard focus.
Проверки: snapshot/component tests, lint/typecheck, no screen-local Button/Card/Header.
Commit: feat: establish reusable mobile UI component catalog
```

## 008 — Expo Router, deep links и возвраты

```text
Собери реальную навигационную основу по ROUTES.yaml, SCREENS.yaml, ACTIONS.yaml и NAVIGATION_RESOLVERS.yaml.

Настрой tabs, stack groups, modals, system overlays, back_fallback, actorId и returnTo. Пять root tabs неизменны: Профиль, Игры, Чаты, Кэмпы, Настройки. Не создавай вторую tab shell. Каждый доступный action из экранов 001–005 должен вести на канонический route или system action; неизвестное действие остаётся disabled.

Добавь route typing и tests для прямых deep links, cold start, malformed params, back gesture и permission redirect. Не меняй продуктовые URL ради удобства реализации.

Вызови iOS-плагин: пройди все пять вкладок, stack push/pop, modal dismiss и cold deep link.
Проверки: navigation/architecture validators и отрицательные route tests.
Commit: feat: wire canonical Expo Router navigation and deep links
```

## 009 — Контроль первых шести промтов и фундамента

```text
Audit-only. Не добавляй новые продуктовые функции.

Проверь результаты 000–008: IMPLEMENTATION_RUNTIME.yaml, фактический iOS plugin mention, backend status, пять нижних вкладок, общие компоненты, light-first tokens, Router, action_id, placeholders и IMPLEMENTATION_STATUS.yaml.

Запусти все validators, typecheck, lint и существующие tests. Через iOS-плагин выполни один сквозной smoke: cold launch → Профиль → Игры → Чаты → Кэмпы → Настройки → обратные переходы. Проверь ширины 320/390/430, 200% text, light/dark, VoiceOver и Reduce Motion.

Исправляй только доказанные ошибки фундамента. Не подключай Supabase data и не реализуй detail-сценарии.
Проверки: финальный отчёт с passed/failed/blocked и ссылками на точные файлы.
Commit: test: audit bootstrap and five-tab foundation
```
