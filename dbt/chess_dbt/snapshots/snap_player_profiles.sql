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


select username from stage.stg_player_profiles spp 
where username not in (select DISTINCT(username) from (select black_username as username from stage.stg_games 
where black_username in (select username from stage.stg_player_profiles spp)
union
select white_username as username from stage.stg_games 
where white_username in (select username from stage.stg_player_profiles spp)) t1)
