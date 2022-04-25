from http import client
from operator import le
import socket
from .networking_consts import *

def send_message(port: str, msg: str):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
        port = int(port)
        client.connect((SERVER, port))
        message = msg.encode(FORMAT)
        msg_length = len(message)
        send_length = str(msg_length).encode(FORMAT)
        send_length  += b' ' * (HEADER - len(send_length))
        client.send(send_length)
        client.send(message)
