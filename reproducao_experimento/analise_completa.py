import pandas as pd
import os
import subprocess
import shutil

# --- CONFIGURAÇÃO DAS PORTAS ---
PORTA_INDEXADOR = 3000
PORTA_FL = 8080

def verificar_dependencias():
    """Garante que o tshark está instalado antes de começar."""
    if not shutil.which("tshark"):
        print("'tshark' não encontrado no sistema.")
        print(" Rode o comando: sudo apt update && sudo apt install tshark -y")
        exit(1)

def analisar_experimentos():
    resultados_cenarios = {}
    print(" Iniciando extração e análise dos 25 arquivos .pcap...\n")

    for c in range(1, 6):
        print(f"{'='*60}\n CENÁRIO {c}\n{'='*60}")
        trafego_fl = []
        trafego_idx = []

        for r in range(1, 6):
            pcap_file = f"c{c}_exec{r}.pcap"
            csv_file = f"temp_c{c}_exec{r}.csv"

            if not os.path.exists(pcap_file):
                print(f"Arquivo {pcap_file} não encontrado. Pulando...")
                continue

            #Python pede pro tshark extrair apenas o tamanho dos pacotes
            tshark_cmd = [
                "tshark", "-r", pcap_file,
                "-Y", f"tcp.port=={PORTA_FL} || tcp.port=={PORTA_INDEXADOR}",
                "-T", "fields",
                "-E", "header=y",
                "-E", "separator=,",
                "-e", "tcp.srcport",
                "-e", "tcp.dstport",
                "-e", "frame.len"
            ]
            
            try:
                # Executa o tshark e salva num CSV temporário
                with open(csv_file, "w") as f:
                    subprocess.run(tshark_cmd, stdout=f, stderr=subprocess.DEVNULL, check=True)
                
                # Tenta ler os dados com Pandas
                try:
                    df = pd.read_csv(csv_file)
                except pd.errors.EmptyDataError:
                    print(f" Rodada {r}: O PCAP estava vazio (Sem tráfego de FL ou Indexador).")
                    continue
                
                # Se o arquivo tem cabeçalho, mas zero linhas de dados
                if df.empty:
                    print(f" Rodada {r}: Nenhum pacote capturado nas portas monitoradas.")
                    continue

                # Força a conversão para numérico (limpa qualquer lixo de string)
                df['tcp.srcport'] = pd.to_numeric(df['tcp.srcport'], errors='coerce')
                df['tcp.dstport'] = pd.to_numeric(df['tcp.dstport'], errors='coerce')
                df['frame.len'] = pd.to_numeric(df['frame.len'], errors='coerce')

                # Filtra e soma o tráfego do Indexador 
                idx_mask = (df['tcp.srcport'] == PORTA_INDEXADOR) | (df['tcp.dstport'] == PORTA_INDEXADOR)
                mb_idx = df[idx_mask]['frame.len'].sum() / (1024 * 1024)

                # Filtra e soma o tráfego do Treinamento FL (Modelos)
                fl_mask = (df['tcp.srcport'] == PORTA_FL) | (df['tcp.dstport'] == PORTA_FL)
                mb_fl = df[fl_mask]['frame.len'].sum() / (1024 * 1024)

                trafego_fl.append(mb_fl)
                trafego_idx.append(mb_idx)

                print(f"Rodada {r}: FL = {mb_fl:.4f} MB | Indexador = {mb_idx:.6f} MB")

            except subprocess.CalledProcessError:
                print(f" Erro ao executar o tshark na Rodada {r}. O arquivo .pcap pode estar corrompido.")
            except Exception as e:
                print(f" Erro inesperado na Rodada {r}: {e}")
            finally:
                # CSV temporário apagado
                if os.path.exists(csv_file):
                    os.remove(csv_file)

        # Calcula a média daquele cenário
        if trafego_fl:
            media_fl = sum(trafego_fl) / len(trafego_fl)
            media_idx = sum(trafego_idx) / len(trafego_idx)
            resultados_cenarios[c] = {'fl': media_fl, 'idx': media_idx}
            print(f"\n MÉDIA DO CENÁRIO {c} -> FL: {media_fl:.4f} MB | Indexador: {media_idx:.6f} MB\n")
        else:
            print(f"\n CENÁRIO {c} não gerou médias (Nenhuma rodada válida encontrada).\n")

    # Tabela Final
    if resultados_cenarios:
        print("\n")
        print("="*65)
        print(f"{'CENÁRIO':<10} | {'MÉDIA FL (MB)':<18} | {'MÉDIA INDEXADOR (MB)':<20}")
        print("-" * 65)
        for c, medias in resultados_cenarios.items():
            print(f"Cenário {c:<2} | {medias['fl']:<18.4f} | {medias['idx']:<20.6f}")
        print("="*65)
    else:
        print("\n Nenhuma tabela final gerada. Verifique os erros acima.")

if __name__ == "__main__":
    verificar_dependencias()
    analisar_experimentos()
