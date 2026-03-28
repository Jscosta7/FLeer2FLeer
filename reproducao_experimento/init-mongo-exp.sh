#!/bin/bash

echo "Iniciando a importação do Database de Experimentos"


mongoimport --db WebserverDB --collection servers --type json --file /docker-entrypoint-initdb.d/seed_experimentos.json --jsonArray

echo "Importação concluída"