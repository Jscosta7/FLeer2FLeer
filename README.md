# FLeer2FLeer: Uma Ferramenta Web Baseada em Arquitetura Par-a-Par para Orquestração do Aprendizado Federado

**Resumo do Artigo:**

_Este trabalho apresenta o FLeer2FLeer (F2F), uma ferramenta web para orquestração de aprendizado federado baseada em uma arquitetura P2P. O F2F introduz um Indexador responsável pela descoberta, anúncio e ingresso de clientes nas múltiplas federações, sem interferir no processo de treinamento. Implementado sobre o framework Flower, o sistema utiliza estratégias baseadas em hooks para coleta não intrusiva de métricas. A ferramenta oferece monitoramento em tempo real de múltiplos treinamentos, expansão da rede pela adição de servidores e reporte de falhas. Os resultados experimentais demonstram que o Indexador impõe sobrecarga mínima à rede, enquanto a carga de treinamento é distribuída entre diferentes servidores promovendo maior escalabilidade._

---
O objetivo deste artefato é disponibilizar a ferramenta **FLeer2FLeer**, permitindo tanto visualizar o uso da ferramenta e suas principais funcionalidades, quanto reproduzir o experimento de tráfego de rede relatado no artigo.

Para garantir uma melhor organização e entendimento da ferramenta, o projeto foi dividido em tres pastas:
1. **Demo Visual (`/demo_visual`)**: Responsável por possibilitar a visualização da interface da ferramenta e suas funcionalidades.
2. **Reprodução de Experimentos (`/reproducao_experimento`)**: Responsável por reproduzir fielmente o experimento citado, extraindo as métricas de tráfego (.pcap) de múltiplos cenários e analisando com o script pyhton.
3. **A Ferramenta (`/src`)** : Onde estão localizados todos os arquivos que fazem parte do F2F.
---

## Estrutura do README.md

Este README.md está organizado nas seguintes seções:

* **Selos Considerados:** Apresenta os selos de qualidade de artefatos científicos reivindicados para este trabalho.
* **Informações Básicas e Requisitos:** Define as especificações de hardware (mínimas e sugeridas) e de sistema operacional necessárias para rodar o projeto.
* **Dependências:** Lista as ferramentas de software exigidas (como Docker e tcpdump) e fornece os comandos rápidos de instalação.
* **Preocupações com Segurança:** Esclarece a necessidade e o impacto do uso de privilégios de administrador (`sudo`) durante a captura do tráfego de rede.
* **Visualização da Ferramenta (Demo Visual):** Fornece um passo a passo rápido para inicializar a aplicação, rodar uma demonstração e validar se a infraestrutura está funcional.
* **Reprodução do Experimento do Artigo:** Detalha o processo para recriar os cenários do artigo.
* **Análise dos Resultados:** Apresenta o passo a passo e a validação das reivindicações originais do artigo.
* **LICENSE:** Apresenta a licença de código aberto do projeto.

---

## Selos Considerados
Os autores reivindicam os seguintes selos científicos para este artefato:
* Artefatos Disponíveis (SeloD);
* Artefatos Funcionais (SeloF);
* Artefatos Sustentáveis (SeloS);
* Experimentos Reprodutíveis (SeloR);

---

## Informações Básicas e Requisitos

Os experimentos foram testados em dois ambientes, com as seguintes especificações:

Requisitos de Software:
Para garantir a fidelidade da reprodução, o ambiente deve possuir:
* **Docker Engine:** Versão mínima 24.0.0
* **Docker Compose Plugin:** Versão mínima 2.20.0
Além disso para garantir a execução plena do artefato, atente-se aos requisitos de Sistema Operacional:
* **Para a Ferramenta (Demo Visual):** Qualquer sistema operacional (Linux, macOS, Windows).
* **Para os Experimentos (SeloR):** É obrigatório o uso de **Linux nativo** (recomendado Ubuntu 20.04/22.04 ou Debian 12).

> Em macOS/Windows, o Docker virtualiza a rede e não expõe as interfaces `br-*` ao hospedeiro, tornando o `tcpdump` inoperante. Nesses casos, utilize uma VM Linux ou WSL2.


Ambiente 1 (mínimo):
* **Sistema Operacional:** Ubuntu 20.04/22.04, Debian 12 .
* **Hardware Mínimo:** 2 CPUs (2.0GHz) e 8GB de memória RAM.
  
Ambiente 2 (sugerido):
* **Sistema Operacional:** Ubuntu 20.04/22.04, Debian 12 .
* **Hardware sugerido:** Intel i9-10900 CPUs, 32GB RAM, 20 threads.

