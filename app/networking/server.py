from ast import Bytes
from distutils.command.install import SCHEME_KEYS
import random
import socket
import threading
from .networking_consts import *
from ..event import Event
from ..encryption import key_gens
from ..encryption.encryption import Encryption
from ..networking.client import Client
import time

from app.encryption import encryption

class Server:
    server_events = Event()
    guest_pub_key : str
    client : Client
    encryption_obj : Encryption

    def __init__(self) -> None:
        self.socket = None
        self.port = None
        self.listening = False
        self.encryption_obj = None
        self.client = None
    
    def handle_client(self, conn, addr):
        print(f"[INFO] Client {addr} connected")
        while self.listening:
            msg_length = conn.recv(HEADER).decode(FORMAT)
            if msg_length:
                msg_length = int(msg_length)
                msg = conn.recv(msg_length)
                if self.encryption_obj is not None:
                    msg = self.encryption_obj.decrypt_with_AES(msg).decode(FORMAT)
                else:
                    msg = msg.decode(FORMAT)
                if self.encryption_obj is None:
                    self.guest_pub_key=msg
                    self.exchange_session_key(conn,addr)
                else:
                    self.server_events.post_event("receive_msg", msg)
                    print(msg)

    def exchange_session_key(self,conn,addr):
        if key_gens.should_generate_session_key(self.guest_pub_key):
            while not self.client.is_connected():
                time.sleep(3)
            self.encryption_obj = Encryption()
            self.encryption_obj.set_RSA_cipher(self.guest_pub_key)
            self.client.send_message_bytes(self.encryption_obj.encrypt_with_RSA(key_gens.get_AES()))
            self.session_key = key_gens.get_AES()
            self.encryption_obj.set_AES_cipher(self.session_key,self.encryption_obj.MODE_ECB)
            self.client.set_encryption(self.encryption_obj)
            print(f"[INFO] Uzgodniono klucz sesyjny {self.session_key}")
        else:
            self.encryption_obj = Encryption()
            self.encryption_obj.set_RSA_cipher(key_gens.get_private_key())
            msg_length = conn.recv(HEADER).decode(FORMAT)
            msg_length = int(msg_length)
            msg = conn.recv(msg_length)
            self.session_key=self.encryption_obj.decrypt_with_RSA(msg)
            self.encryption_obj.set_AES_cipher(self.session_key,self.encryption_obj.MODE_ECB)
            self.client.set_encryption(self.encryption_obj)
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
    