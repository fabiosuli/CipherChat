import base64
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes


class AESCipher:
    def __init__(self, password: str, salt=None):
        self.password = password
        if salt is None:
            self.salt = get_random_bytes(16)
        else:
            self.salt = salt

        self.key = PBKDF2(self.password, self.salt, dkLen=32, count=100000)

    def encrypt(self, raw: str) -> str:
        cipher = AES.new(self.key, AES.MODE_CBC)
        ct_bytes = cipher.encrypt(pad(raw.encode(), AES.block_size))
        return base64.b64encode(self.salt + cipher.iv + ct_bytes).decode('utf-8')

    def decrypt(self, enc: str) -> str:
        try:
            enc = base64.b64decode(enc)
            salt = enc[:16]
            iv = enc[16:32]
            ct = enc[32:]
            key = PBKDF2(self.password, salt, dkLen=32, count=100000)

            cipher = AES.new(key, AES.MODE_CBC, iv)
            pt = unpad(cipher.decrypt(ct), AES.block_size)
            return pt.decode('utf-8')
        except (ValueError, KeyError):
            raise ValueError("A frase de descriptografia está incorreta.")