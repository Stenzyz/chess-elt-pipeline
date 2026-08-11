{{ config(materialized='table', schema='dds') }}

SELECT DISTINCT
    eco,
    regexp_replace(eco, '(Defense|Opening|Gambit|Countergambit|Game|System|Attack).*$', '\1') AS opening_family
FROM {{ ref('stg_games') }}