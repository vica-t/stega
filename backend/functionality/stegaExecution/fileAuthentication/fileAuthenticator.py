import os
import hashlib
import configparser
from abc import ABC


class FileAuthenticator(ABC):
    """
    FileAuthenticator Class
    =======================
    This class provides methods to generate authenticators using SHA256 hashing.

    Methods:
    --------
    generateRawAuthenticator(aesKey, intendedUserHash, additionalData)
        Generates a raw authenticator string based on input parameters.

    generateSha256Hash(strToHash)
        Generates a SHA256 hash string based on input string.

    getSalt()
        Retrieves the salt value from the configuration file.

    """

    def generateRawAuthenticator(self, aesKey, intendedUserHash, additionalData):
        """
        Generates a raw authenticator string using provided parameters.

        :param aesKey: The AES key.
        :param intendedUserHash: The hash of the intended user.
        :param additionalData: Additional data to include in the authenticator.
        :return: The generated authenticator hash.
        """
        salt = self.getSalt()
        authString = aesKey + '.' + intendedUserHash + '.' + additionalData + '.' + salt
        authHash = self.generateSha256Hash(authString)
        return authHash
    
    def generateSha256Hash(self, strToHash):
        """
        :param strToHash: The string to hash using SHA-256.
        :return: The hexadecimal representation of the SHA-256 hash of the input string.
        """
        bytesToHash = strToHash.encode('utf-8')
        hashStr = hashlib.sha256()
        hashStr.update(bytesToHash)
        hashStr = hashStr.hexdigest()
        return hashStr
    
    def getSalt(self):
        """Reads the salt value from the config file.

        :return: The salt value from the config file.
        """
        config = configparser.ConfigParser()
        dirPath = os.path.dirname(os.path.realpath(__file__))
        configFilePath = os.path.join(dirPath, "../../../config.ini")
        configFilePath = os.path.abspath(configFilePath)
        config.read(configFilePath)
        salt = config['FILE_AUTHENTICATION']['salt']
        return salt




