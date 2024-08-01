import secrets
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding


class Encrypter:
    """
    The Encrypter class provides methods to encrypt a message using the AES encryption algorithm.

    Methods:
        - run(message: Union[str, bytes], key: Optional[bytes]) -> Tuple[str, bytes]:
            Encrypts a message using the AES algorithm with the provided key.
            If no key is provided, a random key is generated.
            Returns a tuple containing the key and the encrypted message.

        - padMessage(message: bytes) -> bytes:
            Pads a message using PKCS7 padding.

        - generateKey() -> str:
            Generates a random key for encryption.

    """

    def run(self, message, key=None):
        """
        Encrypts the given message using the specified key.

        :param message: The message to be encrypted. It can be either a string or bytes.
        :param key: The encryption key. If not provided, a new key will be generated.
        :return: A tuple containing the encryption key (decoded as UTF-8 string) and the encrypted message as bytes.
        """
        message = str(message).encode('utf-8') if type(message) != bytes else message
        key = self.generateKey().encode('utf-8') if not key else key
        iv = b'\x00' * 16
        cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        paddedMessage = self.padMessage(message)
        encryptedMessage = encryptor.update(paddedMessage) + encryptor.finalize()
        return key.decode('utf-8'), encryptedMessage
    
    def padMessage(self, message):
        """
        Pad the given message using PKCS7 padding.

        :param message: The message to be padded.
        :return: The padded message.
        """
        padder = padding.PKCS7(128).padder()
        paddedData = padder.update(message) + padder.finalize()
        return paddedData
    
    def generateKey(self):
        """
        Generates a random key.

        :return: The generated key as a hexadecimal string.
        """
        return secrets.token_bytes(16).hex()









'''
import cProfile
e = Encrypter()
data = '10110101' * 5000
print(len(data))
data = data.encode('utf-8')
loop = asyncio.get_event_loop()
cProfile.run('loop.run_until_complete(e.run(data))')
#key, encData = e.run(data)
#cProfile.run('e.run(data)')
#print(encData)
#print('key: ' + key)
#'''






