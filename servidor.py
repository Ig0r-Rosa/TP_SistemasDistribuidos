import socket
import threading
from collections import defaultdict

class VectorClockServer:
    def __init__(self, host='localhost', port=5000):
        self.host = host
        self.port = port
        self.vector_clock = defaultdict(int)  # {process_id: timestamp}
        self.process_id = "5000 (servidor)"  # ID do servidor
        self.clients = {}    # {client_id: (address, port)}
        self.lock = threading.Lock()

    def handle_client(self, conn, addr):
        # Recebe o ID do cliente na primeira mensagem
        initial_data = conn.recv(1024).decode()
        if not initial_data:
            conn.close()
            return
            
        try:
            sender_id, vc_str, _ = initial_data.split(';', 2)
            sender_id = int(sender_id)
        except:
            conn.close()
            return

        # Verifica se o cliente já está conectado
        if sender_id not in self.clients:
            self.clients[sender_id] = conn
            print(f"Cliente {sender_id} conectado: {addr}")
        else:
            print(f"Cliente {sender_id} enviou nova mensagem")

        # Processa mensagens subsequentes
        while True:
            data = conn.recv(1024).decode()
            if not data:
                break

            # Formato: "sender_id;vector_clock;message"
            sender_id, vc_str, message = data.split(';', 2)
            sender_id = int(sender_id)
            received_vc = eval(vc_str)  # Converte string para dicionário

            with self.lock:
                # Atualiza o relógio vetorial do servidor
                for pid in received_vc:
                    self.vector_clock[pid] = max(self.vector_clock[pid], received_vc[pid])
                self.vector_clock[self.process_id] += 1

                # Exibe a mensagem e o relógio atualizado
                print(f"Mensagem recebida de Cliente {sender_id}: {message}")
                print(f"Relógio Vetorial atual: {dict(self.vector_clock)}")

                # Envia confirmação com o novo relógio
                response = f"{self.process_id};{dict(self.vector_clock)};ACK"
                conn.sendall(response.encode())

        conn.close()

    def start(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((self.host, self.port))
            s.listen()
            print(f"Servidor ouvindo em {self.host}:{self.port}")

            while True:
                conn, addr = s.accept()
                threading.Thread(target=self.handle_client, args=(conn, addr)).start()

if __name__ == "__main__":
    server = VectorClockServer()
    server.start()