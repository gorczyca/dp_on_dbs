#!/usr/bin/env bash
# Installation v0.6

echo "===== DPDB and Dependencies Installer ====="

# Install Anaconda
echo "===== Install and Setup Anaconda ====="
cd ../
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh --no-check-certificate
chmod +x Miniconda3-latest-Linux-x86_64.sh
./Miniconda3-latest-Linux-x86_64.sh
. ~/miniconda3/etc/profile.d/conda.sh

echo "===== Create Anaconda Environment for DPDB ====="
cd dp_on_dbs
conda env create -f environment.yml
# conda activate dpdb_env

echo "===== Make binaries and scripts executable ====="
chmod +x ./solver.sh
chmod +x ./run_dpdb.sh
chmod +x ./initdb.sh
chmod +x ./d4_bash.sh
chmod +x ./binaries/*

# echo "To use dpdb:"
# echo "Start conda environment: conda activate dpdb_env"
echo "===== Done ====="
