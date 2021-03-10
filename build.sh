#!/bin/bash
# Installation v0.4

echo "===== DPDB and Dependencies Installer ====="

# Install Anaconda
echo "===== Install and Setup Anaconda ====="
cd ../
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh --no-check-certificate
chmod +x Miniconda3-latest-Linux-x86_64.sh
./Miniconda3-latest-Linux-x86_64.sh
. $CONDA_PREFIX/etc/profile.d/conda.sh

echo "===== Create Anaconda Environment for DPDB ====="
cd dp_on_dbs
conda env create -f environment.yml
conda activate nesthdb

# Install Postgres
echo "===== Install and setup PostgreSQL ====="
conda install -y -c anaconda postgresql
initdb -D mylocal_db
pg_ctl -D mylocal_db -l logfile start
createuser -s postgres
psql postgres -c "ALTER USER postgres PASSWORD 'XXX';"			# ?
psql postgres -c "CREATE USER logicsem WITH PASSWORD 'XXX';"
psql postgres -c "CREATE DATABASE logicsem;"

# Assume git, gcc, cmake, and doxygen?

# Install gcc, g++, make, cmake, doxygen
echo "===== Install GCC ====="
conda install -y -c anaconda gcc_linux-64
echo "===== Install G++ ====="
conda install -y -c anaconda gxx_linux-64
echo "===== Install Make ====="
conda install -y -c anaconda make
echo "===== Install CMake ====="
conda install -y -c anaconda cmake
echo "===== Install Doxygen ====="
conda install -y -c conda-forge doxygen

# Install htd
echo "===== Install htd ====="
conda install -y -c anaconda git
git clone -b normalize_cli --single-branch https://github.com/TU-Wien-DBAI/htd.git ../htd
cd ../htd
cmake -DCMAKE_INSTALL_PREFIX=$CONDA_PREFIX .
make && make install
cd ../dp_on_dbs
