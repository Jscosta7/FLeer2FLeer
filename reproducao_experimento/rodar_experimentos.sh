#!/bin/bash

# Valores padrão (caso o avaliador rode sem argumentos, mantém os 5 originais)
TOTAL_CENARIOS=5
TOTAL_ROUNDS=5

# Processa os argumentos passados via linha de comando
for arg in "$@"; do
    case $arg in
        rounds=*)
        TOTAL_ROUNDS="${arg#*=}"
        ;;
        cenario=*|cenarios=*)
        TOTAL_CENARIOS="${arg#*=}"
        ;;
        *)
        echo "Aviso: Argumento ignorado: $arg"
        ;;
    esac
done

echo "========================================"
echo "Iniciando bateria de experimentos..."
echo "Total de Cenários configurados: $TOTAL_CENARIOS"
echo "Rodadas (Rounds) por Cenário: $TOTAL_ROUNDS"
echo "Total de execuções: $((TOTAL_CENARIOS * TOTAL_ROUNDS))"
echo "========================================"
echo ""

# Loop para os Cenários (do 1 até o TOTAL definido)
for (( c=1; c<=TOTAL_CENARIOS; c++ )); do

    # Loop para as 5 Rodadas de medição
    for (( r=1; r<=TOTAL_ROUNDS; r++ )); do
        echo "Iniciando Cenário $c - Rodada $r de $TOTAL_ROUNDS..."


        sudo docker compose -f docker-compose_c${c}.yml up -d

        until [ $(docker network ls | grep -c "reproducao_experimento_fl_network") -gt 0 ]; do
        echo "Aguardando rede ficar pronta..."
        sleep 1
        done


        # Pega o ID do mongo
        CONTAINER_ID=$(sudo docker compose -f docker-compose_c${c}.yml ps -q mongodb)
        # Inspeciona o container para pegar o ID da rede
        NET_ID=$(sudo docker inspect --format='{{range .NetworkSettings.Networks}}{{.NetworkID}}{{end}}' $CONTAINER_ID | cut -c 1-12)
        INTERFACE="br-$NET_ID"
        
        echo "$INTERFACE"



        sudo tcpdump -i $INTERFACE "port 8080 or port 3000" -U -w c${c}_exec${r}.pcap &
        TCPDUMP_PID=$!

        echo "Treinamento em andamento. Aguardando a finalização..."

   
        sudo docker compose -f docker-compose_c${c}.yml logs -f server1 | grep -m 1 "FL finished"

        echo "Treinamento concluído! Aguardando pacotes residuais..."
        sleep 5

        # 4. Corta a gravação
        sudo kill -SIGINT $TCPDUMP_PID
        sleep 3

        # 5. Desliga e destrói (a interface br- morre aqui)
        sudo docker compose -f docker-compose_c${c}.yml down
        
        echo "Limpeza concluída"
        sleep 5
    done
done

echo "TODOS OS $((TOTAL_CENARIOS * TOTAL_ROUNDS)) EXPERIMENTOS FINALIZADOS"
