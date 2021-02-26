#!/bin/bash
# Installation for Debian / Ubuntu v0.1

echo "===== DPDB and Dependencies Installer ====="
sudo apt-get update

# Install Postgres
echo "===== Install and setup PostgreSQL ====="
aptitude -y install postgresql postgresql-contrib postgresql-common postgresql-client libpq-dev
sudo -u postgres psql -c "ALTER USER postgres PASSWORD 'XXX';"			# ?
sudo -u postgres psql -c "CREATE USER logicsem WITH PASSWORD 'XXX';"
sudo -u postgres psql -c "CREATE DATABASE logicsem;"

# Assume git, gcc, and cmake?

# Install gcc
sudo apt install build-essential
apt-get install manpages-dev
gcc --version

# Install cmake
cd ../
wget https://github.com/Kitware/CMake/releases/download/v3.20.0-rc2/cmake-3.20.0-rc2.tar.gz --no-check-certificate
tar -zxvf cmake-3.20.0-rc2.tar.gz
cd cmake-3.20.0-rc2
./bootstrap && make && sudo make install
cmake --version
cd ../dp_on_dbs

# Install htd
echo "===== Install htd ====="
git clone -b normalize_cli https://github.com/TU-Wien-DBAI/htd.git ../htd
cd ../htd
cmake ./ && sudo make install
cd ../dp_on_dbs

# Install Anaconda
echo "===== Install and setup Anaconda ====="
cd ../
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh --no-check-certificate
chmod +x Miniconda3-latest-Linux-x86_64.sh
./Miniconda3-latest-Linux-x86_64.sh
cd ../dp_on_dbs

echo "===== Create Anaconda Environment for DPDB ====="
conda env create -f environment.yml
conda activate nesthdb