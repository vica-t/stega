import os
import sys
sys.path.append(os.path.abspath(''))
from backend.functionality.database import DatabaseHandler


class PlanRepository:
    def __init__(self):
        self.dbHandler = DatabaseHandler()
    
    
    
    def getAllPlans(self):
        """
        Retrieves all plans from the database.

        :return: A list containing all the plans.
        """
        result = self.dbHandler.selectAll('plans')
        return result
    
    
    def getCurrentPlanIdByUserHash(self, userHash):
        """
        Retrieves the current plan id for a user based on their user hash.

        :param userHash: The user hash to search for.
        :return: The current plan id associated with the user.
        """
        result = self.dbHandler.select('users', ['planId'], 'username', '=', userHash)
        return result
    
    
    def updatePlanForUser(self, userHash, planId):
        """
        Update the plan for a user.

        :param userHash: The hash value of the user's username.
        :param planId: The ID of the new plan.
        :return: True if the plan is successfully updated, False otherwise.
        """
        result = self.dbHandler.update('users', 'planId', planId, 'username', userHash)
        return result
    
    
    def getPlanPrice(self, planId):
        """
        Get the price of a plan based on the planId.

        :param planId: The unique identifier of the plan.
        :return: The price of the plan.
        """
        result = self.dbHandler.select('plans', ['price'], 'planId', '=', planId)
        return result
    
    
    def getCreationLimitForUser(self, userHash):
        """
            Get the creation limit for the specified user.

            :param userHash: The hash value of the user account.
            :type userHash: str
            :return: The creation limit for the user.
            :rtype: int
        """
        result = self.dbHandler.joinSelect('plans', 'filesPerDay', 'users', 'username', userHash, 'planId')
        return result
    
    
    def getUserLastCreationDate(self, userHash):
        """
        :param userHash: The userHash parameter is a hash string representing the username of the user whose last creation date is to be retrieved.
        :return: The method returns the last creation date of the user as a result.
        """
        result = self.dbHandler.select('users', ['lastCreation'], 'username', '=', userHash)
        return result
    
    
    def updateUserCreationCount(self, userHash, creationCount = None):
        """
        :param userHash: The hash ID of the user
        :param creationCount: The number of creations to update (optional)
        :return: True if the update was successful, False otherwise
        """
        # if none add one
        if creationCount == None:
            currentCount = self.getUserCreationCount(userHash)
            if not currentCount and isinstance(currentCount, bool):
                return False
            creationCount = currentCount + 1
        # if not none set to number
        result = self.dbHandler.update('users', 'creationCount', creationCount, 'username', userHash)
        return result
        
    
    def getUserCreationCount(self, userHash):
        """
        Retrieves the creation count of a user.

        :param userHash: The username of the user to retrieve the creation count for.
        :return: The creation count of the specified user.
        """
        result = self.dbHandler.select('users', ['creationCount'], 'username', '=', userHash)
        return result

    
    def updateLastCreation(self, userHash, date):
        """
            Update the last creation date of a user in the database.

            :param userHash: The username or user identifier of the user.
            :type userHash: str
            :param date: The new last creation date to be updated.
            :type date: str
            :return: True if the update operation was successful, False otherwise.
            :rtype: bool
        """
        result = self.dbHandler.update('users', 'lastCreation', date, 'username', userHash)
        return result



