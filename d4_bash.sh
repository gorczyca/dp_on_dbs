#!/usr/bin/env bash

#call d4_bash.sh adm.dl instances/A-1-admbuster_1000.apx
#-> python script where the to... is
# d4 https://www.cril.univ-artois.fr/KC/d4.html
# lp... https://research.ics.aalto.fi/software/asp/download/binary-x86-64/asptools-2020-04-08.tgz
gringo --output=smodels $1 $2 | ./lp2normal-2.18 | ./lp2atomic-1.17 | ./lp2sat-1.24 | ./d4 -mc /dev/stdin