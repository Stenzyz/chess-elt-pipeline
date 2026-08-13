DO
$$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'superset_user') THEN
        CREATE USER superset_user WITH PASSWORD 'superset';
        GRANT USAGE ON SCHEMA marts TO superset_user;
        GRANT SELECT ON ALL TABLES IN SCHEMA marts TO superset_user;
    END IF;
END
$$;

ALTER DEFAULT PRIVILEGES FOR ROLE :pg_admin IN SCHEMA marts
        GRANT SELECT ON TABLES TO superset_user;