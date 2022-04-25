from cgitb import text
from ..networking import client, server
import threading

def handle_set_port(text_box):
    #start_server(text_box.get())
    port = text_box.get()
    thread = threading.Thread(target=server.start_server, args=(port,), daemon=True)
    thread.start()

def handle_connect_port(text_box_port, text_box_msg):
    port = text_box_port.get()
    msg = text_box_msg.get()
    thread = threading.Thread(target=client.send_message, args=(port, msg,))
    thread.start()