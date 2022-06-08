import time
import tkinter as tk
from tkinter import BOTH, END, INSERT, ttk
from tkinter import filedialog as fd
from tkinter.messagebox import showinfo
from turtle import bgcolor
from typing import Callable
from functools import partial
import os
from typing_extensions import Self

from .gui_networking_handlers import NetworkingHandler

class Gui(tk.Tk):
    def __init__(self, title: str):
        super().__init__()

        self.title(title)
        self.geometry('600x400')
        self.resizable(False, False)
        self.style= ttk.Style()
        self.style.theme_use('clam')

        self._create_grid(row_num=6, col_num=2)

        self._select_file_btn = self._create_button(row=1,column=1, columnspan=2, 
                                                    text='Select file', command=self._select_file)

        self._msg_received_text_box = self._create_text_box(row=0, column=0, rowspan=4, columnspan=1,
                                                            bg = "black", fg = "white")
        self._msg_send_entry_box = self._create_entry_box(row=4, column=0, rowspan=1, columnspan=1)
        self._sending_port_entry_box = self._create_entry_box(row=3, column=1)
        self._send_text_box_btn = self._create_button(row=5,column=0, text='Send text', 
            command=partial(NetworkingHandler.handle_send_message, self._msg_send_entry_box))
        self._progress_bar = self._create_progress_bar(row=6,column=0,rowspan=1,columnspan=2)
        self._combobox = self._create_combobox(row=0,column=1, rowspan=1, columnspan=2)
        self._listener_port_entry_box = self._create_entry_box(row=2, column=1, rowspan=1, columnspan=1)
        self._listen_to_port_btn = self._create_button(row=2, column=2, text='Listen on port', 
            command=partial(NetworkingHandler.handle_set_port, self._listener_port_entry_box, self._msg_received_text_box,self._combobox))
        self._connect_to_port_btn = self._create_button(row=3, column=2, text='Connect to port',
            command=partial(NetworkingHandler.handle_connect_to_port, self._sending_port_entry_box,self._msg_received_text_box))

        self._drop_connection_btn = self._create_button(row=4,column=1, rowspan=2, text='Drop connection with server', 
                                                        command=NetworkingHandler.handle_stop_client)
        self._drop_listening_btn = self._create_button(row=4,column=2, rowspan=2, text='Drop listening on port',
                                                       command=NetworkingHandler.handle_stop_server)

    def _create_progress_bar(self,row, column, rowspan, columnspan):
        progress_bar = ttk.Progressbar(self,length=1000)
        progress_bar.grid(row=row,column=column, rowspan=rowspan, columnspan=columnspan, sticky='nsew')
        progress_bar['value'] = 0
        return progress_bar

    def _create_grid(self, row_num: int, col_num: int):
        for i in range(row_num):
            self.rowconfigure(i, weight=1)
        
        for i in range(col_num):
            self.columnconfigure(i, weight=1)

    def _create_button(self, row: int, column: int, rowspan: int = 1, columnspan: int = 1,
                       text: str = None, command: Callable[[], None] = None) ->  ttk.Button:
        button = ttk.Button(self, text=text, command=command)
        button.grid(row=row,column=column, rowspan=rowspan, columnspan=columnspan, sticky='nsew')
        return button
    
    def _create_entry_box(self, row: int, column: int, rowspan: int = 1, columnspan: int = 1,
                            bg: str = "white", fg: str = "black") -> tk.Entry:
        entry_box = tk.Entry(self, bg=bg, fg=fg)
        entry_box.grid(row=row, column=column, rowspan=rowspan, columnspan=columnspan, sticky='nsew')
        return entry_box

    def _create_text_box(self, row: int, column: int, rowspan: int = 1, columnspan: int = 1,
                            bg: str = "white", fg: str = "black") -> tk.Text:
        text_box = tk.Text(self, bg=bg, fg=fg, height=10, width=25)
        text_box.grid(row=row, column=column, rowspan=rowspan, columnspan=columnspan, sticky='nsew')
        return text_box
        
    def _create_combobox(self, row: int, column: int, rowspan: int = 1, columnspan: int = 1) -> ttk.Combobox:
        cipher_mode = ['ECB', 'CBC']
        self.style.configure("TCombobox", fieldbackground= "white", background= "white")
        combobox = ttk.Combobox(self, state="readonly", textvariable=cipher_mode[0] , values=(cipher_mode))
        combobox.set(cipher_mode[0])
        combobox.grid(row=row, column=column, rowspan=rowspan, columnspan=columnspan, sticky='nsew')
        combobox.bind("<<ComboboxSelected>>", self._handler_focus_out)
        return combobox

    def _select_file(self):
        self._progress_bar['value'] = 0
        filetypes = (
            ('text files', '*.txt'),
            ('All files', '*.*')
        )

        filename = fd.askopenfilename(
            title='Open a file',
            initialdir=os.getcwd(),
            filetypes=filetypes)

        if not filename:
            return

        showinfo(
            title='Selected File',
            message=filename
        )
        NetworkingHandler.handle_send_file(filename,self._progress_bar)

    def _handler_focus_out(self, _):
        self.focus()