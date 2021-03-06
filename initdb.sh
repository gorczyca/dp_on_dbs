#!/usr/bin/env bash
pgpath=/dev/shm/

killall -9 postgres
sleep 1

psql dpdb_pg -c 'select pg_kill_all_sessions('"'"'janedoe'"'"','"'"'janedoe'"'"');'
sleep 1

pg_ctl -D $pgpath/postgres-data stop
rm -r $pgpath/postgres-data/*
mkdir -p $pgpath/postgres-data
initdb -D $pgpath/postgres-data --no-locale

pg_ctl -D $pgpath/postgres-data start -o "--fsync=off --wal_level=minimal --synchronous_commit=off --archive_mode=off --max_wal_senders=0 --track_counts=off --autovacuum=off"

psql postgres -c "create user janedoe with password 'janedoe';"
echo "user Ok"
createdb dpdb_pg
psql dpdb_pg <<'EOF'
create or replace function pg_kill_all_sessions(db varchar, application varchar)
returns integer as
$$
begin
return (select count(*) from (select pg_catalog.pg_terminate_backend(pid) from pg_catalog.pg_stat_activity where pid <> pg_backend_pid() and datname = db and application_name = application) k);
end;
$$
language plpgsql security definer volatile set search_path = pg_catalog;
grant execute on function pg_kill_all_sessions(varchar,varchar) to janedoe;
EOF

rm -rf /tmp/tmp*
#killall -9 python
killall -9 d4
