#!/usr/bin/env bash
# Installation v0.6

RED='\033[1;31m'
GREEN='\033[1;32m'
CYAN='\033[1;36m'
NC='\033[0m' # No Color

echo
echo -e $GREEN"DPDB: Installation started."$NC
echo

echo
echo -e $GREEN"DPDB: Installing conda."$NC
echo
cd ../
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh --no-check-certificate
chmod +x Miniconda3-latest-Linux-x86_64.sh
./Miniconda3-latest-Linux-x86_64.sh
. ~/miniconda3/etc/profile.d/conda.sh

echo
echo -e $GREEN"DPDB: Creating conda environment."$NC
echo
cd dp_on_dbs
if conda info --envs | grep dpdb_env; then
  echo
  echo -e $CYAN"DPDB: dpdb_env environment already created."$NC
  echo -e $CYAN"DPDB: skipping creating conda environment."$NC
  echo
else
  echo
  echo -e $GREEN"DPDB: creating conda environment: dpdb_env."$NC
  echo
  conda env create -f environment.yml
  echo
  echo -e $GREEN"DPDB: conda environment created."$NC
  echo
fi

echo
echo -e $GREEN"DPDB: Making files executable."$NC
echo
chmod +x ./solver.sh
chmod +x ./run_dpdb.sh
chmod +x ./initdb.sh
# chmod +x ./d4_bash.sh
chmod +x ./binaries/*

echo
echo -e $GREEN"DPDB: Installation finished."$NC
echo