> Como todos os códigos são executados em containeres Docker e a escala dos experimentos é pequena, espera-se que o usuário consiga reproduzir fielmente os experimentos em máquinas com baixa capacidade de processamento e com SO compatível com Docker, o que levou a estimativa do ambiente mínimo 

---

## Dependências

Abaixo listamos as dependências necessárias para a execução do projeto:

1. Git
2. **Docker e Docker Compose:** Essenciais para subir a infraestrutura e rodar os scripts analíticos finais.
3. **Tcpdump e Tshark:** Necessários apenas para a etapa de Reprodução de Experimentos (captura e análise de pacotes).

> Para maximizar a reprodutibilidade, as versões de todas as dependências críticas estão fixadas dentro dos contêineres (Dockerfile e docker-compose_c*.yml). Para as ferramentas de rede (docker, tcpdump), recomenda-se o uso das versões estáveis mais recentes, respeitando os requisitos mínimos declarados.


## Preocupações com segurança

A execução dos experimentos e contêineres **não apresenta riscos de segurança conhecidos**. O uso do sudo é exigido pelo utilitário tcpdump para permitir a "escuta" das interfaces de ponte de rede (br-) geradas dinamicamente pelo Docker durante os testes. Os comandos Docker são executados por padrão com sudo, mas é possível que o usuário possua uma instalação do Docker configurada para execução de comandos sem sudo, sem apresentar riscos para a segurança

## Instalação

Para configurar o ambiente de visualização da ferramenta e dos experimentos, siga os passos abaixo:

1. Preparação do Ambiente (ferramentas de rede): 

```bash
sudo apt update
sudo apt install docker-ce docker-compose-plugin tcpdump -y
```

2. Clonagem do repositório:

```bash
git clone <URL_DO_SEU_REPOSITORIO>
cd FLeer2FLeer
```

## Teste Mínimo 

Para verificar rapidamente se a infraestrutura do projeto e o banco de dados estão funcionais em sua máquina, execute um ciclo de vida mínimo do F2F.

1. Acesse o diretório onde estão contidos os arquivos Docker responsáveis pela demonstração:

```bash
cd demo_visual
```
2. Inicialize a infraestrutura base:

```bash
sudo docker compose up -d
```
Aguarde o download dos pacotes e módulos, quando o comando terminar de rodar no terminal, acesse http://localhost:4000. Você deverá ver o Dashboard da ferramenta carregado com os dados simulados.

> **Nota para Execução Remota:** Caso esteja avaliando este artefato em um servidor remoto (nuvem) ou via SSH, você precisará redirecionar a porta para acessar a interface na sua máquina local. Ao conectar no servidor, utilize o parâmetro de port-forwarding: 
> `ssh -L 4000:localhost:4000 usuario@ip_do_servidor`

3. Inicie um treinamento federado:

```bash
sudo docker compose -f docker-compose-treino.yml up -d --build
```

Acompanhe pelo terminal se os clientes se conectam ao servidor. Uma vez que o treinamento for concluído (ou caso não deseje aguardar o processo completo), proceda com a limpeza do ambiente.

4. Desligue a aplicação e limpe o ambiente

```bash
sudo docker compose -f docker-compose-treino.yml down
sudo docker compose down -v
cd ..
```


## Visualização da Ferramenta (Demo Visual)

Para acompanhar com mais detalhes o comportamento do F2F, suas funcionalidades e um treinamento de Aprendizado Federado, siga os passos abaixo:

1. Acesse o diretório onde estão contidos os arquivos Docker responsáveis pela demonstração:

```bash
cd demo_visual
```
2. Inicialize o Banco de Dados e o Indexador

```bash
sudo docker compose up -d
```
Aguarde o download dos pacotes e módulos e, quando o comando terminar de rodar no terminal, acesse http://localhost:4000. Você verá o Dashboard centralizado com dados de treinamentos anteriores, uma barra de navegação onde pode realizar buscas nas áreas de `Category` e `Application` e um menu lateral com outros dois módulos (`Be a Server` e `Reports`) do F2F.

3. Inicie um treinamento federado:

```bash
sudo docker compose -f docker-compose-treino.yml up -d --build
```

