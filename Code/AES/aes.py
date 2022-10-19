from hashlib import md5
from Crypto.Util.Padding import pad, unpad
from Crypto.Cipher import AES
from base64 import b64decode
from base64 import b64encode

# Padding for the input string --not
# related to encryption itself.
BLOCK_SIZE = 16  # Bytes

class AESCipher:
    """
    Usage:
        c = AESCipher('password').encrypt('message')
        m = AESCipher('password').decrypt(c)
    Tested under Python 3 and PyCrypto 2.6.1.
    """

    def __init__(self, key):
        self.key = md5(key.encode('utf8')).hexdigest()

    def encrypt(self, raw):
        cipher = AES.new(self.key.encode('utf-8'), AES.MODE_ECB)
        return b64encode(cipher.encrypt(pad(raw.encode('utf-8'), BLOCK_SIZE)))

    def decrypt(self, enc):
        enc = b64decode(enc)
        cipher = AES.new(self.key.encode('utf-8'), AES.MODE_ECB)
        return unpad(cipher.decrypt(enc), BLOCK_SIZE).decode('utf8')
