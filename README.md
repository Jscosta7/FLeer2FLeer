# FLeer2FLeer: Uma Ferramenta Web Baseada em Arquitetura Par-a-Par para Orquestração do Aprendizado Federado

O objetivo deste artefato é disponibilizar a ferramenta **FLeer2FLeer**, permitindo tanto visualizar o uso da ferramenta e suas principais funcionalidades, quanto reproduzir o experimento de tráfego de rede relatado no artigo.

Para garantir uma melhor organização e entendimento da ferramenta, o projeto foi dividido em tres pastas grandes módulos:
1. **Demo Visual (`/demo_visual`)**: Responsável por possibilitar a visualização da interface da ferramenta e suas funcionalidades.
2. **Reprodução de Experimentos (`/reproducao_experimentos`)**: Responsável por reproduzir fielmente o experimento citado, extraindo as métricas de tráfego (.pcap) de múltiplos cenários e analisando com o script pyhton.
3. **A Ferramenta (`/src`)** : Onde estão localizados todos os arquivos que fazem parte do F2F.
---

## Selos Considerados
Os autores reivindicam os seguintes selos científicos para este artefato:
* Artefatos Disponíveis (SeloD);
* Artefatos Funcionais (SeloF);
* Experimentos Reprodutíveis (SeloR);

---

## Informações Básicas e Requisitos
Os experimentos e a ferramenta foram rodados em máquinas diferentes, justamente pela diferença de requisitos de ambas execuções. 
Recomenda-se a execução sob as seguintes condições:
Para o Demo Visual:
* **Sistema Operacional:** Ubuntu 20.04/22.04, Debian 12 ou Windows (via WSL2 + Docker Desktop).
* **Hardware Mínimo:** 2 CPUs (2.0GHz) e 8GB de memória RAM.
Para o experimento de tráfego:
* Guapimirim...
---

## Dependências
A seguir, são apresentados os passos necessários para configurar as dependências:

1. Git
2. **Docker e Docker Compose (V2):** Essenciais para subir a infraestrutura.
3. **Tcpdump e Tshark:** Necessários apenas para a etapa de Reprodução de Experimentos (captura e análise de pacotes).
4. **Python 3.9+ e Pandas:** Necessários para rodar os scripts analíticos finais.

**Instalação rápida das ferramentas de rede (Linux/Ubuntu):**
```bash
sudo apt update
sudo apt install docker-ce docker-compose-plugin tcpdump tshark python3-pip -y
pip3 install pandas
```
## Visualização da Ferramenta (Demo Visual)
1. Acesse o diretório onde esta contido o arquivo docker responsável pela demonstração:

```bash
cd demo_visual
```
2. Inicialize o Banco de Dados e o Indexador

```bash
docker compose up -d
```
Aguarde o download dos pacotes e módulos e acesse http://localhost:4000. Você verá o Dashboard centralizado com dados de treinamentos anteriores, uma barra de navegação onde pode realizar buscas nas áreas de Categoria e Aplicação e um menu lateral com outros dois módulos(Be a Server e Reports) do F2F.

3. Inicie um treinamento federado:

```bash
docker compose -f docker-compose-treino.yml up -d --build
```

Volte ao navegador e veja o servidor iniciado "online", clique em "See Training" para acompanhar o treinamento e aguarde os clientes baixarem os datasets. Após os clientes se conectarem, o treinamento completará o número de rounds estipulados pelo servidor, passando por todos os estágios do Aprendizado Federado com o Flower até finalizar e atualizar os parâmetros de rounds completos e tempo médio de duração da rodada. Volte clicando em Dashboard no menu lateral para visualizar os novos dados.

4. Limpeza

Para não causar conflito com a etapa de experimentos limpe a infraestrutura destruindo os volumes:

```bash
docker compose -f docker-compose-treino.yml down
docker compose down -v
cd ..
```

## Reprodução do Experimento
Esta etapa recria os 5 cenários descritos no artigo. O script inicia os cenários, captura o tráfego gerado pelas portas do Flower (8080) e do Indexador (3000), gera os arquivos .pcap e destrói o ambiente para o próximo ciclo.

1. Acesse o diretório de experimentos:

```bash
cd reproducao_experimentos
```
2. Dê permissão e execute o script:
   
O script executará 5 rodadas para cada um dos 5 cenários (25 execuções no total). Ele pode solicitar a senha sudo para acionar o tcpdump.

```bash
chmod +x rodar_experimentos.sh
./rodar_experimentos.sh
```
Este processo leva tempo, pois treina modelos de Machine Learning reais em contêineres e aguarda o tempo de sincronização da rede.

3. Análise dos Resultados:

Após o script exibir a mensagem de sucesso, os 25 arquivos .pcap estarão na pasta. Para gerar resultados próximos aos do artigo, utilize os scripts em Python fornecidos:

Para ver a média de tráfego por cenário (FL x Indexador):
```bash
python3 analise_completa.py
```
Para ver o tráfego isolado por IP de cada servidor:
```bash
python3 analise_por_servidor.py
```
## Preocupações com segurança

A execução dos experimentos e contêineres não apresenta riscos de segurança conhecidos para os revisores. O uso do sudo é exigido estritamente pelo utilitário tcpdump para permitir a "escuta" das interfaces de ponte de rede (br-) geradas dinamicamente pelo Docker durante os testes.
