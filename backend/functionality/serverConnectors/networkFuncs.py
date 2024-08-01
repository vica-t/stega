from abc import ABC
import hashlib
import configparser
import pickle
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from Crypto.Cipher import AES
import os


class NetworkFuncs(ABC):
    """
        This class provides network functions for communication with a server.

        Attributes:
            taskFormats (dict): A dictionary containing the format of different tasks.

        Methods:
            validTask(action, taskData)
            getMessageToSend(data, sharedKey=None)
            validMessage(message)
            generateChecksum(data)
            generateHash(strToHash)
            validChecksum(data, checksum)
            getSalt()
            generateAuthAnswer(authMessage)
            getAuthSalt()
            sendMessage(message, writer, sharedKey=None)
            printMessage(messageToPrint)
            getMessage(reader, sharedKey=None)
            handleReceivedMessage(message, sharedKey)
    """
    def __init__(self):
        self.taskFormats = {
            'login' : ['username', 'password'],
            'signup' : ['userame', 'password','confirmPassword'],
            'verifyEmail' : ['userHash', 'code'],
            'sendVerificationEmail' : ['userHash'],
            'forgotPassword' : ['email'],
            'validChangePassUser' : ['userHash'],
            'changePassword' : ['userHash', 'password', 'confirmPassword'],
            'updatePlan' : ['userHash', 'planId'],
            'loadPlans' : ['userHash'],
            'getCreationsLeft' : ['userHash'],
            'insert' : ['dataFile', 'dataFileType', 'mediumFile', 'intendedUsersList', 'userHash'],
            'read' : ['modifiedFile', 'metadata', 'userHash']
        }

    
    def validTask(self, action, taskData):
        """
        Check if the task is valid for the given action.

        :param action: The action to validate against.
        :type action: str
        :param taskData: The data for the task.
        :type taskData: dict
        :return: True if the task is valid, False otherwise.
        :rtype: bool
        """
        try:
            # check if action in actions
            if action not in list(self.taskFormats.keys()):
                return False
            # check if keys of data in action
            dataKeys = list(taskData.keys()).sort()
            taskKeys = self.taskFormats[action].sort()
            return dataKeys == taskKeys
        except:
            return False
    
    
    
    
    async def getMessageToSend(self, data, sharedKey = None):
        """
        Returns a message with encoded data and checksum.

        :param data: The data to be encoded.
        :type data: object
        :param sharedKey: The shared key used for encoding the data (optional).
        :type sharedKey: str
        :return: A message dictionary containing the encoded data and checksum.
        :rtype: dict
        """
        # encode data
        if sharedKey:
            encData = await self.encodeData(sharedKey, data)
        else:
            encData = data
        # crc of enc data
        checksum = self.generateChecksum(encData)
        message = {'data' : encData, 'checksum' : checksum}
        return message
    
    
    def validMessage(self, message):
        """
        Check if the message is valid.

        :param message: dictionary representing a message with keys 'data' and 'checksum'
        :return: True if the message is valid, False otherwise
        """
        try:
            messageKeys = list(message.keys())
            supposedKeys = ['data', 'checksum']
            if messageKeys.sort() != supposedKeys.sort():
                return False
            return self.validChecksum(message['data'], message['checksum'])
        except:
            return False
    
    
    def generateChecksum(self, data):
        """
        Generate a SHA256 checksum for the given data.

        :param data: The data to generate the checksum for.
        :return: The SHA256 checksum string.
        """
        data = str(data)
        data += self.getSalt()
        sha256Hash = self.generateHash(data)
        return sha256Hash
    
    def generateHash(self, strToHash):
        """
        Generate a SHA256 hash for the given string.

        :param strToHash: The string to be hashed.
        :return: The SHA256 hash of the input string.
        """
        sha256Hash = hashlib.sha256(strToHash.encode()).hexdigest()
        return sha256Hash
    
    def validChecksum(self, data, checksum):
        """
        Validates if the checksum of the data matches the given checksum.

        :param data: The data to calculate the checksum.
        :param checksum: The expected checksum to compare with the calculated data checksum.
        :return: True if the dataChecksum is equal to the checksum, False otherwise.
        """
        dataChecksum = self.generateChecksum(data)
        return dataChecksum == checksum
    
    def getSalt(self):
        """
        Get the salt value used for checksum calculation.

        :return: The salt value used for checksum calculation.
        """
        config = configparser.ConfigParser()
        dirPath = os.path.dirname(os.path.realpath(__file__))
        configFilePath = os.path.join(dirPath, "../../config.ini")
        configFilePath = os.path.abspath(configFilePath)
        config.read(configFilePath)
        return config['COMMUNICATION']['checksumSalt']
    
    
    def generateAuthAnswer(self, authMessage):
        """
        Generates an authentication answer by reversing the given authentication message,
        adding a salt, and hashing the result.

        :param authMessage: The authentication message.
        :return: The authentication answer.
        """
        # reverse
        answer = authMessage[::-1]
        # add salt
        answer += self.getAuthSalt()
        # hash
        hashAnswer = self.generateHash(answer)
        return hashAnswer
    
    def getAuthSalt(self):
        """
        Retrieves the authentication salt from the configuration file.

        :return: The authentication salt string from the configuration file.
        """
        config = configparser.ConfigParser()
        dirPath = os.path.dirname(os.path.realpath(__file__))
        configFilePath = os.path.join(dirPath, "../../config.ini")
        configFilePath = os.path.abspath(configFilePath)
        config.read(configFilePath)
        return config['COMMUNICATION']['authSalt']
    
    
    
    async def sendMessage(self, message, writer, sharedKey=None):
        """
        Send a message over a network connection established using asyncio

        :param message: The message to be sent.
        :param writer: The writer object used to send the message.
        :param sharedKey: The shared key used for encryption. Default is None.
        :return: Returns True if the message was successfully sent, otherwise returns False.

        """
        print()

        try:
            messageToPrint = message
            message = await self.getMessageToSend(message, sharedKey)
            pickleMessage = pickle.dumps(message)
            messageLen = str(len(pickleMessage)).zfill(16)
            messageLen = messageLen.encode()
            messageToSend = messageLen + pickleMessage
            writer.write(messageToSend)
            await writer.drain()
            print(f'>> Sent message: {self.printMessage(messageToPrint)}')
            return True
        except Exception as e:
            print(f'>> Failed to send message: {messageToPrint}, error: {e}')
            return False
    
    def printMessage(self, messageToPrint):
        """
        :param messageToPrint: The message to be printed.
        :return: The processed message.
        """
        return 'message'
        if not isinstance(messageToPrint, dict):
            if isinstance(messageToPrint, list):
                messageToPrint = [str(i)[:20] for i in messageToPrint]
            try:
                return messageToPrint[:50]
            except:
                return messageToPrint
        return list(messageToPrint.keys())
        dictToPrint = {}
        for key, value in messageToPrint.items():
            if isinstance(value, dict):
                value = list(value.keys())
            else:
                try:
                    value = value[:50]
                except:
                    pass
            dictToPrint[key] = value
        return dictToPrint


    async def getMessage(self, reader, sharedKey=None):
        """
        :param reader: The reader object from which to receive the message.
        :param sharedKey: The shared key to use for decrypting the message. Default is None.
        :return: The decrypted message as data.
        """
        print()

        messageLen = await reader.read(16)

        if not messageLen or messageLen == b'':
            print("<< Failed to receive message")
            return None
        try:
            messageLen = int(messageLen.decode())
        except:
            print("<< Failed to receive message")
            return None

        message = []
        bufferSize = 4096
        while messageLen > 0:
            chunkSize = min(bufferSize, messageLen)
            chunk = await reader.read(chunkSize)
            if not chunk or chunk == b'':
                print("<< Failed to receive message")
                return None
            message.append(chunk)
            messageLen -= len(chunk)
        message = b''.join(message)
        data = await self.handleReceivedMessage(message, sharedKey)
        print(f"<< Received message: {self.printMessage(data)}")
        return data
        
    async def handleReceivedMessage(self, message, sharedKey):
        """
        :param message: The received message in serialized form (bytes)
        :param sharedKey: The shared key used for decoding the data (optional)
        :return: The decoded data or None if there were any errors during processing

        """
        try:
            message = pickle.loads(message)
        except Exception as e:
            print('couldnt pickle loads data')
            return None

        validChecksum = self.validMessage(message)
        if not validChecksum:
            print('not valid checksum')
            return None

        try:
            data = message['data']
        except:
            print('couldnt get message["data"]')
            return None
        if sharedKey:
            print('trying to decode')
            data = await self.decodeData(sharedKey, data)
            print('decoded data')
        return data
    

    
    async def getPrivateKeyAndPublicKeyBytes(self):
        """
        Generate private and public key bytes using the SECP256R1 elliptic curve.

        :return: A tuple containing the private key object and the public key bytes.
                 If an exception occurs during the generation process, it returns (None, None).
        """
        try:
            privateKey = ec.generate_private_key(ec.SECP256R1(), default_backend())
            publicKeyBytes = privateKey.public_key().public_bytes(encoding=serialization.Encoding.PEM, format=serialization.PublicFormat.SubjectPublicKeyInfo)
            return privateKey, publicKeyBytes
        except:
            return None, None
    
    async def getPublicKeyFromBytes(self, publicKeyBytes):
        """
        :param publicKeyBytes: bytes containing the public key in PEM format
        :return: the public key as an instance of `cryptography.hazmat.primitives.asymmetric.rsa.RSAPublicKey` or `None` if an error occurred
        """
        try:
            publicKey = serialization.load_pem_public_key(publicKeyBytes, backend=default_backend())
            return publicKey
        except:
            return None
    
    async def getSharedKey(self, privateKey, otherKey):
        """
        :param privateKey: The private key to be used for key exchange.
        :type privateKey: `ECDHPrivateKey`
        :param otherKey: The public key of the other party for key exchange.
        :type otherKey: `ECDHPublicKey`
        :return: The derived shared key.
        :rtype: `bytes` or `None`
        """
        try:
            sharedKey = privateKey.exchange(ec.ECDH(), otherKey)
            sharedKey = HKDF(
                algorithm=hashes.SHA256(),
                length=32,
                salt=None,
                info=b'ecdh_shared_key',
                backend=default_backend()
            ).derive(sharedKey)
            return sharedKey
        except:
            return None
    
    
    async def encodeData(self, sharedKey, data):
        """
        Encrypts the given data using AES encryption with the provided shared key.

        :param sharedKey: The shared encryption key.
        :type sharedKey: bytes
        :param data: The data to be encrypted.
        :type data: any
        :return: The encrypted data.
        :rtype: bytes
        """
        data = pickle.dumps(data)
        nonce = os.urandom(16)
        cipher = AES.new(sharedKey, AES.MODE_GCM, nonce=nonce)
        encData, tag = cipher.encrypt_and_digest(data)
        return nonce + tag + encData
    
    async def decodeData(self, sharedKey, data):
        """
        Decrypts and decodes data using AES encryption with GCM mode.

        :param sharedKey: The shared key used for encryption. Must be a bytes object.
        :param data: The encrypted data to be decoded. Must be a bytes object.
        :return: The decoded data as a Python object. Returns None if decryption fails.
        """
        try:
            nonce = data[:16]
            tag = data[16:32]
            encData = data[32:]
            cipher = AES.new(sharedKey, AES.MODE_GCM, nonce=nonce)
            decData = cipher.decrypt_and_verify(encData, tag)
            decData = pickle.loads(decData)
            return decData
        except Exception as e:
            return None
