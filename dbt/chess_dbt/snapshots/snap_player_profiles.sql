{% snapshot snap_player_profiles %}

{{
    config(
        target_schema='dds',
        unique_key='username',
        strategy='check',
        check_cols=['title', 'location', 'status'],
    )
}}

SELECT * FROM {{ ref('stg_player_profiles') }}

{% endsnapshot %}