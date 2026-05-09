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
        seed=*)
        export FL_SEED="${arg#*=}"
        ;;
        *)
        echo "Aviso: Argumento ignorado: $arg"
        ;;
    esac
done

echo "Verificando ambiente..."

# Verifica se a porta 27017 está livre
if ss -tlnp | grep -q ":27017" || lsof -i :27017 > /dev/null 2>&1; then
    echo "Erro: A porta 27017 (MongoDB) já está em uso."
    echo "Por favor, pare o serviço que está utilizando a porta antes de prosseguir."
    exit 1
fi

# Verifica se há redes ou containers órfãos do experimento
if docker network ls | grep -q "reproducao_experimento_fl_network"; then
    echo "Erro: Rede ou containers órfãos detectados de uma execução anterior."
    echo "Por favor, execute 'docker compose down -v' no diretório do cenário para limpar o ambiente antes de prosseguir."
    exit 1
fi

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


        docker compose -f docker-compose_c${c}.yml up -d

        # Verifica se o comando anterior (docker compose up) falhou
        if [ $? -ne 0 ]; then
            echo "Erro Crítico: Falha ao iniciar os contêineres na rodada $r do cenário $c."
            exit 1
        fi

        echo "Aguardando a criação da rede do Docker..."
        NET_ID=""

        # Loop com timeout (tenta 15 vezes, aguardando 2 segundos entre cada tentativa)
        for i in {1..15}; do
        # Tenta extrair o ID diretamente da rede
            NET_ID=$(docker network inspect -f '{{.Id}}' reproducao_experimento_fl_network 2>/dev/null | cut -c 1-12)
    
            # Se a variável não estiver vazia, sai do loop
            if [ -n "$NET_ID" ]; then
                break
            fi
    
            echo "Aguardando rede ficar pronta... tentativa $i/15"
            sleep 2
        done

        # Valida que o docker inspect retornou um ID
        if [ -z "$NET_ID" ]; then
            echo "Erro: Tempo limite atingido. Não foi possível obter o ID da rede 'reproducao_experimento_fl_network' via docker inspect."
            # Caso não retorne um ID, limpa o ambiente para não existir orfãos no próximo "docker compose up"
            docker compose -f docker-compose_c${c}.yml down 2>/dev/null
            exit 1
        fi

        INTERFACE="br-$NET_ID"
        echo "Interface validada e pronta para captura: $INTERFACE"


        tcpdump -i $INTERFACE "port 8080 or port 3000" -U -w c${c}_exec${r}.pcap &
        TCPDUMP_PID=$!

        echo "Treinamento em andamento. Aguardando a finalização..."

   
        docker compose -f docker-compose_c${c}.yml logs -f server1 | grep -m 1 "FL finished"

        echo "Treinamento concluído! Aguardando pacotes residuais..."
        sleep 5

        # 4. Corta a gravação
        kill -SIGINT $TCPDUMP_PID
        sleep 3

        # 5. Desliga e destrói (a interface br- morre aqui)
        docker compose -f docker-compose_c${c}.yml down

        echo "Limpeza concluída. Aguardando o Sistema Operacional liberar a porta 27017..."
        
        # Fica travado aqui até a porta ser totalmente liberada
        while ss -tlnp | grep -q ":27017" || lsof -i :27017 > /dev/null 2>&1; do
            sleep 2
        done
        
        echo "Porta liberada. Pronto para a próxima rodada."
    done
done

echo "TODOS OS $((TOTAL_CENARIOS * TOTAL_ROUNDS)) EXPERIMENTOS FINALIZADOS"
