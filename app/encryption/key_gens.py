from ast import Bytes
from base64 import b64decode, b64encode
from Cryptodome.PublicKey import RSA
from ..networking import client
import threading
import hashlib
import os 
import hashlib
from Cryptodome.Cipher import AES, PKCS1_OAEP
from Crypto.Util.Padding import pad, unpad


def generate_keys():
    
    key=RSA.generate(2048)
    prv_key=key.exportKey('PEM') #need to add encrypt password
    pub_key=key.publickey().exportKey('PEM')
    aes_key = os.urandom(16)

    password = "kluczyk"
    m = hashlib.sha256()
    m.update(password.encode("utf-8"))
    hash = m.digest()
    AES_cipher = AES.new(hash, AES.MODE_ECB)
    encrypted_prv_key = AES_cipher.encrypt(pad(prv_key,16))
    if not os.path.isdir('directory1'):
        os.mkdir("directory1")
        os.mkdir("directory2")
    
    with open("./directory1/prv_key.pem", "wb") as file:
        file.write(encrypted_prv_key)
    
    with open("./directory2/pub_key.pem", "wb") as file:
        file.write(pub_key)
    
    with open("./aes_key.txt", "wb") as file:
        file.write(aes_key)
    
def get_public_key() -> str:
    with open("./directory2/pub_key.pem", "r") as file:
        pub_key = file.read()
        return pub_key

def get_private_key(password: str) -> str:

    with open("./directory1/prv_key.pem","rb") as file:
        encrypted_prv_key = file.read()
        m = hashlib.sha256()
        m.update(password.encode("utf-8"))
        hash = m.digest()
        AES_cipher = AES.new(hash, AES.MODE_ECB)
        decrypted = unpad(AES_cipher.decrypt(encrypted_prv_key),16)
        with open("./temp.txt",'wb') as file2:
            file2.write(decrypted)
        with open("./temp.txt",'r') as file2:
            prv_key = file2.read()
        os.remove("./temp.txt")
        return prv_key

def get_AES() -> bytes:
    with open("./aes_key.txt", "rb") as file:
        aes = file.read()
        return aes

def should_generate_session_key(guest_pub_key) -> bool:
    with open("./directory2/pub_key.pem", "r") as file:
        pub_key=file.read()
        my_hash = int.from_bytes(hashlib.sha256(pub_key.encode('utf-8')).digest(), 'big')
        guest_hash=int.from_bytes(hashlib.sha256(guest_pub_key.encode('utf-8')).digest(), 'big')
        if my_hash>guest_hash:
            return True
        else:
            return False