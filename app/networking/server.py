from ast import Bytes
from distutils.command.install import SCHEME_KEYS
import random
import socket
import threading
from .networking_consts import *
from ..event import Event
from ..encryption import key_gens
from ..networking.client import Client
import time

class Server:
    server_events = Event()
    session_key = None
    guest_pub_key = ""
    client = Client()

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
                #msg = conn.recv(msg_length).decode(FORMAT)
                msg = conn.recv(msg_length)
                if self.session_key is not None:
                    msg = key_gens.decrypt_with_AES(msg,self.session_key).decode(FORMAT)
                else:
                    msg = msg.decode(FORMAT)
                if self.guest_pub_key.__eq__(""):
                    self.guest_pub_key=msg
                    self.exchange_session_key(conn,addr)
                else:
                    self.server_events.post_event("receive_msg", msg)
                    print(msg)

    def exchange_session_key(self,conn,addr):
        if key_gens.should_generate_session_key(self.guest_pub_key):
            while not self.client.is_connected():
                time.sleep(3)
            self.client.send_message_bytes(key_gens.get_encoded_AES(self.guest_pub_key))
            self.session_key=key_gens.get_AES()
            self.client.set_session_key(self.session_key)
            print(f"[INFO] Uzgodniony klucz sesyjny {self.session_key}")
        else:
            msg_length = conn.recv(HEADER).decode(FORMAT)
            msg_length = int(msg_length)
            msg = conn.recv(msg_length)
            self.session_key=key_gens.decode_AES(msg)
            self.client.set_session_key(self.session_key)
            print(f"[INFO] Uzgodniony klucz sesyjny {self.session_key}")

    def start_server(self, port: str, client: Client):
        print("[INFO] Starting server")
        self.port = int(port)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((SERVER, self.port))
        self.socket.listen()
        self.client = client
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
    