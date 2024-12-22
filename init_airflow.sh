#!/bin/bash

# Initialisation de la base de données Airflow (si ce n'est pas encore fait)
airflow db init

# Ajout de la connexion PostgreSQL
airflow connections add 'books_connection' \
  --conn-type 'postgres' \
  --conn-host 'postgres_container' \
  --conn-login 'airflow' \
  --conn-password 'airflow' \
  --conn-port '5432' \
  --conn-schema 'postgres'

# Démarrage du scheduler ou du webserver
exec "$@"
