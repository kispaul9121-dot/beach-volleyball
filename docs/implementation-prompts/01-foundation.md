# Блок 1 — фундамент проекта

## 001 — Синхронизация сине-белой дизайн-системы

```text
Работай по docs/implementation-prompts/README.md.

Цель: устранить противоречие между старым dark-first контрактом и утверждённым классическим сине-белым light-first направлением. Не реализуй экраны приложения.

Прочитай: AGENTS.md, docs/DECISIONS.md, docs/DESIGN_SYSTEM.md, docs/DESIGN_TOKENS.yaml, docs/UI_RULES.md, scripts/validate_design_system.py и workflow проверки архитектуры.

Сделай:
1. Добавь решение о light-first сине-белой системе в DECISIONS.md.
2. Синхронно обнови AGENTS.md, DESIGN_SYSTEM.md, DESIGN_TOKENS.yaml и UI_RULES.md.
3. Утверди semantic palette в DESIGN_TOKENS.yaml: белые/светлые поверхности, основной синий, тёмно-синий текст, нейтральные серо-синие границы, success green, warning amber, danger red, info cyan/blue.
4. Light — основной режим; dark и system остаются поддерживаемыми архитектурно.
5. Hard-coded цвета внутри экранов и компонентов остаются запрещены; значения допустимы только в токенах темы.
6. Обнови validate_design_system.py, чтобы он проверял новую стратегию, утверждённую палитру и наличие обязательных semantic roles.
7. Найди по репозиторию остаточные обязательные требования dark-first и исправь только прямые противоречия.

Проверки:
- YAML парсится;
- все архитектурные validators проходят;
- DESIGN_SYSTEM.md не содержит прямых hex-значений;
- validator падает при возврате required_primary_mode=dark;
- нижняя навигация и размеры компонентов не меняются.

Commit: docs: approve light-first blue white design system
```

## 002 — Инвентаризация фактической реализации

```text
Работай по runbook. Этот промт не реализует продуктовые функции.

Цель: создать честную карту текущего состояния кода, чтобы последующие агенты не переписывали сделанное и не считали документацию готовым приложением.

Прочитай весь корень репозитория, package manifests, src/app директории при наличии, SCREEN_READINESS.yaml, SCREENS.yaml, ROUTES.yaml, ACTIONS.yaml и specs.

Сделай:
1. Создай docs/IMPLEMENTATION_STATUS.yaml.
2. Для каждого screen_id и ключевого инфраструктурного блока укажи status: implemented, partial, placeholder, definition_pending, not_started или blocked.
3. Для каждого статуса добавь evidence: реальные пути файлов, тесты, маршрут, mock-only или отсутствие кода.
4. Отдельно зафиксируй наличие/отсутствие мобильного проекта, backend, БД, auth provider, realtime, payments и push.
5. Не изменяй SCREEN_READINESS.yaml: это готовность спецификаций, а не кода.
6. Добавь timestamp, audited_commit и правила обновления статуса.
7. Если код отсутствует, так и напиши; не создавай пустые экраны ради улучшения метрики.

Проверки:
- каждый SCREENS.yaml id присутствует в manifest;
- нет статуса implemented без кода и тестового evidence;
- нет абсолютных локальных путей;
- YAML детерминированно сортируется по разделам.

Commit: docs: add evidence based implementation status
```

## 003 — Инициализация Expo-проекта без уничтожения существующего кода

```text
Работай по runbook и IMPLEMENTATION_STATUS.yaml.

Цель: получить запускаемый React Native + TypeScript + Expo Router проект. Если мобильный проект уже существует, не создавай новый — проведи точечный аудит и дополни отсутствующую основу.

Прочитай DESIGN_SYSTEM.md, DESIGN_TOKENS.yaml, ROUTES.yaml и текущие package/config файлы.

Сделай:
1. При отсутствии проекта инициализируй Expo TypeScript приложение в корне или уже утверждённой app-директории.
2. Используй совместимые версии текущего Expo SDK через expo install и зафиксируй lockfile.
3. Подключи Expo Router, safe-area-context, react-native-screens, gesture-handler, reanimated/worklets, lucide-react-native и react-native-svg.
4. Настрой New Architecture согласно текущему Expo SDK.
5. Создай только технический root layout и neutral bootstrap screen; продуктовые экраны пока не реализуй.
6. Добавь env example без секретов и разделение public/server variables.
7. Сохрани любой существующий код; миграции делай малыми commits внутри одного логического изменения.

Проверки:
- clean install;
- Expo config validation;
- TypeScript compile;
- запуск iOS/Android bundler без route errors;
- секреты и локальные env не попадают в Git.

Commit: build: initialize expo mobile foundation
```

## 004 — Инструменты качества и единая команда проверки

