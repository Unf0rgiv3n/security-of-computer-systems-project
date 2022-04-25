import socket
import threading
from .networking_consts import *

def handle_client(conn, addr):
    print(f"Client {addr}connected")
    
    msg_length = conn.recv(HEADER).decode(FORMAT)
    if msg_length:
        msg_length = int(msg_length)
        msg = conn.recv(msg_length).decode(FORMAT)
        print(msg)

def start_server(port: str):
    print("[INFO] Starting server")
    port = int(port)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.bind((SERVER, port))
        server.listen()
        print(f"[LISTENING] Server is listening on port {port}")
        while True:
            conn, addr = server.accept()
            thread = threading.Thread(target=handle_client, args=(conn, addr))
            thread.start()
