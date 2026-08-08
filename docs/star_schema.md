# Звезда (dds-слой)

## Зерно таблиц фактов

- `fct_games` - одна строка = одна партия
- `fct_player_rating_daily` - одна строка = игрок + дата снимка +класс контроля

Две таблицы фактов с разной гранулярностью.

## Схема

```mermaid
erDiagram
    FCT_GAMES }o--|| DIM_PLAYER : "white_username"
    FCT_GAMES }o--|| DIM_PLAYER : "black_username"
    FCT_GAMES }o--|| DIM_OPENING : "eco"
    FCT_GAMES }o--|| DIM_TIME_CONTROL : "time_class"
    FCT_GAMES }o--|| DIM_DATE : "end_time::date"
    FCT_PLAYER_RATING_DAILY }o--|| DIM_PLAYER : "username"
    FCT_PLAYER_RATING_DAILY }o--|| DIM_DATE : "snapshot_date"
    FCT_PLAYER_RATING_DAILY }o--|| DIM_TIME_CONTROL : "time_class"

    FCT_GAMES {
        varchar uuid PK
        text game_url
        varchar white_username FK
        varchar black_username FK
        int white_rating
        int black_rating
        varchar white_result
        varchar black_result
        varchar outcome
        varchar termination
        real white_accuracies
        real black_accuracies
        text eco FK
        varchar time_class FK
        timestamptz end_time
    }

    DIM_TIME_CONTROL {
        varchar time_class PK
        int base_time
        real increment_time
        varchar label
    }

    DIM_PLAYER {
        varchar username
        varchar title
        varchar country
        varchar status
        timestamptz dbt_valid_from
        timestamptz dbt_valid_to
    }

    DIM_OPENING {
        text eco PK
        text opening_family
    }

    FCT_PLAYER_RATING_DAILY {
        varchar username FK
        date snapshot_date
        varchar time_class FK
        int rating
        int win
        int loss
        int draw
        timestamptz last_game_date
    }

    DIM_DATE {
        date date_day PK
        int year
        int month
        varchar month_name
        int day_of_week
        varchar day_name
        boolean is_weekend
        int quarter
    }
```

## Решения и компромиссы

**Денормализация.** `white_username`, `black_username`, `eco`, `time_class` хранятся в факте текстом, а не суррогатными ключами. Причина: объём умеренный (~1.9 млн партий), Postgres нормально справляется с JOIN, но большинство витрин обходятся без них вовсе, если нужные поля уже лежат в факте.

**`dim_player` через SCD2.** Титул, страна и статус меняются редко, поэтому историчность через `dbt_valid_from`/`dbt_valid_to`. Джойн с фактом идёт с учётом периода действия версии, а не просто по `username`.

**Рейтинг - снапшотом, не SCD2.** Рейтинг меняется после каждой партии, вести его через SCD2 породило бы миллионы версий. Поэтому отдельная таблица фактов с ежедневным срезом.

**`dim_time_control` по `time_class`.** Ключ — класс контроля (rapid/blitz/bullet), а не конкретная комбинация секунд, потому что витрины оперируют классами. `base_time`/`increment_time` остаются как атрибуты измерения.