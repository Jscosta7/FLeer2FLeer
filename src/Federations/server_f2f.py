import flwr as fl
from flwr.server import Server
from flwr.server.client_manager import SimpleClientManager
from datetime import datetime
import threading
import time
import socketio
import argparse

# ------------------------------
# 1. Configuração de Argumentos 
# ------------------------------
parser = argparse.ArgumentParser(description='Flower Server F2F')
parser.add_argument('--port', type=int, default=8080, help='Porta do Servidor FL')
parser.add_argument('--id', type=str, required=True, help='ID único do Mongo/Indexador')
parser.add_argument('--indexador_host', type=str, default="localhost", help='Host do Indexador (localhost ou nome do container)')
parser.add_argument('--min_clients', type=int, default=2, help='Mínimo de clientes simultâneos')
parser.add_argument('--rounds', type=int, default=2, help='Número de Rounds')

args = parser.parse_args()

# Aplica as configurações passadas no terminal
PORTA_FL = args.port
ID_SERVIDOR = args.id
HOST_INDEXADOR = f"http://{args.indexador_host}:3000"
MIN_CLIENTS = args.min_clients
NUM_ROUNDS = args.rounds

print(f"CONFIG: Porta={PORTA_FL} | ID={ID_SERVIDOR} | Indexador={HOST_INDEXADOR} | Clients={MIN_CLIENTS}")

# ------------------------------
# 2. Conexão Socket.io 
# ------------------------------
sio = socketio.Client()

connected = False
while not connected:
    try:
        sio.connect(HOST_INDEXADOR)
        connected = True
        print(f"Conectado ao Indexador em {HOST_INDEXADOR}")
    except Exception as e:
        print(f"Aguardando Indexador subir em {HOST_INDEXADOR}... Tentando de novo em 2s.")
        time.sleep(2)

# ------------------------------
# 3. Estados e Variáveis Auxiliares
# ------------------------------
auxiliar = {
    "round_started": False,
    "start_time": None,
    "end_time": None,
    "round_end": True,
}

Training_state = {
    "id" : ID_SERVIDOR,             
    "Server_status": "offline",
    "Training_status": "waiting_for_clients",
    "current_round": 0,
    "Total_rounds": 0,
    "Round_duration": 0,
    "Completed_rounds": 0,
    "last_update": datetime.now(),
    "connected_clients": 0,
    "Total_clients" : 0,
    "Min_clients" : 0,
    "Fraction_fit": 0,
}

# ------------------------------
# 4. Funções de Comunicação 
# ------------------------------
def emit_Training_state():
    """Emite o estado bruto via socket.io para o Webserver"""
    if sio.connected:
        data = Training_state.copy()
        # Converte datetime para ISO string para evitar erro no JSON
        if isinstance(data["last_update"], datetime):
            data["last_update"] = data["last_update"].isoformat()
        sio.emit("training_update", data)

last_clients = {"value": -1} # Começa com -1 para forçar o primeiro envio

def emit_clients():
    """Emite o numero de clientes quando o valor é alterado"""
    if Training_state["connected_clients"] != last_clients["value"]:
        if sio.connected:
            sio.emit("clients_update", {
                "id": Training_state["id"],
                "clients": Training_state["connected_clients"],
                "Training_status": Training_state["Training_status"]
            })
            last_clients["value"] = Training_state["connected_clients"]
            print(f"Clientes conectados: {Training_state['connected_clients']} (Status: {Training_state['Training_status']})")

def monitor_clients(client_manager, Min_clients=MIN_CLIENTS, interval=1):
    """Monitoramento em tempo real da sala de espera do servidor FL"""
    while True:
        try:
            n = client_manager.num_available()
            Training_state["connected_clients"] = n
            
            if n < Min_clients:
                if Training_state["Training_status"] != "finished":
                    Training_state["Training_status"] = "waiting_for_clients"
            else:
                if Training_state["Training_status"] == "waiting_for_clients":
                    Training_state["Training_status"] = "training" 
            
            emit_clients()
            time.sleep(interval)
        except Exception as e:
            print(f"Erro no monitor: {e}")
            time.sleep(1)

# ------------------------------
# 5. Hooks do Flower
# ------------------------------
def on_fit_config_fn(rnd):
    Training_state["current_round"] = rnd
    if Training_state["Training_status"] != "waiting_for_clients":
        auxiliar["round_started"] = True
        Training_state["Training_status"] = "training"
    
    auxiliar["start_time"] = datetime.now()
    Training_state["Round_duration"] = 0
    Training_state["last_update"] = datetime.now()
    
    emit_Training_state()
    print(f"Estado de Treinamento enviado no fit (Iniciando Round {rnd})")
    return {}

def on_evaluate_config_fn(rnd):
    Training_state["current_round"] = rnd
    auxiliar["end_time"] = datetime.now()
    
    if auxiliar["start_time"]:
        Training_state["Round_duration"] = (auxiliar["end_time"] - auxiliar["start_time"]).total_seconds()
        
        
        Training_state["Completed_rounds"] += 1
    
    auxiliar["round_started"] = False
    Training_state["Training_status"] = "evaluating"
    Training_state["last_update"] = datetime.now()

    emit_Training_state()
    print(f"Estado de treinamento enviado no evaluate (Finalizando Round {rnd})")
    
    Training_state["Round_duration"] = 0
    return {}

# ------------------------------
# 6. Estratégia e Servidor (Com blindagem contra queda de clientes)
# ------------------------------
strategy = fl.server.strategy.FedAvg(
    min_available_clients=MIN_CLIENTS,
    min_fit_clients=MIN_CLIENTS,       # Força esperar os clientes para evitar o erro de dados picotados
    min_evaluate_clients=MIN_CLIENTS,  # Força esperar na avaliação também
    fraction_fit=1.0,
    fraction_evaluate=1.0,
    on_fit_config_fn=on_fit_config_fn,
    on_evaluate_config_fn=on_evaluate_config_fn
)

client_manager = SimpleClientManager()
server = Server(client_manager=client_manager, strategy=strategy)

monitor_thread = threading.Thread(
    target=monitor_clients,
    args=(client_manager, MIN_CLIENTS),
    daemon=True
)
monitor_thread.start()

# ------------------------------
# 7. Iniciar Servidor FL
# ------------------------------
if __name__ == "__main__":
    try:
        Training_state["Server_status"] = "online"
        Training_state["Total_rounds"] = NUM_ROUNDS
        Training_state["Min_clients"] = MIN_CLIENTS
        Training_state["Fraction_fit"] = 1.0
        
        emit_Training_state()
        print("Estado de treinamento enviado antes do server iniciar")
        
        fl.server.start_server(
            server_address=f"0.0.0.0:{PORTA_FL}",
            config=fl.server.ServerConfig(num_rounds=NUM_ROUNDS),
            server=server
        )
        
    except KeyboardInterrupt:
        print("\nInterrompido manualmente pelo usuário.")
    except Exception as e:
        print(f"\nErro fatal durante a execução: {e}")
    finally:
        # Garante que o status final seja enviado mesmo se der erro
        Training_state["Training_status"] = "finished"
        Training_state["last_update"] = datetime.now()
        Training_state["Server_status"] = "offline"
        
        emit_Training_state()
        print("Estado de treinamento enviado após treinamento finalizar (Offline)")

        time.sleep(2)
        
        if sio.connected:
            sio.disconnect()