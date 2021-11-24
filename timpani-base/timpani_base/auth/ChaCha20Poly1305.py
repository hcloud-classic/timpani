from cryptography.hazmat.backends import default_backend as defb
from cryptography.hazmat.primitives.poly1305 import Poly1305
from cryptography.hazmat.primitives.ciphers import Cipher
from cryptography.hazmat.primitives.ciphers import algorithms as algo

class ChaCha20Poly1305:

    def __init__(self, encrypt, key, nonce):
        self._encrypt = encrypt
        self._dataLength = 0
        self._aadLength = 0
        self._nonceCounter = (0).to_bytes(4, byteorder='little') + nonce
        self._nonceEncrypt = (1).to_bytes(4, byteorder='little') + nonce

        cipher = Cipher(algo.ChaCha20(key, self._nonceEncrypt), None, defb())

        if encrypt:
            self._cipher = cipher.encryptor()
        else:
            self._cipher = cipher.decryptor()

        polyKey = self.__getPolyKey(key)
        self._auth = Poly1305(polyKey)

    # Add AAD and zero pad if necessary (optional, may only be called once and before first 'update' call)
    def updateAAD(self, aad):
        self._auth.update(aad)
        self._aadLength = len(aad)
        self._auth.update(self.__getZeroBytes(self._aadLength))

    # Add ciphertext / plaintext for encryption / decryption and actualize tag
    def update(self, data):
        ctxt = self._cipher.update(data)
        self._dataLength += len(ctxt)
        if self._encrypt:
            self._auth.update(ctxt)
        else:
            self._auth.update(data)
        return ctxt

    # Complete padding and verify tag (only decryption)
    def verify_tag(self, tag=None):
        if not self._encrypt:
            self.__pad()
            if tag is None:
                raise ValueError('tag required')
            self._auth.verify(tag)
        else:
            raise ValueError('Tag verification only during decryption')

    # Complete padding and calculate tag(only encryption)
    def calculate_tag(self):
        if self._encrypt:
            self.__pad()
            return self._auth.finalize()
        else:
            raise ValueError("Tag calculation only during encryption")

    # Complete formatting: zero pad ciphertext, append AAD and ciplhertext lengths
    def __pad(self):
        self._auth.update(self.__getZeroBytes(self._dataLength))
        self._auth.update(self._aadLength.to_bytes(8, byteorder='little'))
        self._auth.update(self._dataLength.to_bytes(8, byteorder='little'))

    # Zero pad data (AAD or ciphertext)
    def __getZeroBytes(self, len):
        spareBytes = len % 16
        if (spareBytes != 0):
            length = 16 - spareBytes
            return bytes([0]) * length
        return b''

    # Derive Poly1305 key
    def __getPolyKey(self, key):
        cipher = Cipher(algo.ChaCha20(key, self._nonceCounter), None, defb())
        cipher = cipher.encryptor()
        key = cipher.update(b"\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0")
        return key




