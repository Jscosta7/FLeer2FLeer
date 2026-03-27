import os
import subprocess
import pandas as pd
import sys

# --- CONFIGURAÇÃO ---

PORTA_FL = "8080"       
PORTA_INDEXADOR = "3000" 

def verificar_dependencias():
    #Verifica se o tshark está instalado.
    try:
        subprocess.run(["tshark", "-v"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    except (FileNotFoundError, subprocess.CalledProcessError):
        print(" Erro: O 'tshark' (Wireshark CLI) não está instalado ou não está no PATH.")
        print("Instale com: sudo apt install tshark")
        sys.exit(1)

def analisar_experimentos_detalhado():
    nome_arquivo = "analise_por_servidor.txt"

    print(" Iniciando a analise detalhada de IPs do Fleer2Fleer...\n")

    # Abre o arquivo de texto para escrita
    with open(nome_arquivo, "w", encoding="utf-8") as f_out:
        f_out.write("Iniciando extração e análise detalhada por IP dos 25 arquivos .pcap...\n\n")

        for c in range(1, 6): # Cenários 1 a 5
            print(f" Processando Cenario {c}/5...")
            
            f_out.write(f"\n{'='*60}\n ANÁLISE DO CENÁRIO {c}\n{'='*60}\n")
            
            for r in range(1, 6): # Rodadas 1 a 5
                pcap_file = f"c{c}_exec{r}.pcap"
                csv_file = f"temp_c{c}_exec{r}.csv"

                if not os.path.exists(pcap_file):
                    f_out.write(f"Arquivo {pcap_file} não encontrado. Pulando...\n")
                    continue

                #  Extraindo os IPs (ip.src e ip.dst) ---
                tshark_cmd = [
                    "tshark", "-r", pcap_file,
                    "-Y", f"ip", 
                    "-T", "fields",
                    "-E", "header=y",
                    "-E", "separator=,",
                    "-e", "ip.src",       
                    "-e", "ip.dst",       
                    "-e", "tcp.dstport",  
                    "-e", "tcp.srcport",  
                    "-e", "frame.len"     
                ]

                try:
                    with open(csv_file, "w") as f:
                        subprocess.run(tshark_cmd, stdout=f, stderr=subprocess.DEVNULL, check=True)

                    try:
                        df = pd.read_csv(csv_file)
                    except pd.errors.EmptyDataError:
                        f_out.write(f"Rodada {r}: O arquivo temporario CSV estava vazio.\n")
                        continue

                    if df.empty:
                        f_out.write(f"Rodada {r}: O dataframe carregado estava vazio.\n")
                        continue

                    # Limpeza de dados
                    df['frame.len'] = pd.to_numeric(df['frame.len'], errors='coerce').fillna(0)
                    df['tcp.dstport'] = pd.to_numeric(df['tcp.dstport'], errors='coerce').fillna(0)
                    df['tcp.srcport'] = pd.to_numeric(df['tcp.srcport'], errors='coerce').fillna(0)

                    #  Identificando os Servidores por IP 
                    # Vamos pegar todo tráfego onde a porta (origem ou destino) seja 8080
                    df_fl = df[ (df['tcp.srcport'] == int(PORTA_FL)) | (df['tcp.dstport'] == int(PORTA_FL)) ].copy()

                    if df_fl.empty:
                        f_out.write(f"Rodada {r}: Sem tráfego FL detectado.\n")
                        continue

                    # Cria uma coluna única 'IP_Servidor' para agrupar
                    df_fl['server_ip'] = df_fl.apply(
                        lambda row: row['ip.src'] if row['tcp.srcport'] == int(PORTA_FL) else row['ip.dst'], axis=1
                    )

                    # Agrupa por IP do servidor e soma os Bytes
                    trafego_por_ip = df_fl.groupby('server_ip')['frame.len'].sum() / (1024 * 1024) # Em MB

                    f_out.write(f"\n--- Rodada {r} ---\n")
                    
                    # Exibe o tráfego de cada servidor encontrado
                    contador_servidores = 1
                    for ip, mb in trafego_por_ip.items():
                        f_out.write(f"Servidor (IP {ip}): {mb:.4f} MB\n")
                        contador_servidores += 1
                    
                    total_round = trafego_por_ip.sum()
                    f_out.write(f"TOTAL DA RODADA: {total_round:.4f} MB\n")

                except Exception as e:
                    f_out.write(f" Erro na Rodada {r}: {e}\n")
                finally:
                    if os.path.exists(csv_file):
                        os.remove(csv_file)

    # Mensagem final no terminal 
    print(f"\n Analise concluida")
    print(f" Abra o arquivo '{nome_arquivo}' para visualizar os resultados detalhados por IP.")

if __name__ == "__main__":
    verificar_dependencias()
    analisar_experimentos_detalhado()