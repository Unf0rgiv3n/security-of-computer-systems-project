import socket
import threading
from .networking_consts import *
from ..event import Event

class Server:
    server_events = Event()

    def handle_client(self, conn, addr):
        print(f"Client {addr} connected")
        
        msg_length = conn.recv(HEADER).decode(FORMAT)
        if msg_length:
            msg_length = int(msg_length)
            msg = conn.recv(msg_length).decode(FORMAT)
            self.server_events.post_event("receive_msg", msg)
            print(msg)

    def start_server(self, port: str):
        print("[INFO] Starting server")
        port = int(port)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
            server.bind((SERVER, port))
            server.listen()
            print(f"[LISTENING] Server is listening on port {port}")
            while True:
                conn, addr = server.accept()
                thread = threading.Thread(target=self.handle_client, args=(conn, addr))
                thread.start()
