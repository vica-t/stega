import os
import sys
sys.path.append(os.path.abspath(''))
from backend.functionality.serverConnectors.absClient import AbsClient as Client


class Waiter:
    """
    :class: Waiter

    The `Waiter` class represents a waiter who can perform tasks by sending requests to a server using a client.

    Attributes:
        host (str): The IP address of the server.
        port (int): The port number of the server.

    Methods:
        runTask: Performs the given action with the provided data by calling the `runClient` method.
        runClient: Sends a request to the server using a client and returns the response.

    """
    def __init__(self):
        self.host = '127.0.0.1'
        self.port = 8888
    

    
    async def runTask(self, action, data):
        """
        :param action: The action to be performed.
        :param data: Additional data to be sent with the action.
        :return: The answer received after running the task.

        This method is used to run a task asynchronously. It takes in an action and additional data, and returns the answer received after running the task.
        """
        answer = await self.runClient(action, data)
        # handle here if got None or check if valid idk
        return answer
    
    
    
    async def runClient(self, action, data):
        """
        :param action: The action to be performed by the client.
        :param data: The data related to the action.
        :return: The result obtained from the server.
        """
        task = {'action':action, 'data':data}
        client = Client(self.host, self.port)
        answer, _ = await client.runClient(task)
        return answer

