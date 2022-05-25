from ast import Bytes
import socket
from xmlrpc.client import boolean
from .networking_consts import *
from ..event import Event
from ..encryption import key_gens
from ..encryption.encryption import Encryption
from app import encryption
import os

class Client:
    
    client_events = Event()
    encryption_obj : Encryption

    STRING_MSG = 1
    BYTES_MSG = 2
    FILE_MSG = 3

    def __init__(self) -> None:
        self.socket = None
        self.port = None
        self.connected = False
        self.session_key = None
        self.encryption_obj = None

    def send_message(self, msg: str):
        message = msg.encode(FORMAT)
        if self.encryption_obj is not None:
            message = self.encryption_obj.encrypt_with_AES(message)
        msg_length = len(message)
        send_length = str(msg_length).encode(FORMAT)
        send_length  += b' ' * (HEADER - len(send_length))
        self.socket.send(send_length)
        #self.client_events.post_event("send_msg", message)
        self.socket.send(message)

    def send_file(self,filepath: str, size):
        read_size = 1024
        readed = 0
        with open(filepath, "rb") as file:
            while readed < size:
                data_chunk = file.read(read_size)
                encrypted = self.encryption_obj.encrypt_with_AES(data_chunk)
                readed = readed + read_size

                msg_length = len(encrypted)
                send_length = str(msg_length).encode(FORMAT)
                send_length  += b' ' * (HEADER - len(send_length))

                self.socket.send(send_length)
                self.socket.send(encrypted)

    def send(self, msg, type_of_msg):
        if type_of_msg == self.STRING_MSG:
            self.send_message("string") #sending header
            self.send_message(msg) # sending message
        if type_of_msg == self.BYTES_MSG:
            self.send_message("bytes")
            self.send_message_bytes(msg)
        if type_of_msg == self.FILE_MSG:
            file_size = os.path.getsize(msg)
            file_name = os.path.basename(msg)
            self.send_message("file")
            self.send_message(str(file_size))
            self.send_message(file_name)
            self.send_file(msg,file_size)
            

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
        self.send(key_gens.get_public_key(),self.STRING_MSG)

        
    def stop_client(self):
        print(f"[INFO] Shutting down client connected to: {self.port}")
        self.socket.close()
        self.socket = None
        self.port = None

    def is_connected(self) -> bool:
        return self.connected

    def set_encryption(self,encryption):
        self.encryption_obj = encryption