from ..networking import client, server
import threading

def handle_set_port(input_box, text_box):
    #start_server(text_box.get())
    port = input_box.get()
    gui_server = server.Server()
    #gui_server.server_events.subscribe("receive_msg", handle_receive_msg)
    thread = threading.Thread(target=gui_server.start_server, args=(port,), daemon=True)
    thread.start()

def handle_connect_port(text_box_port, text_box_msg):
    port = text_box_port.get()
    msg = text_box_msg.get()
    gui_client = client.Client()
    thread = threading.Thread(target=gui_client.send_message, args=(port, msg,))
    thread.start()

def handle_receive_msg(msg):
    pass