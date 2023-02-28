from hashlib import md5
from Crypto.Cipher import AES
from base64 import b64decode
from base64 import b64encode

# Padding for the input string --not
# related to encryption itself.
BLOCK_SIZE = 16  # Bytes
#BLOCK_SIZE = 64  # Bytes
def pad(s): return s + (BLOCK_SIZE - len(s) % BLOCK_SIZE) * \
    chr(BLOCK_SIZE - len(s) % BLOCK_SIZE)


def unpad(s): return s[:-ord(s[len(s) - 1:])]

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
        raw = pad(raw)
        cipher = AES.new(self.key.encode('utf-8'), AES.MODE_ECB)
        return b64encode(cipher.encrypt(raw.encode('utf-8')))

    def decrypt(self, enc):
        enc = b64decode(enc)
        cipher = AES.new(self.key.encode('utf-8'), AES.MODE_ECB)
        return unpad(cipher.decrypt(enc)).decode('utf8')
