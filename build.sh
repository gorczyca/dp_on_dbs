#!/bin/bash
# Installation v0.3 for CentOS

echo "===== DPDB and Dependencies Installer ====="
sudo yum update

# Install Postgres
echo "===== Install and setup PostgreSQL ====="
sudo yum -y install postgresql-server postgresql-contrib
sudo postgresql-setup initdb
sudo systemctl start postgresql
sudo systemctl enable postgresql
sudo -u postgres psql -c "ALTER USER postgres PASSWORD 'XXX';"			# ?
sudo -u postgres psql -c "CREATE USER logicsem WITH PASSWORD 'XXX';"
sudo -u postgres psql -c "CREATE DATABASE logicsem;"

# Assume git, gcc, cmake, and doxygen?

# Install gcc, g++, openssl
sudo yum -y install gcc
sudo yum -y install gcc-c++
sudo yum -y install openssl-devel

# Install cmake
cd ../
wget https://github.com/Kitware/CMake/releases/download/v3.19.6/cmake-3.19.6.tar.gz --no-check-certificate
tar -zxvf cmake-3.19.6.tar.gz
cd cmake-3.19.6
./bootstrap && make && sudo make install
cmake --version
cd ../dp_on_dbs

# Install doxygen
sudo yum -y install doxygen

# Install htd
echo "===== Install htd ====="
sudo yum -y install git
git clone -b normalize_cli --single-branch https://github.com/TU-Wien-DBAI/htd.git ../htd
cd ../htd
cmake ./ && make
make install
cd ../dp_on_dbs

# Install Anaconda
echo "===== Install and setup Anaconda ====="
cd ../
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh --no-check-certificate
chmod +x Miniconda3-latest-Linux-x86_64.sh
./Miniconda3-latest-Linux-x86_64.sh
source ~/.bashrc

echo "===== Create Anaconda Environment for DPDB ====="
cd dp_on_dbs
conda env create -f environment.yml
conda activate nesthdb