```text
Цель: создать стабильный quality gate, не меняя продуктовый UI.

Прочитай package scripts, workflows, scripts/*.py и существующие тестовые настройки.

Сделай:
1. Настрой strict TypeScript без массового any.
2. Добавь ESLint и Prettier или сохрани существующие инструменты, если они уже утверждены.
3. Настрой unit/component test runner, совместимый с Expo/React Native.
4. Добавь команды: typecheck, lint, format:check, test, test:ci, validate:architecture и verify.
5. verify должна последовательно запускать архитектурные validators и проверки кода.
6. Обнови GitHub Actions так, чтобы docs-only ветка продолжала проверяться, а кодовая ветка дополнительно проходила install/typecheck/lint/tests.
7. Кэш не должен скрывать отсутствующий lockfile или падение install.
8. Не вводи требования 100% coverage; установи разумный baseline и отчёт.

Проверки:
- verify проходит локально;
- намеренная TypeScript ошибка ломает CI;
- намеренно устаревший SCREEN_READINESS ломает CI;
- workflow не использует секреты для pull_request проверки.

Commit: ci: add unified implementation quality gate
```

## 005 — Архитектура каталогов и границы модулей

```text
Цель: заложить структуру, в которой будущие экраны не будут импортировать бизнес-логику друг у друга.

Прочитай ARCHITECTURE.md, DATA_MODEL.md, ENTITY_SECTIONS.yaml, CAPABILITIES.yaml и фактическую структуру проекта.

Создай или адаптируй:
- app/ или src/app — только маршруты Expo Router;
- src/ui — общие визуальные примитивы;
- src/features — пользовательские сценарии;
- src/entities — типы и представление сущностей;
- src/domain — чистые правила игр и турниров;
- src/services — API, storage, auth, payments, notifications;
- src/state — глобальные stores только при реальной необходимости;
- src/testing — fixtures и test utilities.

Правила:
1. Route files остаются тонкими.
2. Domain не импортирует React Native, router или network clients.
3. UI не обращается к API напрямую.
4. Features не создают локальные копии Button/Card/Header.
5. Циклические зависимости запрещены.
6. Незапланированные модули получают README/интерфейс, а не фальшивую реализацию.

Добавь архитектурный тест или lint boundaries, если это возможно без тяжёлой зависимости.

Commit: refactor: establish implementation module boundaries
```

## 006 — Runtime-тема и semantic tokens

```text
Цель: реализовать runtime-слой дизайн-токенов после промта 001, без создания продуктовых экранов.

Прочитай DESIGN_TOKENS.yaml и существующую тему.

Сделай:
1. Создай типизированное представление semantic tokens для light, dark и system.
2. Light использует утверждённую классическую сине-белую палитру.
3. Компоненты получают только semantic roles, а не raw palette keys.
4. Поддержи системное переключение и пользовательское override-хранилище, но не делай отдельный экран настроек.
5. Добавь typography, spacing, radius, elevation/border и motion tokens.
6. Добавь development-only проверку неизвестного токена.
7. Не разрешай произвольные цвета через component props; допускай только семантические варианты.

Тесты:
- light/dark/system resolution;
- сохранение override;
- fallback при неизвестном режиме;
- контраст ключевых пар токенов;
- поиск hard-coded hex/rgb в src, кроме файла палитры и тестовых fixtures.

Commit: feat: implement semantic theme runtime
```

## 007 — Библиотека базовых UI-компонентов

```text
Цель: реализовать только общий UI-каталог, необходимый следующим промтам.

Прочитай DESIGN_SYSTEM.md и component_catalog из DESIGN_TOKENS.yaml.

Реализуй минимально законченные компоненты:
AppScreen, ScreenHeader, AppTabBar, Button, IconButton, AppIcon, SurfaceCard, Section, FilterChip, StatusBadge, TextField, SearchField, InfoRow, Avatar, EmptyState, ErrorState, Skeleton и BottomSheet shell.

Требования:
1. Не подключай внешний UI-kit ради внешнего вида.
2. Все интерактивные зоны минимум 48×48.
3. Loading не меняет размеры кнопки.
4. Цвет не является единственным носителем статуса.
5. FilterChip — одна горизонтальная строка без wrapping.
6. Компоненты поддерживают light/dark, 200% text scaling и accessibility labels.
7. BottomSheet пока может быть инфраструктурным shell без продуктового содержимого.
8. Добавь preview-каталог или изолированный development route, не доступный в production navigation.

Тесты: состояния компонентов, press, disabled/loading, accessibility role/name, snapshots только для стабильной структуры.

Commit: feat: add volleyplay core ui library
```

## 008 — Router shell, canonical layouts и deep-link основа

```text
Цель: построить навигационный каркас без реализации содержимого 54 экранов.

Прочитай SCREENS.yaml, ROUTES.yaml, NAVIGATION_RESOLVERS.yaml и APP_MAP.md.

Сделай:
1. Реализуй единственный root Expo Router shell.
2. Создай пять неизменяемых нижних вкладок: Профиль, Игры, Чаты, Кэмпы, Настройки.
3. Добавь stack/modal layout группы и route placeholders только для уже зарегистрированных маршрутов.
4. Placeholder обязан показывать screen_id, статус not_started/definition_pending и безопасный Back; он не считается готовым экраном.
5. Реализуй back_fallback resolver и обработку прямого deep link.
6. Не создавай вторую нижнюю навигацию внутри manage/club flows.
7. System overlays actor.switcher и player.picker должны иметь modal-контекст и returnTo.
8. Добавь route registry test, который сопоставляет реализованные route files с ROUTES.yaml и разрешённым placeholder manifest.

Проверки: tab persistence, Android back, iOS gesture, unknown route, signed-out redirect shell, direct links.

Commit: feat: add canonical expo router shell
```