* Volte ao navegador e veja o campo `Server Status` do servidor iniciado ficar com o indicador `online` após aguardar um tempo de inicialização, da ordem de alguns minutos. Observe que isso acontece quando os contêineres se iniciam no terminal.
![alt text](imagens/1-status.png)
* Clique no campo `See Training` para acompanhar o treinamento e aguarde os clientes baixarem os datasets. 
![alt text](imagens/2-seetraining.png)
* Espere os clientes se conectarem, observando o valor na caixa `Connected Clients` aumentar até 2.
![alt text](imagens/3-connected.png)
* Observe a caixa `Round Progress` indicando que treinamento completa os dois rounds estipulados pelo servidor, passando por todos os estágios do Aprendizado Federado com o Flower (caixa `Round Status` indica o estágio).
![alt text](imagens/4-progress.png)
* Clicando em `Dashboard` no menu lateral, volte para visualizar os campos `Round Duration` (duração média da rodada, em segundos) e `Last  Update` (momento em que treinamento finalizou, com tempo desde a última atualização do servidor).
![alt text](imagens/5-novas-infos.png)

4. É possível rodar o treinamento novamente e acompanhar a nova execução repetindo o passo a passo descrito(os dados das execuções anteriores são mantidos e atualizados).

```bash
sudo docker compose -f docker-compose-treino.yml down
sudo docker compose -f docker-compose-treino.yml up -d --build
```

5. Após terminar a visualização da demo, faça uma limpeza para não causar conflito com a etapa de experimentos, limpando a infraestrutura destruindo os volumes:

```bash
sudo docker compose -f docker-compose-treino.yml down
sudo docker compose down -v
cd ..
```

> A aba do navegador em http://localhost:4000 pode ser fechada, pois ela não será mais necessária no resto do passo a passo.

## Reprodução do Experimento do artigo
Esta etapa possibilita recriar os 5 cenários descritos no artigo. O script inicia os cenários, captura o tráfego gerado pelas portas do Flower (8080) e do Indexador (3000), gera os arquivos `.pcap` e destrói o ambiente para o próximo ciclo. Para facilitar a compreensão de cada etapa do experimento, abaixo está uma descrição dos cenários:

| Cenário | Qtd. Servidores | Qtd. Clientes 
| :--- | :---: | :---: | :--- |
| **Cenário 1 (c1)** | 1 | 2 | 
| **Cenário 2 (c2)** | 2 | 4 | 
| **Cenário 3 (c3)** | 3 | 6 | 
| **Cenário 4 (c4)** | 4 | 8 | 
| **Cenário 5 (c5)** | 5 | 10 | 

É importante ressaltar que todos os cenários contribuem para a sustentação da Reivindicação #2. Já em relação à Reivindicação #1, os cenários com maior quantidade de servidores demandam mais do Indexador, devido ao constante aumento na carga de orquestração que ele deve realizar.

### Passo a Passo Geral da Execução

Antes de validar as reivindicações, é necessário gerar os dados brutos executando os experimentos:

1. Acesse o diretório de experimentos:

```bash
cd reproducao_experimento
```

2. Dê permissão de execução ao script:
   
```bash
chmod +x rodar_experimentos.sh
```

3. Execute os experimentos:

O script possibilita ajustar o número de cenários (1 até 5) e o número de rodadas (1 até 5). Abaixo está o tempo médio da bateria completa e cada rodada, por cenário:

Para garantir a reprodutibilidade exata dos experimentos e permitir comparações justas de métricas futuras, as seeds de aleatoriedade (TensorFlow, NumPy e Random) foram fixadas. A seed escolhida como padrão é a 42, poré é possível passar uma nova seed diretamente como argumento na execução do script.

>Caso deseje rodar a bateria completa do artigo, basta executar sudo ./rodar_experimentos.sh sem parâmetros.

```bash
sudo ./rodar_experimentos.sh rounds=2 cenarios=2 seed=42
```

Este processo leva tempo, pois treina modelos de Machine Learning reais em contêineres e aguarda o tempo de sincronização da rede. O comando exige privilégios de administrador (sudo) para habilitar o tcpdump e controlar o Docker.

Exemplo dos logs no início do comando:
![alt text](imagens/6-logs-inicio.png)

---
## Análise dos Resultados

Após o script exibir a mensagem de sucesso, os arquivos `.pcap` estarão na mesma pasta (`reproducao_experimento`). Para gerar os resultados, utilize os scripts em Python fornecidos:

> Garanta que você está dentro da pasta `reproducao_experimento` no terminal antes de executar esses próximos comandos

### Reivindicação #1: O Indexador impõe sobrecarga mínima à rede

Para comprovar que a introdução do Indexador não gera tráfego excessivo que comprometa o desempenho da federação, executaremos o script de análise completa.

Para ver a média de tráfego por cenário (FL x Indexador):
```bash
cd analise_completa
sudo docker compose up -d
```
O script gera um `.txt`, Volte para o diretório anterior e exiba a análise no seu terminal:

