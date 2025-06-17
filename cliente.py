import socket
import threading
from collections import defaultdict

class VectorClockClient:
    def __init__(self, server_host='localhost', server_port=5000):
        self.server_host = server_host
        self.server_port = server_port
        self.vector_clock = defaultdict(int)
        self.process_id = int(input("Digite o ID deste cliente: "))
        self.vector_clock[self.process_id] = 0
        self.connection = None  # Armazena a conexão persistentemente

    def connect(self):
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connection.connect((self.server_host, self.server_port))
        
        # Envia uma mensagem inicial para identificar o cliente
        initial_message = f"{self.process_id};{dict(self.vector_clock)};INIT"
        self.connection.sendall(initial_message.encode())

    def send_message(self):
        if not self.connection:
            self.connect()
            
        message = input("Digite a mensagem: ")
        self.vector_clock[self.process_id] += 1
        data = f"{self.process_id};{dict(self.vector_clock)};{message}"
        self.connection.sendall(data.encode())
        
        # Recebe resposta
        response = self.connection.recv(1024).decode()
        print(f"Resposta do servidor: {response}")

    def start(self):
        self.connect()
        while True:
            self.send_message()

if __name__ == "__main__":
    client = VectorClockClient()
    client.start()