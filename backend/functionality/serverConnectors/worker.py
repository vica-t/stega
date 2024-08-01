# inherits from server
# connected to router
# gets tasl from router
# executes task
# returns answer to router

import asyncio
import os
import sys
sys.path.append(os.path.abspath(''))
from backend.functionality.serverConnectors.absServer import AbsServer
from backend.functionality.userValidation import UserValidationController
from backend.functionality.stegaExecution import StegaInserter, StegaReader
from backend.functionality.serverConnectors.planHandle import PlanContoller
from backend.functionality.serverConnectors.emailHandle import EmailHandler


class Worker(AbsServer):
    """
    Worker class for handling tasks.

    Args:
        host (str): The hostname for the server.
        port (int): The port number for the server.

    Attributes:
        userValidation (UserValidationController): The user validation controller.
        stegaInserter (StegaInserter): The steganography inserter.
        stegaReader (StegaReader): The steganography reader.
        planController (PlanContoller): The plan controller.

    """

    def __init__(self, host, port):
        """
        :param host: The hostname or IP address of the server.
        :param port: The port number to connect to.

        """
        super().__init__(host, port)
        self.userValidation = UserValidationController()
        self.stegaInserter = StegaInserter()
        self.stegaReader = StegaReader()
        self.planController = PlanContoller()
        self.emailHandler = EmailHandler()
    
    
    
    async def handleTask(self, reader, writer, sharedKey):
        """

        handleTask(self, reader, writer, sharedKey)

        Asynchronously handles a task received from the router.

        :param reader: The reader object to receive data from the router.
        :type reader: StreamReader

        :param writer: The writer object to send data to the router.
        :type writer: StreamWriter

        :param sharedKey: The shared key used for encryption/decryption of messages.
        :type sharedKey: str

        :return: None

        """
        # get task from router
        task = await super().handleTask(reader, writer, sharedKey)
        if not task:
            return
        # run task
        answer = await self.runTask(task)
        # send answer to router
        await self.sendMessage(answer, writer, sharedKey)
    
    
    
    async def runTask(self, task):
        """
        :param task: A dictionary representing the task to be executed. It should contain two keys: 'action' and 'data'. 'action' represents the name of the method to be called, and 'data' represents the data to be passed to the method.
        :return: The result of the task execution. If the task is invalid or the execution fails, None is returned.

        This method is responsible for running a task asynchronously. It checks if the task is valid by verifying if it contains the necessary keys. If the task is invalid, None is returned. Otherwise, the method retrieves the corresponding action method using getattr(). The retrieved method is then executed asynchronously using asyncio.to_thread(), passing the 'data' as an argument. Finally, the result of the action method execution is returned.
        """
        # check if valid task
        try:
            action = task['action']
            data = task['data']
        except:
            return None
        if not self.validTask(action, data):
            return None

        func = getattr(self, action)
        result = await asyncio.to_thread(func, data)
        return result
    
    
    
    # login
    def login(self, data):
        """
        Login method for user authentication.

        :param data: A dictionary containing the username and password.
        :type data: dict
        :return: A tuple consisting of the success status, usernameHash, and currentPlan.
                 Returns None if login is unsuccessful or if no currentPlan is found.
        :rtype: tuple or None
        """
        # success, usernameHash
        success, usernameHash, verEmail = self.userValidation.login(data['username'], data['password'])
        if not success:
            return None
        currentPlan = self.planController.getCurrentPlan(usernameHash)
        if currentPlan == False and isinstance(currentPlan, bool):
            return None
        return success, usernameHash, verEmail, currentPlan
    
    
    # signup
    def signup(self, data):
        """
        :param data: a dictionary containing user signup data
            - 'username': a string representing the username of the user
            - 'password': a string representing the password of the user
            - 'confirmPassword': a string representing the confirmed password of the user
        :return: a tuple containing the signup result
            - success: a boolean indicating whether the signup was successful or not
            - usernameHash: a string representing the hashed username
            - errorCode: an integer representing the error code (-1 if no error)
        """
        # success, usernameHash
        result = self.userValidation.signup(data['username'], data['password'], data['confirmPassword'])
        if not result:
            return result
        result = result[0], result[1], result[2], -1
        return result
    
    
    # insert
    def insert(self, data):
        """
        Insert data into a medium file using steganography.

        :param data: A dictionary containing the following keys:
                     - 'userHash' (str): The user hash.
                     - 'dataFile' (str): The data file.
                     - 'dataFileType' (str): The type of the data file.
                     - 'mediumFile' (str): The medium file.
                     - 'intendedUsersList' (list): A list of intended users.

        :return: The result of the steganography insertion, or None if the insertion fails.
        """
        # ['dataFile', 'dataFileType', 'mediumFile', 'mediumFileType', 'intendedUsersList']
        # fileBytes, fileType, metadata
        userHash = data['userHash']
        creationsLeft = self.planController.getCreationsLeft(userHash)
        if creationsLeft == -1:
            pass
        elif creationsLeft <= 0 or not creationsLeft:
            return None
        result = self.stegaInserter.run(data['dataFile'], data['dataFileType'], data['mediumFile'], data['intendedUsersList'])
        if result == -1 or result == None:
            return result
        added = self.planController.addUserCreation(userHash)
        if not added:
            return None
        return result
    
    
    # read
    def read(self, data):
        """
        Method to read data using stegaReader.

        :param data: Dictionary containing the following keys:
                     - 'modifiedFile': File containing the modified data.
                     - 'metadata': Metadata related to the modified data.
                     - 'userHash': Hash of the user.
        :return: Output of the stegaReader.run() method.
        """
        #['modifiedFile', 'modifiedFileType', 'metadata', 'userHash']
        return self.stegaReader.run(data['modifiedFile'], data['metadata'], data['userHash'])
    
    
    # verifyEmail
    def verifyEmail(self, data):
        return self.emailHandler.verifyEmail(data['userHash'], data['code'])
    
    
    # sendVerificationEmail
    def sendVerificationEmail(self, data):
        return self.emailHandler.sendVerificationEmail(data['userHash'])
    
    
    # forgotPassword
    def forgotPassword(self, data):
        email = data['email']
        # get username by email
        userHash = self.userValidation.getUserHashByEmail(email)
        if not userHash:
            return None
        # save username to table in db
        if not self.userValidation.saveUserToChangePass(userHash):
            return False
        link = 'http://127.0.0.1:5000/fpl?h=' + userHash
        if not self.emailHandler.sendPasswordChangeEmail(userHash, link):
            return False
        return userHash
    
    
    # validChangePassUser
    def validChangePassUser(self, data):
        return self.userValidation.validChangePassUser(data['userHash'])
    
    
    # changePassword
    def changePassword(self, data):
        return self.userValidation.updateUserPassword(data['userHash'], data['password'], data['confirmPassword'])
    
    
    # loadPlans
    def loadPlans(self, data):
        """
        Load plans for a user.

        :param data: A dictionary containing userHash value.
        :type data: dict
        :return: The loaded plans.
        :rtype: list
        """
        return self.planController.loadPlans(data['userHash'])
    
    
    # updatePlan
    def updatePlan(self, data):
        """
        Update the plan for a user.

        :param data: A dictionary containing the user's hash and the plan ID.
        :return: True if the plan is successfully updated, False otherwise.
        """
        return self.planController.updatePlan(data['userHash'], data['planId'])


    # getCreationsLeft
    def getCreationsLeft(self, data):
        """
        Retrieve the number of creations left for a user.

        :param data: A dictionary containing the userHash.
        :return: The number of creations left for the user.
        """
        userHash = data['userHash']
        return self.planController.getCreationsLeft(userHash)
    
    




async def start(port):
    """Starts the server on the specified port.

    :param port: The port number to start the server on.
    :return: None
    """
    w = Worker('127.0.0.1', port)
    print('start')
    await w.startServer()

async def main():
    """Starts multiple tasks asynchronously.

    :return: None
    """
    tasks = [start(8889+i) for i in range(2)]
    await asyncio.gather(*tasks)

asyncio.run(main())

