# Звезда (dds-слой)

## Зерно таблицы фактов

- `fct_games` - одна строка = одна партия

## Схема

```mermaid
erDiagram
    FCT_GAMES }o--|| DIM_PLAYER : "white_username"
    FCT_GAMES }o--|| DIM_PLAYER : "black_username"
    FCT_GAMES }o--|| DIM_OPENING : "eco"
    FCT_GAMES }o--|| DIM_TIME_CONTROL : "time_class"
    FCT_GAMES }o--|| DIM_DATE : "end_time::date"

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
        date end_date
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

**Рейтинг - снапшотом, без отдельного fct-слоя.** Рассматривал `fct_player_rating_daily` как вторую таблицу фактов с другим зерном (игрок + дата + класс контроля), но staging-модель (`stg_player_stats`) уже даёт это зерно напрямую, без тяжёлых вычислений поверх raw. Отдельная dds-модель была бы буквальной копией staging без архитектурной пользы (не нужна инкрементальность, не требуется стабилизировать интерфейс от сложной трансформации) - решил не плодить прослойку ради методологии и оставить `stg_player_stats` как источник для будущих витрин напрямую.

**`dim_time_control` по `time_class`.** Ключ - класс контроля (rapid/blitz/bullet), а не конкретная комбинация секунд, потому что витрины оперируют классами. `base_time`/`increment_time` остаются как атрибуты измерения.

**`fct_games` инкрементальна.** В отличие от рейтингов, партии - тяжёлая трансформация (jsonb-разворачивание по 1.9+ млн строк), полный пересчёт при каждом запуске был бы дорогим. `materialized='incremental'`, `unique_key='uuid'`, фильтр по `end_time` новее максимума в уже существующей таблице.