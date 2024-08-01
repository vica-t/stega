from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding

    
class Decrypter:
    """
    Decrypter class for decrypting messages using AES encryption.

    Methods:
        - run(key, encryptedMessage): Decrypts the encrypted message using the provided key.
        - unpadMessage(paddedMessage): Unpads the decrypted message.

    Attributes:
        None.
    """

    def run(self, key, encryptedMessage):
        """
        Decrypts the encrypted message using the provided key.

        :param key: The encryption key used to decrypt the message. It should be a byte string.
        :param encryptedMessage: The encrypted message to be decrypted. It should be a byte string.
        :return: The decrypted and unpadded message as a byte string.
        """
        key = key.encode('utf-8')
        iv = b'\x00' * 16  # Initialization vector
        cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        decryptedMessage = decryptor.update(encryptedMessage) + decryptor.finalize()
        unpaddedMessage = self.unpadMessage(decryptedMessage)
        return unpaddedMessage
    
    def unpadMessage(self, paddedMessage):
        """
        Unpads a message by using the PKCS7 padding scheme.

        :param paddedMessage: The padded message to be unpadded.
        :return: The unpadded message.
        """
        unpadder = padding.PKCS7(128).unpadder()
        unpaddedData = unpadder.update(paddedMessage)
        return unpaddedData + unpadder.finalize()



'''
d = Decrypter()
with open('C:/Users/vicat/Dropbox/Vica_new/vica/computer/cyber/yud_bet/stega/backend/functionality/assets/handsome.png', 'rb') as file:
    f = file.read()

key = '5d41402abc4b2a76b9719d911017c592'

data = d.run(key, f)
#'''







