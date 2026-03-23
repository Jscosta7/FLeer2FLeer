#!/bin/bash

# Loop para os 5 Cenários (c1 ao c5)
for c in {1..5}; do

    # Loop para as 5 Rodadas de medição
    for r in {1..5}; do
        echo "Iniciando Cenário $c - Rodada $r de 5..."


        docker compose -f docker-compose_c${c}.yml up -d

        # Espera o container subir
        until [ $(docker network ls | grep -c "reproducao_experimento_fl_network") -gt 0 ]; do
        echo "Aguardando rede ficar pronta..."
        sleep 1
        done


        # Pega o ID do mongo
        CONTAINER_ID=$(docker compose -f docker-compose_c${c}.yml ps -q mongodb)
        # Inspeciona o container para pegar o ID da rede
        NET_ID=$(docker inspect --format='{{range .NetworkSettings.Networks}}{{.NetworkID}}{{end}}' $CONTAINER_ID | cut -c 1-12)
        INTERFACE="br-$NET_ID"
        
        echo "$INTERFACE"



        sudo tcpdump -i $INTERFACE "port 8080 or port 3000" -U -w c${c}_exec${r}.pcap &
        TCPDUMP_PID=$!

        echo "Treinamento em andamento. Aguardando a finalização..."

   
        docker compose -f docker-compose_c${c}.yml logs -f server1 | grep -m 1 "FL finished"

        echo "Treinamento concluído! Aguardando pacotes residuais..."
        sleep 5

        # 4. Corta a gravação
        sudo kill -SIGINT $TCPDUMP_PID
        sleep 3

        # 5. Desliga e destrói (a interface br- morre aqui)
        docker compose -f docker-compose_c${c}.yml down
        
        echo "Limpeza concluída"
        sleep 5
    done
done

echo "TODOS OS 25 EXPERIMENTOS FINALIZADOS"
