"""En la consola de postgres debes crear """
postgres=# CREATE USER proforest PASSWORD 'proforest2022*';
postgres=# CREATE DATABASE proforest OWNER proforest;
postgres=# \c proforest
Ahora está conectado a la base de datos «proforest» con el usuario «postgres».
proforest=# create extension postgis;
CREATE EXTENSION
proforest=#

""" Con ello ya deberiamos tener una base de datos con habilidades postgis para trabajo futuro """
""" recuerda dar permisos al nuevo usuario en el archivo pg_hba.conf"""

