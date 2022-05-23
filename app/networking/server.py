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
import os

from app.encryption import encryption

class Server:
    message_ack = "Message Delivered"
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
        self.encryption_method = None
    
    def handle_client(self, conn, addr):
        print(f"[INFO] Client {addr} connected")
        while self.listening:
            msg_length = conn.recv(HEADER).decode(FORMAT)
            if msg_length:
                msg_length = int(msg_length)
                msg = conn.recv(msg_length)
                if self.encryption_obj is not None:
                    msg = self.encryption_obj.decrypt_with_AES(msg).decode(FORMAT)
                    self.server_events.post_event("receive_msg", msg)
                    print(msg)
                    if not msg.__eq__(self.message_ack):
                        self.client.send_message(self.message_ack)
                else:
                    msg = msg.decode(FORMAT)
                    self.guest_pub_key=msg
                    self.negotiate_mode_and_key(conn,addr)

    def negotiate_mode_and_key(self,conn,addr):
        self.encryption_obj = Encryption()
        if key_gens.should_generate_session_key(self.guest_pub_key):
            while not self.client.is_connected():
                time.sleep(3)
            self.send_and_set_session_key()
            self.send_and_set_encryption_properties()
        else:
            self.receive_session_key(conn)
            self.receive_encryption_properties(conn)
        self.client.set_encryption(self.encryption_obj)

    def send_and_set_session_key(self):
        self.encryption_obj.set_RSA_cipher(self.guest_pub_key)
        self.client.send_message_bytes(self.encryption_obj.encrypt_with_RSA(key_gens.get_AES()))
        self.session_key = key_gens.get_AES()
        ##self.client.set_encryption(self.encryption_obj)
        print(f"[INFO] Session key agreed {self.session_key}")

    def send_and_set_encryption_properties(self):
        self.client.send_message(self.encryption_method)
        if (self.encryption_method.__eq__("CBC")):
            self.encryption_method = self.encryption_obj.MODE_CBC
            self.encryption_obj.set_AES_cipher(self.session_key,self.encryption_method,os.urandom(16))
            self.client.send_message_bytes(self.encryption_obj.get_AES_IV())
        else:
            self.encryption_method = self.encryption_obj.MODE_ECB
            self.encryption_obj.set_AES_cipher(self.session_key,self.encryption_method)

    def receive_session_key(self,conn):
        self.encryption_obj.set_RSA_cipher(key_gens.get_private_key())
        msg_length = conn.recv(HEADER).decode(FORMAT)
        msg_length = int(msg_length)
        encrypted_session_key = conn.recv(msg_length)
        self.session_key=self.encryption_obj.decrypt_with_RSA(encrypted_session_key)
        print(f"[INFO] Session key agreed {self.session_key}")

    def receive_encryption_properties(self,conn):
        msg_length = conn.recv(HEADER).decode(FORMAT)
        msg_length = int(msg_length)
        msg = conn.recv(msg_length)
        self.encryption_method = msg.decode(FORMAT)
        if (self.encryption_method.__eq__("CBC")):
            self.encryption_method = self.encryption_obj.MODE_CBC
            msg_length = conn.recv(HEADER).decode(FORMAT)
            msg_length = int(msg_length)
            IV_vector = conn.recv(msg_length)
            self.encryption_obj.set_AES_cipher(self.session_key,self.encryption_method,IV_vector)
        else:
            self.encryption_method = self.encryption_obj.MODE_ECB
            self.encryption_obj.set_AES_cipher(self.session_key,self.encryption_method)

    def start_server(self, port: str, client: Client, encryption_method: str):
        print("[INFO] Starting server")
        self.port = int(port)
        self.encryption_method = encryption_method
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
    