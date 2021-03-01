#!/bin/bash
# Installation v0.2 for CentOS

echo "===== DPDB and Dependencies Installer ====="
sudo yum update

# Install Postgres
echo "===== Install and setup PostgreSQL ====="
wget https://download.postgresql.org/pub/repos/yum/9.6/redhat/rhel-7-x86_64/pgdg-centos96-9.6-3.noarch.rpm --no-check-certificate
sudo yum install pgdg-centos96-9.6-3.noarch.rpm epel-release
sudo yum update
sudo yum install postgresql96-server postgresql96-contrib
sudo /usr/pgsql-9.6/bin/postgresql96-setup initdb
sudo systemctl start postgresql-9.6
sudo systemctl enable postgresql-9.6
sudo -u postgres psql -c "ALTER USER postgres PASSWORD 'XXX';"			# ?
sudo -u postgres psql -c "CREATE USER logicsem WITH PASSWORD 'XXX';"
sudo -u postgres psql -c "CREATE DATABASE logicsem;"

# Assume git, gcc, cmake, and doxygen?

# Install gcc
sudo yum -y install gcc
gcc --version

# Install cmake
cd ../
wget https://github.com/Kitware/CMake/releases/download/v3.20.0-rc2/cmake-3.20.0-rc2.tar.gz --no-check-certificate
tar -zxvf cmake-3.20.0-rc2.tar.gz
cd cmake-3.20.0-rc2
./bootstrap && make && sudo make install
cmake --version
cd ../dp_on_dbs

# Install doxygen
sudo yum -y install doxygen

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