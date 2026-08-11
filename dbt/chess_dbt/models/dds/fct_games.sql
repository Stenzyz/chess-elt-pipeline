{{ config(materialized='incremental', unique_key='uuid') }}

SELECT
    *,
    end_time::date as end_date
FROM {{ ref('stg_games') }}

{% if is_incremental() %}
WHERE end_time > (SELECT MAX(end_time) FROM {{ this }})
{% endif %}