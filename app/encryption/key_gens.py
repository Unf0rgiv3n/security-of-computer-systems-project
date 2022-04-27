from base64 import b64decode, b64encode
from Cryptodome.PublicKey import RSA
from Cryptodome.Cipher import AES, PKCS1_OAEP
from ..networking import client
import threading
import hashlib

def generate_rsa_keys():
    
    key=RSA.generate(2048)
    prv_key=key.exportKey('PEM') #need to add encrypt password
    pub_key=key.publickey().exportKey('PEM')

    with open("./prv_key.pem", "wb") as file:
        file.write(prv_key)
    
    with open("./pub_key.pem", "wb") as file:
        file.write(pub_key)

def send_rsa_key(port):
    gui_client = client.Client()
    with open("./pub_key.pem", "r") as file:
        pub_key = file.read()
        gui_client.send_message(port.get(),pub_key)

    