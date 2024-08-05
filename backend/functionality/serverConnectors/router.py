# inherits from server
# has client objects for each worker
# recieves task as server
# sends to one of the workers the task
# gets answer back
# sends answer to waiter


import asyncio
import os
import sys
sys.path.append(os.path.abspath(''))
from backend.functionality.serverConnectors.absServer import AbsServer
from backend.functionality.serverConnectors.absClient import AbsClient as Client


class Router(AbsServer):
    """
    Initialize the Router object.
    """

    def __init__(self):
        """
        Initializes an instance of the class.

        :param self: The current object.
        :return: None
        """
        super().__init__('127.0.0.1', 8888) # the port im sitting on
        #self.workerAddrs = [('127.0.0.1', 8889), ('127.0.0.1', 8890), ('127.0.0.1', 8891)] # the ports the workers are sitting on
        self.workersInfo = {('127.0.0.1', 8889):0, ('127.0.0.1', 8890):0, ('127.0.0.1', 8891):0}
        self.workersInfoLock = asyncio.Lock()
    
    
    
    
    async def handleTask(self, reader, writer, sharedKey):
        """
        :param reader: The reader object to receive data from the client.
        :param writer: The writer object to send data to the client.
        :param sharedKey: The shared key used for encryption and decryption.
        :return: None

        This method handles a task received from a client. It first retrieves the task using the super class's handleTask method. If the task is received successfully, it redirects it to a worker using the redirectTaskToWorker method. Finally, it sends the answer received from the worker back to the client using the sendMessage method.
        """
        # get task from waiter
        message = await super().handleTask(reader, writer, sharedKey)
        if not message:
            print('couldnt get the task from super handle task')
            return
        print('got the task')
        # send task to worker
        print('redirecting to worker')
        answer = await self.redirectTaskToWorker(message)
        # send answer to waiter
        await self.sendMessage(answer, writer, sharedKey)
    
    
    
    async def redirectTaskToWorker(self, task):
        """
        Redirects a task to a worker.

        :param task: The task to be redirected.
        :return: The answer to the task, or None if the task could not be completed.
        """
        failedToConnectWorkers = []
        answerToReturn = None
        while len(failedToConnectWorkers) < len(self.workersInfo) or len(failedToConnectWorkers) < 5:
            print('sending to worker')
            # choose which worker to connect to
            workerHost, workerPort = await self.getWorkerAddrToConnect(failedToConnectWorkers)
            # run client
            answer, isActualAnswer = await self.runClient(workerHost, workerPort, task)
            if isActualAnswer:
                answerToReturn = answer
                break
            else:
                failedToConnectWorkers.append((workerHost, workerPort))
        return answerToReturn

    
    async def getWorkerAddrToConnect(self, failedToConnectWorkers):
        """
        Find a worker (from a set of workers) with the minimum number of active connections.

        :param failedToConnectWorkers: A list of worker addresses that failed to connect
        :return: The worker address with the fewest connections in the current workersInfo dictionary

        """
        async with self.workersInfoLock:
            # copy dict and remove failed connections
            workersInfo = self.workersInfo.copy()
            for failed in failedToConnectWorkers:
                workersInfo.pop(failed)
            # get values
            workersConnectionCount = list(workersInfo.values())
            # find minimum
            sortedWorkersConnectionCount = workersConnectionCount.copy()
            sortedWorkersConnectionCount.sort()
            minConnections = sortedWorkersConnectionCount[0]
            # find index of minimum
            indexOfMinConnections = workersConnectionCount.index(minConnections)
            # get keys
            workerAddrs = list(workersInfo.keys())
            # get key in index
            workerAddr = workerAddrs[indexOfMinConnections]
            return workerAddr

    
    async def runClient(self, workerHost, workerPort, task):
        """
        Run a client to execute a task on a worker.

        :param workerHost: The host of the worker.
        :param workerPort: The port of the worker.
        :param task: The task to execute on the worker.
        :return: The answer returned by the worker.
        """
        async with self.workersInfoLock:
            self.workersInfo[(workerHost, workerPort)] += 1
        client = Client(workerHost, workerPort)
        answer = await client.runClient(task)
        async with self.workersInfoLock:
            self.workersInfo[(workerHost, workerPort)] -= 1
        return answer



async def main():
    """
    The `main` method is an asynchronous method that serves as the entry point for the program.

    :return: None
    """
    r = Router()
    print('start')
    await r.startServer()


asyncio.run(main())


