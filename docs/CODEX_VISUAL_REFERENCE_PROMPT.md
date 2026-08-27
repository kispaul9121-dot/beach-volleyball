# Codex — визуальные референсы без конфликта с архитектурой

Этот промт используется перед любой задачей, где Codex реализует или полирует UI VolleyPlay по скриншотам.

## Готовый промт

```text
Работай как UI implementation agent для VolleyPlay.

Главное правило: скриншоты являются только визуальными референсами. Они НЕ являются источником бизнес-логики, маршрутов, ролей, прав, названий вкладок, форматов турниров, способов оплаты, состояний участия или структуры данных.

Перед работой прочитай:
1. AGENTS.md
2. docs/DECISIONS.md
3. docs/ROUTES.yaml
4. docs/SCREENS.yaml
5. docs/ACTIONS.yaml
6. docs/CAPABILITIES.yaml
7. docs/ROLES.yaml
8. docs/ENTITY_SECTIONS.yaml
9. docs/DESIGN_SYSTEM.md
10. docs/DESIGN_TOKENS.yaml
11. docs/UI_RULES.md
12. соответствующий docs/screens/**/*.md
13. docs/implementation-prompts/README.md
14. docs/IMPLEMENTATION_RUNTIME.yaml, если он уже создан.

Приоритет при конфликте:
Git-функциональность и продуктовые контракты > screen spec > design tokens > скриншоты.

Никогда не меняй функциональность проекта, чтобы сделать экран похожим на картинку.

### Основные визуальные референсы

1. `a_clean_mobile_app_ui_screenshot_white_light_back.png`
   Главный референс для light-first интерфейса.
   Брать за пример:
   - белый фон;
   - спокойную плотность информации;
   - крупный читаемый title;
   - тонкие нейтральные границы;
   - аккуратные списки;
   - поиск и фильтры;
   - горизонтальные avatar/list элементы;
   - ощущение нативного iOS-интерфейса;
   - generous whitespace без пустоты.

   НЕ копировать:
   - зелёный как основной accent;
   - названия нижних вкладок;
   - структуру навигации;
   - конкретные кнопки и пользовательские действия.

   В VolleyPlay основной accent берётся только из semantic token action.primary и должен быть синим согласно DESIGN_TOKENS.yaml.

2. `a_clean_mobile_app_ui_screenshot_light_theme_of.png`
   Второй главный референс для списков и разделов с большим количеством игроков/объектов.
   Брать за пример:
   - карточку списка с avatar + title + secondary metadata;
   - визуальный ритм 12/16/24;
   - tab/segment hierarchy;
   - count badges;
   - search/filter row;
   - компактные secondary actions;
   - нижнюю панель как визуальный ориентир по размеру touch areas.

   НЕ копировать зелёную палитру и старые названия вкладок.

3. `детали_игры_на_пляжном_волейболе.png`
   Референс для game.details и других detail-screen.
   Брать за пример:
   - порядок hero → название → ключевые факты → организатор → описание → правила → участники → sections → CTA;
   - сильную визуальную иерархию;
   - компактные info chips;
   - sticky CTA;
   - preview участников;
   - крупное отображение цены и свободных мест.

   НЕ копировать:
   - тёмную тему;
   - зелёный neon accent;
   - текст, правила, количество вкладок и действия;
   - логику «Присоединиться»;
   - старую структуру sections.

   Реальная логика вступления, оплаты, чата и управления берётся только из JOIN_FLOW.yaml, ENTITY_SECTIONS.yaml и game specs.

4. `1000043438.jpg`
   Референс только для визуализации турнирной сетки.
   Брать за пример:
   - горизонтальное перемещение между раундами;
   - колонки этапов;
   - компактные match cards;
   - понятные линии progression;
   - визуальную фиксацию текущего раунда.

   НЕ копировать команды, стадии, турнирный формат или Google UI.

   В VolleyPlay разрешены только утверждённые форматы из COMPETITION_FORMATS.yaml. Нельзя возвращать round robin, Swiss, groups+playoff, отдельный King of Beach или double elimination без нового решения.

5. `1000043439.jpg`
   Референс только для плотности match-details и переключения внутренних section/tab.
   Брать за пример:
   - счёт как главный визуальный объект;
   - secondary metadata ниже;
   - компактную tab row;
   - clear separation между summary и деталями.

   Не использовать этот скриншот как источник функциональности, названий вкладок или цветовой темы.

### Дополнительные, низкоприоритетные референсы

6. `профиль_тренера_по_пляжному_волейболу.png`
   Использовать только для:
   - группировки профильных блоков;
   - hero profile header;
   - карточек расписания;
   - section spacing;
   - плотности review cards.

   Игнорировать тёмно-жёлтую тему, нижнюю навигацию и любые функции, которых нет в Git-контрактах.

7. `мобильный_интерфейс_для_пляжных_игр.png`
   Использовать только для:
   - размера catalog cards;
   - плотности metadata;
   - расположения status badge;
   - общей читаемости management list.

   Этот скриншот содержит устаревшие продуктовые решения. Не переносить:
   - постоянную кнопку/пункт «Архив»;
   - старый FAB «Создать»;
   - турнир «Король пляжа» как отдельный формат;
   - старую цветовую схему;
   - старые названия нижней навигации.

### Каноническая нижняя навигация

Всегда:
`Профиль · Игры · Чаты · Кэмпы · Настройки`

Нельзя заменять её навигацией со скриншота даже ради визуального совпадения.

### Цветовая система

Используй только semantic tokens.
Никаких локальных hex/RGB в screen-файлах.

Visual direction:
- primary surface: white/light;
- primary action: blue;
- primary text: dark navy;
- borders: neutral blue-gray;
- success: green;
- warning: amber;
- danger: red;
- info: cyan/blue.

Скриншоты с зелёным, жёлтым или тёмным главным accent используются только как layout reference.

### Правило адаптации

Не копируй скриншот pixel-for-pixel.
Для каждого экрана сначала составь короткую mapping table:

- current screen_id;
- closest screenshot reference;
- какие visual patterns берём;
- какие элементы скриншота запрещено переносить из-за Git-contract;
- какие semantic tokens/components используются.

После этого меняй только presentation layer, если текущий prompt не разрешает менять domain/navigation/data.

### Защита Git-функциональности

Перед UI-изменением проверь git diff и существующие tests.

Запрещено ради дизайна:
- менять route;
- менять action_id;
- переименовывать screen_id;
- менять permissions/capabilities;
- менять join/payment logic;
- менять owner-only result entry;
- создавать новый чат;
- создавать второй detail screen;
- добавлять новый tournament format;
- менять data model;
- удалять partial/placeholder/definition_pending функцию;
- заменять рабочий feature mock-экраном;
- делать массовый refactor соседних модулей.

Если скриншот требует функциональность, которой нет в Git-контракте:
1. не реализуй её;
2. сохрани существующее поведение;
3. используй только визуально совместимый контейнер;
4. отметь расхождение в отчёте как reference-only difference.

### Незавершённые экраны

Если область имеет status `partial`, `placeholder` или `definition_pending`:
- не дорисовывай неизвестную бизнес-логику;
- можно улучшать header, spacing, typography, cards, skeleton/empty state и безопасную оболочку;
- будущие action areas оставляй disabled/placeholder только если это соответствует текущему контракту;
- не выдавай placeholder за implemented.

### iOS-плагин

Для UI-задач используй фактический iOS-плагин из docs/IMPLEMENTATION_RUNTIME.yaml.
Проверяй:
- safe area;
- 320/360/390/430 pt;
- Dynamic Type 200%;
- keyboard;
- back gesture;
- VoiceOver;
- Reduce Motion;
- light appearance;
- при наличии — dark/system compatibility.

Не заявляй о пройденной iOS-проверке без фактического результата plugin/tool.

### Финальная проверка

Перед commit:
- сравни визуальный результат с выбранным screenshot reference;
- отдельно сравни поведение с Git-contract;
- запусти architecture/navigation/design validators;
- запусти связанные tests;
- убедись, что diff не содержит функциональных изменений вне scope.

В отчёте выведи:
1. screen_id;
2. использованные screenshot filenames;
3. что именно было взято из каждого референса;
4. какие детали намеренно НЕ были скопированы из-за Git-contract;
5. изменённые файлы;
6. test/validator results;
7. результат iOS-проверки;
8. оставшиеся visual TODO.

Commit должен описывать UI-изменение, а не заявлять о новой функции, если функциональность не менялась.
```

## Ключевой принцип

Скриншоты задают **визуальный язык**, Git задаёт **поведение продукта**.

Если изображение и Git расходятся, побеждает Git.
