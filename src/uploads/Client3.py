# Arquivo Client.py padrão com modelo e dataset igual ao Client_arg.py, porém sem a estrutura de argparse e não otimizado para o docker
# A manutenção do mesmo se deve pelo funcionamento do contador de download, cada client.py esta referenciado no banco de dados para um servidor FL do Dashboard
import tensorflow as tf
import flwr as fl

model = tf.keras.applications.MobileNetV2((32, 32, 3), classes=10, weights=None)
model.compile("adam", "sparse_categorical_crossentropy", metrics=["accuracy"])
(x_train, y_train), (x_test, y_test) = tf.keras.datasets.cifar10.load_data()

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

fl.client.start_numpy_client(server_address="127.0.0.1:8082", client=FlowerClient())
