from ast import Bytes
from distutils.command.install import SCHEME_KEYS
from math import fabs
import random
import socket
import threading
from xxlimited import Str

from blinker import receiver_connected
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
    
    def receive_string_message(self,conn,decrypt = True,msg_ack = True) -> str:
        msg_length = conn.recv(HEADER).decode(FORMAT)
        if msg_length:
            msg_length = int(msg_length)
            msg = conn.recv(msg_length)
            if self.encryption_obj is not None and decrypt:
                msg = self.encryption_obj.decrypt_with_AES(msg).decode(FORMAT)
                if not msg == self.message_ack and msg_ack:
                    self.client.send(self.message_ack,self.client.STRING_MSG)
                return msg
            else:
                msg = msg.decode(FORMAT)
                return msg
        else:
            return None

    def receive_bytes_message(self,conn) -> bytes:
        msg_length = conn.recv(HEADER).decode(FORMAT)
        if msg_length:
            msg_length = int(msg_length)
            msg = conn.recv(msg_length)
            return msg

    def receive_file(self,conn):
        chunk_size = 1024
        readed = 0
        size_of_file = int(self.receive_string_message(conn))
        name_of_file = self.receive_string_message(conn)
        with open(name_of_file, "wb") as file:
            while readed < size_of_file:
                msg_length = conn.recv(HEADER)
                while len(msg_length) < HEADER:
                    msg_length += conn.recv(HEADER - len(msg_length))
                msg_length = msg_length.decode(FORMAT)
                if msg_length:
                    msg_length_encrypted = int(msg_length)
                    chunk_encrypted = conn.recv(msg_length_encrypted)
                    while len(chunk_encrypted) < msg_length_encrypted:
                        chunk_encrypted += conn.recv(msg_length_encrypted - len(chunk_encrypted))
                    ## encrypted size != data size
                    chunk = self.encryption_obj.decrypt_with_AES(chunk_encrypted)
                    file.write(chunk)
                    readed = readed + chunk_size

    def handle_client(self, conn, addr):
        print(f"[INFO] Client {addr} connected")
        while self.listening:
            type_of_message = self.receive_string_message(conn,True,False)
            if type_of_message == "string":
                message = self.receive_string_message(conn)
                if self.encryption_obj is None:   #its public key
                    self.guest_pub_key=message
                    self.negotiate_mode_and_key(conn) 
                elif message is not None:
                    print(message)
            if type_of_message == "file":
                self.receive_file(conn)

    def negotiate_mode_and_key(self,conn):
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
        encrypted_session_key = self.encryption_obj.encrypt_with_RSA(key_gens.get_AES())
        self.client.send(encrypted_session_key,self.client.BYTES_MSG)
        self.session_key = key_gens.get_AES()
        print(f"[INFO] Session key agreed {self.session_key}")

    def send_and_set_encryption_properties(self):
        self.client.send(self.encryption_method,self.client.STRING_MSG)
        if (self.encryption_method == "CBC"):
            self.encryption_method = self.encryption_obj.MODE_CBC
            self.encryption_obj.set_AES_cipher(self.session_key,self.encryption_method,os.urandom(16))
            self.client.send(self.encryption_obj.get_AES_IV(),self.client.BYTES_MSG)
        else:
            self.encryption_method = self.encryption_obj.MODE_ECB
            self.encryption_obj.set_AES_cipher(self.session_key,self.encryption_method)

    def receive_session_key(self,conn):
        self.encryption_obj.set_RSA_cipher(key_gens.get_private_key())
        type_of_message = self.receive_string_message(conn, False)
        encrypted_session_key = self.receive_bytes_message(conn)
        self.session_key=self.encryption_obj.decrypt_with_RSA(encrypted_session_key)
        print(f"[INFO] Session key agreed {self.session_key}")

    def receive_encryption_properties(self,conn):
        type_of_message = self.receive_string_message(conn, False)
        self.encryption_method = self.receive_string_message(conn, False)
        if (self.encryption_method == "CBC"):
            self.encryption_method = self.encryption_obj.MODE_CBC
            type_of_message = self.receive_string_message(conn, False)
            IV_vector = self.receive_bytes_message(conn)
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
    