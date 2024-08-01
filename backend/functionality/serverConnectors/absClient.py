import asyncio
import os
import sys
sys.path.append(os.path.abspath(''))
from backend.functionality.serverConnectors.networkFuncs import NetworkFuncs


class AbsClient(NetworkFuncs):
    """
    AbsClient

    This class is a client for a network communication. It provides methods for establishing a connection to a server, exchanging encryption keys, authenticating the client, and sending and receiving messages.

    Methods:
        - __init__(host, port)
            Initializes the AbsClient instance with the specified host and port.

        - runClient(task)
            Runs the client with the given task. It performs the following steps:
                - Checks if the task is valid.
                - Connects to the server.
                - Handles the first connection, including authentication and key exchange.
                - Sends the task message.
                - Waits for and returns the response from the server.

        - connectToServer()
            Establishes a connection to the server using the specified host and port.

        - disconnectFromServer()
            Closes the connection to the server.

        - handleFirstConnection()
            Handles the first connection to the server, including authentication and key exchange.

        - runAuthMessage()
            Runs the authentication message exchange with the server. It performs the following steps:
                - Receives the authentication challenge.
                - Generates the authentication answer.
                - Sends the authentication answer to the server.

        - dhExchange()
            Performs the Diffie-Hellman key exchange with the server. It generates a private key, receives the server's public key, sends the client's public key, and computes the shared key.

        - runAuthConfirm()
            Runs the authentication confirmation step. It receives the encrypted 'connected' message from the server, decodes and checks it, and returns 'True' if the message is 'connected'.

        - sendMessage(message)
            Sends the specified message to the server, encrypting it using the shared key.

        - getMessage()
            Receives a message from the server, decrypting it using the shared key.

    Attributes:
        - host
            The host to connect to.

        - port
            The port to connect to.

        - reader
            The reader object for receiving data from the server.

        - writer
            The writer object for sending data to the server.

        - sharedKey
            The shared encryption key.

        - connected
            Flag indicating whether the client is connected to the server.
    """
    def __init__(self, host, port):
        """
        Initialize the object with the given host and port.

        :param host: The host of the connection.
        :type host: str
        :param port: The port of the connection.
        :type port: int
        """
        super().__init__()
        self.host = host
        self.port = port
        self.reader = None
        self.writer = None
        self.sharedKey = None
        self.connected = False


    
        
    async def runClient(self, task):
        """

        Runs the client to perform a given task.

        :param task: A dictionary representing the task to be performed by the client. The dictionary should contain the following keys:
                     - 'action': The action to be performed.
                     - 'data': The data associated with the action.
        :return: A tuple containing the result of the task execution and a boolean indicating whether the task was executed successfully or not.
                 - If the task is executed successfully, the result of the task will be returned as the first element of the tuple,
                   and the boolean value will be True as the second element.
                 - If the task cannot be executed successfully, None will be returned as the first element of the tuple,
                   and the boolean value will be False as the second element.

        """
        try:
            print('Client started')
            # valid task
            validTask = self.validTask(task['action'], task['data'])
            if not validTask:
                print('Not valid task')
                return None, False

            # connection to server
            connected = await self.connectToServer()
            if not connected:
                print('Couldn\'t connect to server')
                return False, False

            # first connection
            firstConnection = await self.handleFirstConnection()
            if not firstConnection:
                print('First connection failed')
                return None, False

            # task
            sent = await self.sendMessage(task)
            if not sent:
                return None, False
            answer = await self.getMessage()
            return answer, True
        except:
            return None, False
        finally:
            await self.disconnectFromServer()
    
    
    
    async def connectToServer(self):
        """
        Connects to a server using asyncio.

        :return: Returns True if connection is successful, False otherwise.
        """
        try:
            self.reader, self.writer = await asyncio.open_connection(self.host, self.port)
            self.connected = True
            return True
        except:
            return False
    
    async def disconnectFromServer(self):
        """
        Disconnects from the server.

        :return: None
        """
        if self.connected:
            try:
                self.writer.close()
                await self.writer.wait_closed()
            except:
                pass
            self.reader = None
            self.writer = None
            self.connected = False
            print('Disconnected from server')
    
    
    
    async def handleFirstConnection(self):
        """
        Handle the first connection by performing the authentication, Diffie-Hellman exchange,
        and authentication confirmation.

        :return: True if all steps are successful, False otherwise.
        """
        # auth
        success = await self.runAuthMessage()
        if not success:
            return False
        # dhExchange
        success = await self.dhExchange()
        if not success:
            return False
        # auth confirm
        success = await self.runAuthConfirm()
        if not success:
            pass
        return success
    
    
    async def runAuthMessage(self):
        """
        Run the authentication message.

        :return: True if the authentication message is successfully sent, False otherwise.
        """
        # get challenge
        authMessage = await self.getMessage()
        if not authMessage:
            return False
        # generate answer
        authAnswer = self.generateAuthAnswer(authMessage)
        # send answer
        sent = await self.sendMessage(authAnswer)
        return sent
    
    async def dhExchange(self):
        """
        Performs a Diffie-Hellman key exchange.

        :return: True if the key exchange was successful, False otherwise.

        """
        privateKey, publicKeyBytes = await self.getPrivateKeyAndPublicKeyBytes()
        if not privateKey:
            return False
        serverPublicKeyBytes = await self.getMessage()
        if serverPublicKeyBytes == None:
            return False
        sent = await self.sendMessage(publicKeyBytes)
        if not sent:
            return False
        serverPublicKey = await self.getPublicKeyFromBytes(serverPublicKeyBytes)
        if not serverPublicKey:
            return False
        sharedKey = await self.getSharedKey(privateKey, serverPublicKey)
        self.sharedKey = sharedKey
        return True
    
    async def runAuthConfirm(self):
        """
        Runs the authorization confirmation process.

        :return: True if the authorization is confirmed, False otherwise.
        """
        # get enc 'connected' from server
        authConfirm = await self.getMessage()
        if not authConfirm:
            return False
        # decode and check
        if authConfirm != 'connected':
            return False
        # return enc 'accepted'
        return True
    
    
    
    async def sendMessage(self, message):
        """
        Sends a message using the writer and shared key.

        :param message: The message to be sent.
        :return: A coroutine that sends the message.
        """
        return await super().sendMessage(message, self.writer, self.sharedKey)
    
    async def getMessage(self):
        """
        Retrieves a message from the absClient.

        :return: The retrieved message.
        """
        #print('waiting to get message in absClient getMessage')
        return await super().getMessage(self.reader, self.sharedKey)
