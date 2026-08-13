SELECT format('CREATE USER %I WITH PASSWORD %L', :'ro_user', :'ro_password')
WHERE NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = :'ro_user')
\gexec

GRANT USAGE ON SCHEMA marts TO :ro_user;
GRANT SELECT ON ALL TABLES IN SCHEMA marts TO :ro_user;

ALTER DEFAULT PRIVILEGES FOR ROLE :pg_admin IN SCHEMA marts
    GRANT SELECT ON TABLES TO :ro_user;