#!/usr/bin/env bash

# Actualizar paquetes y agregar repositorio de Microsoft
apt-get update
ACCEPT_EULA=Y apt-get install -y curl gnupg unixodbc-dev

curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
curl https://packages.microsoft.com/config/debian/11/prod.list > /etc/apt/sources.list.d/mssql-release.list

apt-get update
ACCEPT_EULA=Y apt-get install -y msodbcsql17

# Por si usas pyodbc
pip install pyodbc
