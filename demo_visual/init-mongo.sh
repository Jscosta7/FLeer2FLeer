#!/bin/bash

echo "Iniciando a importação do Databse"

# O Mongo importa os dados do JSON direto para o banco
mongoimport --db WebserverDB --collection servers --type json --file /docker-entrypoint-initdb.d/seed_servidores.json --jsonArray

echo "Importação concluída"