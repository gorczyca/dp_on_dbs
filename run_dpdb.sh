#!/usr/bin/env bash
basepath=$(dirname $(realpath $0))

cd $(dirname $0)

$basepath/initdb.sh > /dev/stderr
echo "===================="
echo "SETUP DONE"
python $basepath/dpdb.py -f $1 $2 --input-format apx
