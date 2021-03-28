#!/usr/bin/env bash
basepath=$(dirname $(realpath $0))

$basepath/initdb.sh > /dev/stderr
python $basepath/dpdb.py -f $1 $2 --input-format tgf
