# Блок 4 — создание и публичная страница игры

## 025 — Game domain shell и repository boundary

```text
Цель: подготовить game feature без визуальной реализации всех экранов.

Прочитай GAME_MVP.yaml, GAME_FORMATS.yaml, GAME_MATCH_TABLE.yaml, GAME_TUNISIAN_LADDER.yaml, JOIN_FLOW.yaml и ENTITY_SECTIONS.yaml.

Сделай:
1. Типы Game, GameFormatConfig, GameParticipant, GameMatch, GameResult и GamePermissions.
2. Repository/use-case interfaces для details, create draft, manage, join и matches.
3. Route loaders для game.details/create/manage с cancellation и stale-response protection.
4. Чётко раздели public read model и manage commands.
5. Результаты представлены immutable events/read model; участник не получает write command.
6. Не реализуй UI или генераторы матчей в этом промте.
7. Не создавай сезонные поля и tournament bracket внутри Game.

Тесты: schema validation, lifecycle transitions, owner vs delegated manager command surface.

Commit: feat: add game domain feature boundary
```

## 026 — Создание игры: шаг 1 «Что и когда»

```text
Реализуй только первый шаг game.create.

Поля: Создать как, название/описание по контракту, дата, start/end в одном временном окне. Используй active actor и capability resolver.

Требования:
- ровно четыре шага мастера в общем progress;
- draft создаётся/восстанавливается;
- end после start, timezone явно учитывается;
- нет recurrence, сезона или нескольких игровых дней;
- смена actor с заполненными данными требует подтверждения и пересчёта прав;
- route returnTo сохраняется;
- offline не подтверждает server draft как сохранённый.

Не реализуй место, формат, участие или цену. Создай stable draft contract для следующих шагов.

Тесты: date validation, daylight-saving boundary, actor change, resume draft, duplicate submit.

Commit: feat: implement game creation basics step
```

## 027 — Создание игры: шаг 2 «Место и формат»

```text
Реализуй только второй шаг game.create.

Форматы: fixed pairs 2x2, 4x4/fixed teams и Тунисская лестница. Используй GAME_FORMATS и GAME_TUNISIAN_LADDER.

Сделай:
1. Venue/court selection через существующий route/selector; при незавершённом бронировании сохрани только venue reference, не симулируй booking.
2. Для Тунисской лестницы court count 1/2/3 автоматически задаёт 5/10/15 игроков.
3. Отдельные поля: матчей на площадку default 15 и циклов default 1.
4. Все циклы обязаны помещаться в одно временное окно; показывай estimate, но не выдумывай duration матча без настройки.
5. Для fixed formats capacity следует контракту; не превращай разовую игру в турнир.
6. Переход назад сохраняет draft.

Тесты: format switching resets only incompatible fields, 1→5/2→10/3→15, invalid court count.

Commit: feat: implement game format and venue step
```

## 028 — Создание игры: шаг 3 «Участие и цена»

```text
Реализуй третий шаг game.create по JOIN_FLOW.yaml.

Две независимые настройки:
- enrollment: Сразу записываются / Отправляют заявку / Только по приглашению;
- payment: Бесплатно / Оплата онлайн / Оплата организатору вне приложения.

Сделай waitlist toggle, capacity summary и server capability validation для online payments. Visibility всей сущности задаётся отдельно по существующему контракту и не смешивается со способом набора.

Правила:
- invitation_only скрывает public join action, но не обязательно делает сущность непубличной;
- online payment требует payout readiness; при отсутствии показать block и путь настройки, не fake success;
- external payment не создаёт platform payment;
- не добавляй ручное изменение online payment status организатором.

Тесты: все 9 комбинаций policies, full capacity/waitlist, payout unavailable и draft persistence.

Commit: feat: implement game enrollment and price step
```

## 029 — Создание игры: шаг 4 «Проверка и публикация»

```text
Реализуй финальный шаг game.create.

Сделай review sections по трём предыдущим шагам, edit links с возвратом, validation summary и Publish action.

Перед публикацией authoritative server check проверяет actor capability, время, venue reference, format capacity, enrollment/payment config и payout readiness. Двойное нажатие идемпотентно.

После успеха:
- published game получает canonical gameId;
- создаётся/привязывается один event conversation согласно контракту;
- draft помечается completed;
- route ведёт на game.manage или game.details согласно product action, сохраняя корректный back context.

При частичной server ошибке не показывай published. Не формируй матчи автоматически, если контракт требует отдельного действия владельца.

Тесты: stale review, price changed, idempotency, server rejection, successful redirect.

Commit: feat: complete game publishing wizard
```

## 030 — Страница игры: guest variant

```text
Реализуй game.details для guest/stranger, сохраняя единый canonical экран.

Используй гибридную light-first композицию: компактная hero/visual зона, ключевая информация, вкладки Обзор · Участники · Матчи · Чат и sticky primary action, когда применимо.

Guest видит разрешённые публичные данные: формат, организатор, дата/время, место, заполненность, цена, правила и ограниченный preview участников. Guest не видит payment statuses, сообщения чата, закрытые результаты или manage controls.

Главное действие одно: `Вступить`; resolver определяет дальнейший flow. Для invitation-only без активного приглашения action скрыт и показывается текстовый статус.

Не додумывай полный визуал definition_pending блоков; создай совместимые slots.

Тесты: public/private, no places, registration closed, invitation only, deep link и no sensitive fields.

Commit: feat: implement public game details
```

## 031 — Invitation details и переход к игре

```text
Реализуй invitation.details для game/training/tournament/tour через общий invitation feature, но в этом промте полноценно протестируй game invitation.

Сделай:
1. Контекст события, пригласивший actor, срок и условия.
2. Действия Принять приглашение и Отказаться только здесь.
3. Acceptance не означает оплату: free→confirmed, online→payment_required, external→confirmed_external_payment_unverified.
4. Нерешённое приглашение не появляется в Profile activity и не даёт chat access.
5. Повторное открытие resolved invitation показывает итог и link к canonical entity.
6. Expired/revoked/stale capacity обрабатываются authoritative response.
7. Decline требует подтверждения только если контракт это допускает; не добавляй лишний friction.

Тесты: accept idempotency, expired, revoked, online payment state и activity/chat boundary.

Commit: feat: implement invitation resolution flow
```

## 032 — Страница игры: participant и organizer viewing variants

```text
Расширь game.details, не создавая отдельные экраны.

Participant:
- статус `Вы участвуете`;
- полный разрешённый список участников;
- собственная payment cell с Оплатить/Повторить/статусом;
- матчи и статистика read-only;
- canonical event chat;
- для Тунисской лестницы: моя площадка, текущий цикл, подтверждённые переходы.

Organizer на публичном details:
- badge `Вы организатор`;
- действие `Управлять` на /games/:gameId/manage;
- данные остаются в view mode, editable поля не появляются.

Delegated manager также не получает поля счёта на public page. Оплата за другого запрещена.

Тесты: role switching, owner vs manager, own payment only, chat membership, permission revoked while open.

Commit: feat: add participant and organizer game details variants
```