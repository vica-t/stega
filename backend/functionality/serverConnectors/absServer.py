import asyncio
import time
import random
import os
import sys
sys.path.append(os.path.abspath(''))
from backend.functionality.serverConnectors.networkFuncs import NetworkFuncs
import tracemalloc
tracemalloc.start()


class AbsServer(NetworkFuncs):
    """
    AbsServer class for handling network server functionality.

    This class inherits from NetworkFuncs.

    Attributes:
        host (str): The host address of the server.
        port (int): The port number of the server.

    Methods:
        __init__(host, port): Initializes the AbsServer object.
        startServer(): Starts the server.
        handleClient(reader, writer): Handles the client connection.
        asyncHandleClient(reader, writer): Asynchronously handles the client connection.
        handleTask(reader, writer, sharedKey): Handles the task from the client.
        disconnectClient(writer): Disconnects the client.
        handleFirstConnection(reader, writer): Handles the first connection with the client.
        runAuthMessage(reader, writer): Runs the authentication message exchange with the client.
        dhExchange(reader, writer): Performs the Diffie-Hellman key exchange with the client.
        runConfirmAuthMessage(writer, sharedKey): Runs the confirmation authentication message exchange with the client.

    """
    def __init__(self, host, port):
        """
        Initializes a new instance of the class.

        :param host: The hostname or IP address of the server.
        :type host: str
        :param port: The port number for the server.
        :type port: int
        """
        super().__init__()
        self.host = host
        self.port = port
    
    
    
    
    async def startServer(self):
        """
        Starts the server to accept clients.

        :return: None
        """
        server = await asyncio.start_server(self.handleClient, self.host, self.port)
        async with server:
            print(f"Server started on {self.host}:{self.port}")
            await server.serve_forever()
    
    
    
    async def handleClient(self, reader, writer):
        """
        Handle a client connection.

        :param reader: The reader object for the client connection.
        :type reader: asyncio.StreamReader
        :param writer: The writer object for the client connection.
        :type writer: asyncio.StreamWriter

        :return: None
        :rtype: None

        """
        asyncio.create_task(self.asyncHandleClient(reader, writer))
    
    async def asyncHandleClient(self, reader, writer):
        """
        Handles a client connection asynchronously.

        :param reader: The StreamReader object for receiving data from the client.
        :param writer: The StreamWriter object for sending data to the client.
        :return: None
        """
        try:
            sharedKey = await self.handleFirstConnection(reader, writer)
            if not sharedKey:
                print('first connection failed')
                return
            print('first connection done')
            await self.handleTask(reader, writer, sharedKey)
        finally:
            await self.disconnectClient(writer)
    
    
    async def handleTask(self, reader, writer, sharedKey):
        """
        Handle task.

        :param reader: The reader object for receiving data from the client.
        :param writer: The writer object for sending data to the client.
        :param sharedKey: The shared key used for data encryption.

        :return: The message received from the client.
        """
        # get task from waiter
        message = await self.getMessage(reader, sharedKey)
        return message
    
    async def disconnectClient(self, writer):
        """
        Disconnects a client by closing the writer connection.

        :param writer: the writer object representing the connection
        :return: None
        """
        try:
            writer.close()
            await writer.wait_closed()
        except:
            pass
        print('disconnected client')
    
    
    
    async def handleFirstConnection(self, reader, writer):
        """
        Handles the first connection with a client.

        :param reader: The StreamReader object used to read data from the client.
        :param writer: The StreamWriter object used to write data to the client.
        :return: The shared key used for encryption, or None if the authentication or key exchange fails.
        """
        try:
            # get auth
            validAuth = await self.runAuthMessage(reader, writer)
            if not validAuth:
                return None
            # exchange keys
            sharedKey = await self.dhExchange(reader, writer)
            if not sharedKey:
                return None
            # confirm auth
            validConfirm = await self.runConfirmAuthMessage(writer, sharedKey)
            if not validConfirm:
                return None
            return sharedKey
        except:
            return None
    
    
    async def runAuthMessage(self, reader, writer):
        """

        :param reader: An object representing the reader used to receive messages.
        :param writer: An object representing the writer used to send messages.
        :return: Returns True if the received message matches the generated authentication answer, False otherwise.

        """
        # send random
        randMessage = str(time.time()) + str(random.randint(0, 100000))
        randMessage = randMessage[:22]
        sent = await self.sendMessage(randMessage, writer)
        if not sent:
            return False
        # recieve message
        answer = await self.getMessage(reader)
        if not answer:
            return False
        # check
        supposedAnswer = self.generateAuthAnswer(randMessage)
        return answer == supposedAnswer
    
    async def dhExchange(self, reader, writer):
        """
        Exchange Diffie-Hellman key with the client.

        :param reader: StreamReader object for receiving messages from the client.
        :param writer: StreamWriter object for sending messages to the client.
        :return: The shared key generated from the Diffie-Hellman key exchange, or None if the key exchange fails.

        """
        privateKey, publicKeyBytes = await self.getPrivateKeyAndPublicKeyBytes()
        if not privateKey:
            return None
        await self.sendMessage(publicKeyBytes, writer)
        clientPublicKeyBytes = await self.getMessage(reader)
        if clientPublicKeyBytes == None:
            return None
        clientPublicKey = await self.getPublicKeyFromBytes(clientPublicKeyBytes)
        if not clientPublicKey:
            return None
        sharedKey = await self.getSharedKey(privateKey, clientPublicKey)
        return sharedKey
    
    async def runConfirmAuthMessage(self, writer, sharedKey):
        """
        :param writer: The writer object representing the connection to the client.
        :type writer: asyncio.StreamWriter

        :param sharedKey: The shared key used for encryption/decryption of messages.
        :type sharedKey: str

        :return: A boolean indicating whether the encoded message was successfully sent.
        :rtype: bool
        """
        # send encoded confirmation
        sent = await self.sendMessage('connected', writer, sharedKey)
        return sent
    