```bash
cat ../analise_completa.txt
```

**Recursos e Tempo Esperado:**

* **Recursos:** Baixo consumo de CPU/RAM (apenas processamento de arquivos texto).
* **Tempo esperado:** Menos de 1 minuto para a execução do script Python.

**Exemplo de resultado esperado:**

O terminal apresentará uma tabela de médias. É possível observar que a coluna MÉDIA INDEXADOR (MB) (ex: ~0.03 MB) apresenta valores em ordens de grandeza imensamente inferiores à coluna MÉDIA FL (MB) (ex: ~158 MB), comprovando a sobrecarga mínima.

```bash
Iniciando extração e análise dos 25 arquivos .pcap...

============================================================
 CENÁRIO 1
============================================================
Rodada 1: FL = 154.3585 MB | Indexador = 0.030462 MB
Rodada 2: FL = 162.4127 MB | Indexador = 0.033282 MB

 MÉDIA DO CENÁRIO 1 -> FL: 158.3856 MB | Indexador: 0.031872 MB

============================================================
 CENÁRIO 2
============================================================
Rodada 1: FL = 312.7265 MB | Indexador = 0.099224 MB
Rodada 2: FL = 321.5669 MB | Indexador = 0.108914 MB

 MÉDIA DO CENÁRIO 2 -> FL: 317.1467 MB | Indexador: 0.104069 MB

============================================================
 CENÁRIO 3
============================================================

 CENÁRIO 3 não gerou médias (Nenhuma rodada válida encontrada).

============================================================
 CENÁRIO 4
============================================================

 CENÁRIO 4 não gerou médias (Nenhuma rodada válida encontrada).

============================================================
 CENÁRIO 5
============================================================

 CENÁRIO 5 não gerou médias (Nenhuma rodada válida encontrada).


=================================================================
CENÁRIO    | MÉDIA FL (MB)      | MÉDIA INDEXADOR (MB)
-----------------------------------------------------------------
Cenário 1  | 158.3856           | 0.031872            
Cenário 2  | 317.1467           | 0.104069            
=================================================================
```

Limpeza 1: 

```bash
sudo docker compose down
cd ..
```

### Reivindicação #2: A carga de treinamento é constante entre os servidores

Para validar que o sistema escala distribuindo a carga do Aprendizado Federado entre diferentes servidores, analisaremos o tráfego isolado por IP.

Para ver o tráfego isolado por IP de cada servidor:

```bash
cd analise_por_servidor
sudo docker compose up -d
```

Exiba a análise por IP no seu terminal:

```bash
cat ../analise_por_servidor.txt
```

**Recursos e Tempo Esperado:**

* **Recursos:** Baixo consumo de CPU/RAM.
* **Tempo esperado:** Menos de 1 minuto para a execução do script.


**Exemplo de resultado esperado:**

A saída demonstrará o tráfego dividido por IP em cenários com múltiplos servidores. No Cenário 2, por exemplo, o avaliador verá que o total da rodada (~312 MB) não está concentrado em uma única máquina, mas distribuído entre as instâncias (ex: 172.19.0.4 recebendo ~152 MB e 172.19.0.5 recebendo ~160 MB), confirmando a distribuição de carga reivindicada.

```bash
Iniciando extração e análise detalhada por IP dos 25 arquivos .pcap...


============================================================
 ANÁLISE DO CENÁRIO 1
============================================================

--- Rodada 1 ---
Servidor (IP 172.19.0.4): 154.3585 MB
TOTAL DA RODADA: 154.3585 MB

--- Rodada 2 ---
Servidor (IP 172.19.0.4): 162.4127 MB
TOTAL DA RODADA: 162.4127 MB

============================================================
 ANÁLISE DO CENÁRIO 2
============================================================

--- Rodada 1 ---
Servidor (IP 172.19.0.4): 152.3998 MB
Servidor (IP 172.19.0.5): 160.3267 MB
TOTAL DA RODADA: 312.7265 MB

--- Rodada 2 ---
Servidor (IP 172.19.0.4): 157.5510 MB
Servidor (IP 172.19.0.5): 164.0159 MB
TOTAL DA RODADA: 321.5669 MB

============================================================
 ANÁLISE DO CENÁRIO 3
============================================================

============================================================
 ANÁLISE DO CENÁRIO 4
============================================================

============================================================
 ANÁLISE DO CENÁRIO 5
============================================================
```

Limpeza 2: 

```bash
sudo docker compose down
cd ..
```

Limpeza final:

```bash
sudo rm *.pcap
sudo rm *.txt
```

## LICENSE

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para mais detalhes.
