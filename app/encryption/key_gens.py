from base64 import b64decode, b64encode
from Crypto.PublicKey import RSA
from Crypto.Cipher import AES, PKCS1_OAEP
from ..networking import client
import threading
import hashlib
import pyDH


def generate_rsa_keys():
    d1 = pyDH.DiffieHellman()

    pub_key_b64 = b64decode(pub_key)
    pub_key_rsa = RSA.importKey(pub_key_b64)

    with open("./prv_key.pem", "wb") as file:
        file.write()
    
    with open("./pub_key.pem", "wb") as file:
        file.write()

def send_rsa_key(port):
    gui_client = client.Client()
    with open("./pub_key.pem", "r") as file:
        pub_key = file.read()
        gui_client.send_message(port.get(),pub_key)

def generate_partial_key(guest_pub_key):

    with open("./pub_key.pem", "r") as file:
        pub_key=file.read()
        my_hash = int.from_bytes(hashlib.sha256(pub_key.encode('utf-8')).digest(), 'big')
        guest_hash=int.from_bytes(hashlib.sha256(guest_pub_key.encode('utf-8')).digest(), 'big')
        if my_hash>guest_hash:
            guest_rsa_key=RSA.import_key(guest_pub_key)
            cipher_rsa = PKCS1_OAEP.new(guest_rsa_key)
            print(cipher_rsa)
        else:
            my_rsa_key=RSA.import_key(pub_key)
            print(pub_key)

    