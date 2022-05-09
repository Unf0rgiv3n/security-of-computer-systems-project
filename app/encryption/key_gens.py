from ast import Bytes
from base64 import b64decode, b64encode
from Cryptodome.PublicKey import RSA
from ..networking import client
import threading
import hashlib
import os 

def generate_keys():
    
    key=RSA.generate(2048)
    prv_key=key.exportKey('PEM') #need to add encrypt password
    pub_key=key.publickey().exportKey('PEM')
    aes_key = os.urandom(16)

    with open("./prv_key.pem", "wb") as file:
        file.write(prv_key)
    
    with open("./pub_key.pem", "wb") as file:
        file.write(pub_key)
    
    with open("./aes_key.txt", "wb") as file:
        file.write(aes_key)
    
def get_public_key() -> str:
    with open("./pub_key.pem", "r") as file:
        pub_key = file.read()
        return pub_key

def get_private_key() -> str:
    with open("./prv_key.pem", "r") as file:
        prv_key = file.read()
        return prv_key

def get_AES() -> bytes:
    with open("./aes_key.txt", "rb") as file:
        aes = file.read()
        return aes

def should_generate_session_key(guest_pub_key) -> bool:
    with open("./pub_key.pem", "r") as file:
        pub_key=file.read()
        my_hash = int.from_bytes(hashlib.sha256(pub_key.encode('utf-8')).digest(), 'big')
        guest_hash=int.from_bytes(hashlib.sha256(guest_pub_key.encode('utf-8')).digest(), 'big')
        if my_hash>guest_hash:
            return True
        else:
            return False