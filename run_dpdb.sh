#!/usr/bin/env bash
basepath=$(dirname $(realpath $0))

cd $(dirname $0)

conda activate dpdb_env

$basepath/initdb.sh > /dev/stderr
echo "===================="
echo "SETUP DONE"

python $basepath/dpdb.py -f $1 $2 --input-format $3

sleep 1
psql dpdb_pg -c 'select pg_kill_all_sessions('"'"'janedoe'"'"','"'"'janedoe'"'"');'
sleep 1
killall -9 postgres
