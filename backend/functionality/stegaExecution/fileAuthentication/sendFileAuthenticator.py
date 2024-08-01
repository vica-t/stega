import zlib
from backend.functionality.stegaExecution.fileAuthentication.fileAuthenticator import FileAuthenticator


class SendFileAuthenticator(FileAuthenticator):
    """
    :class:`SendFileAuthenticator` class

    This class inherits from the :class:`FileAuthenticator` class and provides methods for generating authenticators for sending files.

    Initialization
    --------------
    To initialize the :class:`SendFileAuthenticator` object, use the following code:

        authenticator = SendFileAuthenticator()

    Methods
    -------
    The :class:`SendFileAuthenticator` class provides the following methods:

    """

    def __init__(self):
        """
        Initializes a new instance of the class.

        :param self: The current object instance.
        """
        pass
    
    
    
    def generateAuthenticator(self, aesKey, intendedUserHashList, additionalData, reedSolomonAdditionalData):
        """
        :param aesKey: A string representing the AES key. The length should be 32 characters.
        :param intendedUserHashList: A list of up to 3 strings, representing the intended user hash list.
        :param additionalData: A string representing additional data generated when inserting data into file.
        :param reedSolomonAdditionalData: An additional Reed-Solomon data to be appended to the authenticator.
        :return: The generated authenticator.

        The method generates an authenticator using the given AES key, intended user hash list, additional data, and Reed-Solomon additional data.

        Each user in the intended user hash list is processed to generate an authenticator using the `generateAuthenticatorForUser` method. The resulting authenticators are stored in a list.

        The full authenticator is obtained by calling `getFullAuthenticatorWithUserAuthenticators` method with the user authenticators list and additional data as arguments.

        Finally, the authenticator is appended with the Reed-Solomon additional data and returned.
        """

        # aesKey - string, 32
        # intendedUserHashList - up to 3, list of strings
        # additionalData - string, bitmap
        #
        # get the hash
        # hash(aesKey.intendedUserHash.additionalData)
        # how many users + compressed additional data + hash&key for each user
        #
        userAuthenticators = []
        for user in intendedUserHashList:
            auth = self.generateAuthenticatorForUser(aesKey, user, additionalData)
            userAuthenticators.append(auth)
        authenticator = self.getFullAuthenticatorWithUserAuthenticators(userAuthenticators, additionalData, reedSolomonAdditionalData)
        return authenticator
    
    
    def generateAuthenticatorForUser(self, aesKey, intendedUserHash, additionalData):
        """
        Generate an authenticator for a user based on the provided parameters.

        :param aesKey: The AES key used for encryption.
        :param intendedUserHash: The hash of the intended user.
        :param additionalData: Additional data to be included in the authenticator.
        :return: The generated authenticator.

        """
        # raw hash
        rawAuth = self.generateRawAuthenticator(aesKey, intendedUserHash, additionalData)
        # insert key
        auth = self.insertKeyIntoRawAuthenticator(rawAuth, aesKey)
        return auth
        
    def insertKeyIntoRawAuthenticator(self, rawAuthenticator, aesKey):
        """
        Inserts AES key into raw authenticator.

        :param rawAuthenticator: The raw authenticator string.
        :param aesKey: The AES key string.
        :return: The modified authenticator string.
        """
        authenticator = ''
        for i in range(32):
            authenticator += rawAuthenticator[i*2]
            authenticator += rawAuthenticator[i*2+1]
            authenticator += aesKey[i]
        return authenticator
    

    def getFullAuthenticatorWithUserAuthenticators(self, userAuthenticators, additionalData, reedSolomonAdditionalData):
        """
        Builds a full authenticator string combining the user authenticators and additional data.

        :param userAuthenticators: A list of user authenticators.
        :type userAuthenticators: list[str]
        :param additionalData: Additional data to be included in the authenticator.
        :type additionalData: str
        :param reedSolomonAdditionalData: An additional Reed-Solomon data to be appended to the authenticator.
        :type reedSolomonAdditionalData: str
        :return: The full authenticator string.
        :rtype: str
        """
        compressedAdditionalData = self.compressString(additionalData)
        auth = str(len(userAuthenticators)) + compressedAdditionalData
        for userAuth in userAuthenticators:
            auth += userAuth
        auth += reedSolomonAdditionalData
        return auth
    
    def compressString(self, strToCompress):
        """
        Compresses the given string using zlib compression.

        :param strToCompress: The string to compress.
        :type strToCompress: str
        :return: The compressed string in hexadecimal representation.
        :rtype: str
        """
        # Encode the string to bytes
        strBytes = strToCompress.encode('utf-8')
        # Compress the bytes
        compressedBytes = zlib.compress(strBytes)
        # Encode the compressed bytes to base64 for readability
        compressedStr = compressedBytes.hex()
        return compressedStr




