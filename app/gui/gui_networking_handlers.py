from cgitb import text
from click import progressbar
from ..networking import client, server
import threading

class NetworkingHandler:
    
    _gui_server = None
    _gui_client = None

    @classmethod
    def handle_set_port(self, input_box, text_box,combobox):
        port = input_box.get()
        encryption_method = combobox.get()
        self._gui_server = server.Server()
        if self._gui_client is None:
            self._gui_client = client.Client()
        #gui_server.server_events.subscribe("receive_msg", handle_receive_msg)
        thread = threading.Thread(target=self._gui_server.start_server, args=(port,self._gui_client,encryption_method,text_box), daemon=True)
        thread.start()

    @classmethod
    def handle_connect_to_port(self, input_box,text_box):
        port = input_box.get()
        if self._gui_client is None:
            self._gui_client = client.Client()
        thread = threading.Thread(target=self._gui_client.start_client, args=(port,text_box), daemon=True)
        thread.start()

    @classmethod
    def handle_stop_server(self):
        if self._gui_server and self._gui_server.socket:
            self._gui_server.stop_server()
            self._gui_server = None
        else:
            print("[WARNING] Server is not listening")

    @classmethod
    def handle_stop_client(self):
        if self._gui_client and self._gui_client.socket:
            self._gui_client.stop_client()
            self._gui_client = None
        else:
            print("[WARNING] Client is not connected")

    @classmethod
    def handle_send_message(self, text_box_msg):
        if self._gui_client:
            msg = text_box_msg.get()
            self._gui_client.send(msg,self._gui_client.STRING_MSG)
        else: 
            print("[WARNING] Client not connected")

    @classmethod
    def handle_send_file(self,filename,progress_bar):
        if self._gui_client:
            self._gui_client.send(filename,self._gui_client.FILE_MSG,progress_bar)
        else: 
            print("[WARNING] Client not connected")

    @classmethod
    def handle_receive_msg(self, msg):
        pass