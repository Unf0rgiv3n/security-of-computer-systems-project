from base64 import b64encode
from Cryptodome.Cipher import AES, PKCS1_OAEP
from Crypto.Util.Padding import pad, unpad
from Cryptodome.PublicKey import RSA
from Cryptodome.Cipher import AES, PKCS1_OAEP


class Encryption:

    MODE_ECB = 1
    MODE_CBC = 2
    method :int
    

    def __init__(self) -> None:
        self.AES_cipher = None
        self.RSA_cipher = None

    def set_AES_cipher(self,key,method,IV = None):
        if IV is None:
            self.AES_cipher = AES.new(key, method)
        else:
            self.AES_cipher = AES.new(key, method, IV)
        self.method = method
        self.key = key
        self.IV = IV
        
    def set_RSA_cipher(self,RSA_key):
        self.RSA_cipher = PKCS1_OAEP.new(RSA.import_key(RSA_key))

    def encrypt_with_AES(self,msg) -> bytes:
        if self.method == self.MODE_CBC:
            self.AES_cipher = AES.new(self.key, self.method, self.IV)
        data = self.AES_cipher.encrypt(pad(msg,self.AES_cipher.block_size))
        return data

    def decrypt_with_AES(self,msg) -> bytes:
        if self.method == self.MODE_CBC:
            self.AES_cipher = AES.new(self.key, self.method, self.IV)
        data = unpad(self.AES_cipher.decrypt(msg),self.AES_cipher.block_size)
        return data

    def encrypt_with_RSA(self,msg) -> bytes:
        data = self.RSA_cipher.encrypt(msg)
        return data

    def decrypt_with_RSA(self,msg) -> bytes:
        data = self.RSA_cipher.decrypt(msg)
        return data

    def get_AES_IV(self):
        return self.IV
