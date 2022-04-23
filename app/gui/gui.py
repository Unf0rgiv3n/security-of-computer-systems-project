from ast import Call
from logging import root
from pydoc import text
import tkinter as tk
from tkinter import Place, ttk
from tkinter import filedialog as fd
from tkinter.messagebox import showinfo
from turtle import bgcolor
from typing import Callable
import os

from ..encryption.key_gens import generate_rsa_keys, send_rsa_key

class Gui(tk.Tk):
    def __init__(self, title: str):
        super().__init__()

        self.title(title)
        self.geometry('600x400')
        self.resizable(False, False)
        self.style= ttk.Style()
        self.style.theme_use('clam')

        self._create_grid(row_num=5, col_num=2)

        self._gen_rsa_btn = self._create_button(row=0,column=0, text='Generate RSA keys', command=generate_rsa_keys)
        self._send_rsa_btn = self._create_button(row=1,column=0, text='Send RSA key', command=send_rsa_key)

        self._select_file_btn = self._create_button(row=1,column=1, columnspan=2, text='Select file', command=self._select_file)

        self._text_box = self._create_text_box(row=2, column=0, rowspan=3, columnspan=1)
        self._send_text_box_btn = self._create_button(row=5,column=0, text='Send text', command=None)

        self._combobox = self._create_combobox(row=0,column=1, rowspan=1, columnspan=2)
        self._listener_port_text_box = self._create_text_box(row=2, column=1, rowspan=1, columnspan=1)
        self._listen_to_port_btn = self._create_button(row=2, column=2, text='Listen on port', command=None)

        self._sending_port_text_box = self._create_text_box(row=3, column=1)
        self._send_port_text_box = self._create_button(row=3, column=2, text='Send port confirmation', command=None)

    def _create_grid(self, row_num: int, col_num: int):
        for i in range(row_num):
            self.rowconfigure(i, weight=1)
        
        for i in range(col_num):
            self.columnconfigure(i, weight=1)

    def _create_button(self, row: int, column: int, rowspan: int = 1, columnspan: int = 1, text: str = None, command: Callable[[], None] = None) ->  ttk.Button:
        button = ttk.Button(self, text=text, command=command)
        button.grid(row=row,column=column, rowspan=rowspan, columnspan=columnspan, sticky='nsew')
        return button
    
    def _create_text_box(self, row: int, column: int, rowspan: int = 1, columnspan: int = 1) -> tk.Entry:
        text_box = tk.Entry(self)
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

    def _handler_focus_out(self, _):
        self.focus()