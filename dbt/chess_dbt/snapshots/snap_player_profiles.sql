{% snapshot snap_player_profiles %}

{{
    config(
        target_schema='dds',
        unique_key='username',
        strategy='check',
        check_cols=['title', 'country', 'status'],
    )
}}

SELECT * FROM {{ ref('stg_player_profiles') }}

{% endsnapshot %}