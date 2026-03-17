import tensorflow as tf
import flwr as fl
import argparse

# --- Carregamento do Modelo e Dados ---
model = tf.keras.applications.MobileNetV2((32, 32, 3), classes=10, weights=None)
model.compile("adam", "sparse_categorical_crossentropy", metrics=["accuracy"])
(x_train, y_train), (x_test, y_test) = tf.keras.datasets.cifar10.load_data()

# --- Definição do Cliente ---
class FlowerClient(fl.client.NumPyClient):
    def get_parameters(self, config):
        return model.get_weights()

    def fit(self, parameters, config):
        model.set_weights(parameters)
        model.fit(x_train, y_train, epochs=1, batch_size=32)
        return model.get_weights(), len(x_train), {}

    def evaluate(self, parameters, config):
        model.set_weights(parameters)
        loss, accuracy = model.evaluate(x_test, y_test)
        return loss, len(x_test), {"accuracy": accuracy}

# --- Execução Principal com Argparse ---
if __name__ == "__main__":
    # 1. Configura o leitor de argumentos
    parser = argparse.ArgumentParser(description="Flower Client")
    
    # 2. Define o argumento do endereço do servidor
    parser.add_argument(
        "--server_address", 
        type=str, 
        default="127.0.0.1:8080", 
        help="Endereço do servidor FL (ex: 127.0.0.1:8080 ou server1:8080)"
    )
    
    # 3. Lê o que foi digitado no terminal
    args = parser.parse_args()

    print(f" Iniciando cliente e conectando ao servidor em: {args.server_address}")

    # 4. Inicia o cliente apontando para a variável dinâmica
    fl.client.start_numpy_client(
        server_address=args.server_address, 
        client=FlowerClient()
    )