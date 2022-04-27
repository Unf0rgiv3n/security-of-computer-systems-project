from ast import Bytes
from distutils.command.install import SCHEME_KEYS
import random
import socket
import threading
from .networking_consts import *
from ..event import Event
from ..encryption import key_gens

class Server:
    server_events = Event()
    session_key = ""
    guest_pub_key = ""
    method_partial_key="empty"

    def __init__(self) -> None:
        self.socket = None
        self.port = None
        self.listening = False
    
    def handle_client(self, conn, addr):
        print(f"[INFO] Client {addr} connected")
        
        while self.listening:
            msg_length = conn.recv(HEADER).decode(FORMAT)
            if msg_length:
                msg_length = int(msg_length)
                msg = conn.recv(msg_length).decode(FORMAT)
                self.server_events.post_event("receive_msg", msg)
                print(msg)

    def get_pub_key(self, conn, addr):
        print(f"[INFO] Client {addr} connected")
        msg_length = conn.recv(HEADER).decode(FORMAT)
        if msg_length:
            msg_length = int(msg_length)
            msg = conn.recv(msg_length).decode(FORMAT)
            self.server_events.post_event("receive_msg", msg)
            return msg

    def start_server(self, port: str):
        print("[INFO] Starting server")
        self.port = int(port)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((SERVER, self.port))
        self.socket.listen()
        print(f"[INFO] Server is listening on port {self.port}")
        self.listening = True
        while self.listening:
            try:
                conn, addr = self.socket.accept()
            except Exception:
                print("[INFO] Closed connection")
                break
            thread = threading.Thread(target=self.handle_client, args=(conn, addr))
            thread.start()
    
    def stop_server(self):
        print(f"[INFO] Shutting down server listening on: {self.port}")
        self.socket.close()
        self.socket = None
        self.port = None
    