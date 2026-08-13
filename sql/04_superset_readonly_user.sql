DO
$$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = :'ro_user') THEN
        CREATE USER :ro_user WITH PASSWORD :'ro_password';
        GRANT USAGE ON SCHEMA marts TO :ro_user;
        GRANT SELECT ON ALL TABLES IN SCHEMA marts TO :ro_user;
    END IF;
END
$$;

ALTER DEFAULT PRIVILEGES FOR ROLE :pg_admin IN SCHEMA marts
    GRANT SELECT ON TABLES TO :ro_user;