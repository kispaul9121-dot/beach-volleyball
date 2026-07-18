# VolleyPlay / Beach Volleyball

Архитектура мобильного приложения для поиска, участия и организации пляжного волейбола.

## С чего начинать

1. [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — главная модель продукта.
2. [`docs/ARCHITECTURE_AUDIT.md`](docs/ARCHITECTURE_AUDIT.md) — что было неполным и что исправлено.
3. [`docs/APP_MAP.md`](docs/APP_MAP.md) — полное текстовое дерево экранов и переходов.
4. [`docs/diagrams/app-map.mmd`](docs/diagrams/app-map.mmd) — Mermaid-карта.
5. [`docs/SCREENS.yaml`](docs/SCREENS.yaml) — реестр экранов.
6. [`docs/ACTIONS.yaml`](docs/ACTIONS.yaml) — кнопки и действия.
7. [`docs/ROUTES.yaml`](docs/ROUTES.yaml) — маршруты и возврат назад.
8. [`docs/DESIGN_SYSTEM.md`](docs/DESIGN_SYSTEM.md) — единые размеры, компоненты, тёмная тема, иконки, чипы и анимации.
9. [`docs/DESIGN_TOKENS.yaml`](docs/DESIGN_TOKENS.yaml) — машиночитаемый UI-контракт.
10. `docs/screens/` — подробные спецификации экранов.

## Профили одного аккаунта

Один аккаунт может иметь:

- игрока;
- тренера;
- организацию / клуб.

Аватар в верхней панели переключает активный профиль. Интерфейс адаптируется, а создаваемая сущность хранит, от чьего имени она опубликована.

Подробности:

- [`docs/ACTORS.yaml`](docs/ACTORS.yaml)
- [`docs/CAPABILITIES.yaml`](docs/CAPABILITIES.yaml)
- [`docs/ROLES.yaml`](docs/ROLES.yaml)
- [`docs/AUTH_AND_ONBOARDING.md`](docs/AUTH_AND_ONBOARDING.md)

## UI и мобильный клиент

Архитектура интерфейса рассчитана на единый React Native / Expo клиент для iOS и Android.

- тёмная тема обязательна и проектируется первой;
- конкретная цветовая палитра ещё не утверждена;
- нижнее меню неизменно: `Главная · События · Чаты · Клубы · Профиль`;
- чипы при переполнении прокручиваются горизонтально в одну строку;
- основная библиотека иконок — `lucide-react-native`;
- motion строится на Reanimated и Gesture Handler с поддержкой Reduce Motion;
- минимальная зона нажатия — 48×48 на обеих платформах.

## Соревнования

- [`docs/COMPETITION_FORMATS.yaml`](docs/COMPETITION_FORMATS.yaml) — плей-офф, круговой, группы, швейцарский, полное распределение, сезонная таблица.
- [`docs/GAME_FORMATS.yaml`](docs/GAME_FORMATS.yaml) — 2×2, 4×4, ротация пяти игроков.
- [`docs/ENTITY_LIFECYCLES.yaml`](docs/ENTITY_LIFECYCLES.yaml) — статусы сущностей, участий, платежей и раундов.

## Как найти конкретный экран

Пример: `Профиль → Мои турниры и сезоны`.

```text
SCREENS.yaml
→ найти profile.competitions
→ открыть поле spec
→ docs/screens/profile/my-competitions.md
→ действия в ACTIONS.yaml
→ адрес в ROUTES.yaml
→ размеры и компоненты в DESIGN_TOKENS.yaml
```

## Как работать с Codex

Корневой [`AGENTS.md`](AGENTS.md) содержит обязательные правила. При передаче задачи указывай `screen_id`, например:

```text
Прочитай AGENTS.md и реализуй screen_id tournament.manage.
Не создавай новые маршруты. Используй SCREENS.yaml, ACTIONS.yaml,
ROUTES.yaml, DESIGN_SYSTEM.md, DESIGN_TOKENS.yaml
и docs/screens/shared/tournament-manage.md.
```

## Статус

Ветка `architecture/v2-multi-profile` расширяет документацию до архитектуры MVP:

- вход и онбординг;
- несколько профилей;
- адаптивные кабинеты;
- быстрый доступ организатора;
- внутренние экраны игр, тренировок, турниров, сезонов и туров;
- соревнования и расчёт результатов;
- календарь, статистика, платежи, настройки, чаты и уведомления;
- единая дизайн-система для iOS и Android.

Это архитектурный контракт. Рабочее приложение, база, платежи и алгоритмы должны быть реализованы и протестированы отдельно.
