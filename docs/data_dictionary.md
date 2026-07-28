# Data dictionary - games endpoint

Источник: `/pub/player/{username}/games/{year}/{month}`

Ответ - объект с ключом `games`, внутри список партий. Ниже расписаны поля одной партии (одного элемента этого списка). "game field" значит прямое поле объекта партии, в отличие от того, что зашито внутри текста pgn.

| Поле           | Тип  | Откуда     | Может быть пустым | Пример                                      |
|----------------|------|------------|-------------------|---------------------------------------------|
| uuid           | str  | game field | нет | 4ff16746-7575-11f1-92b4-76ef4301000f                      |
| url            | str  | game field | нет | https://www.chess.com/game/live/170985319350              |
| rated          | bool | game field | нет | false                                                     |
| time_class     | str  | game field | нет | rapid                                                     |
| time_control   | str  | game field | нет | 600 (формат base+increment, разобрать на этапе 5)         |
| rules          | str  | game field | нет | chess (варианты: bughouse/crazyhouse/chess960, не грузим) |
| end_time       | int  | game field | нет | 1782928783 (unix, секунды)                                |
| white.username | str  | game field | нет | tiazn12                                                   |
| white.rating   | int  | game field | нет | 1028                                                      |
| white.result   | str  | game field | нет | checkmated (см. список значений ниже)                     |
| black.username | str  | game field | нет | Rozum_Ivan                                                |
| black.rating   | int  | game field | нет | 2432                                                      |
| black.result   | str  | game field | нет | win                                                       |
| eco            | str  | game field | да  | https://www.chess.com/openings/Ruy-Lopez-Opening...       |
| accuracies     | float| game field | да  | 83.83 / 96.98                                             |

## Пустые значение
eco - У  партии может не быть дебюта (хотя  в партиях ГМ неизвестно, встречается ли такая ситуация)
accuracies - есть партии без подсчитанной точности

## Значения result (по докам Chess.com API)

Способ завершения партии: checkmated, resigned, timeout, abandoned, agreed, repetition, stalemate, insufficient, 50move, timevsinsufficient, kingofthehill, threecheck

Исход относительно стороны (не причина): win, lose

Специфика вариантов (не обычные шахматы): bughousepartnerlose

## Что не используем

- pgn - полный текст партии не разбираем, кроме дебюта (берём его из eco-ссылки, не из PGN)
- fen / CurrentPosition - финальная позиция доски, не нужна для целей проекта
- tcn - закодированные ходы, не нужны
- initial_setup - всегда стандартная начальная позиция для обычных шахмат, не несёт информации

## Особенность источника

Партия между двумя GM присутствует в архивах обоих игроков с одинаковым uuid, дедуп по этому полю на stage-слое.