from ast import Bytes
import socket
from .networking_consts import *
from ..event import Event
from ..encryption import key_gens

class Client:
    client_events = Event()

    def __init__(self) -> None:
        self.socket = None
        self.port = None
        self.connected = False

    def send_message(self, msg: str):
        message = msg.encode(FORMAT)
        msg_length = len(message)
        send_length = str(msg_length).encode(FORMAT)
        send_length  += b' ' * (HEADER - len(send_length))
        self.socket.send(send_length)
        #self.client_events.post_event("send_msg", message)
        self.socket.send(message)

    def send_message_bytes(self, msg: Bytes):
        message = msg
        msg_length = len(message)
        send_length = str(msg_length).encode(FORMAT)
        send_length  += b' ' * (HEADER - len(send_length))
        self.socket.send(send_length)
        #self.client_events.post_event("send_msg", message)
        self.socket.send(message)

    def start_client(self, port: str):
        print("[INFO] Starting client")
        self.port = int(port)
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((SERVER, self.port))
        print(f"[INFO] Client connected to {SERVER}:{self.port}")
        self.socket = client
        self.connected = True
        self.send_message(key_gens.get_public_key())
        


    def stop_client(self):
        print(f"[INFO] Shutting down client connected to: {self.port}")
        self.socket.close()
        self.socket = None
        self.port = None

    def is_connected(self):
        return self.connected