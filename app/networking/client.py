import socket
from .networking_consts import *
from ..event import Event

class Client:
    client_events = Event()

    def send_message(self, port: str, msg: str):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
            port = int(port)
            client.connect((SERVER, port))
            message = msg.encode(FORMAT)
            msg_length = len(message)
            send_length = str(msg_length).encode(FORMAT)
            send_length  += b' ' * (HEADER - len(send_length))
            client.send(send_length)
            #self.client_events.post_event("send_msg", message)
            client.send(message)
