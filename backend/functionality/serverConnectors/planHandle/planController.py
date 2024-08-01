from backend.functionality.serverConnectors.planHandle.planService import PlanService


class PlanContoller:
    def __init__(self):
        self.planService = PlanService()
    
    
    def loadPlans(self, userHash):
        """
        Load Plans.

        Load plans for a given user.

        :param userHash: The hash identifier of the user.
        :return: The list of plans loaded for the user.

        """
        return self.planService.loadPlans(userHash)
    
    def updatePlan(self, userHash, planId):
        """
        :param userHash: The hash value of the user.
        :param planId: The ID of the plan to update.
        :return: True if the plan is successfully updated, False otherwise.
        """
        return self.planService.updatePlan(userHash, planId)
    
    def getCurrentPlan(self, userHash):
        """
        Get the current plan for a given user.

        :param userHash: The hash of the user.
        :return: The current plan ID.
        """
        return self.planService.getCurrentPlanId(userHash)
    
    def getCreationsLeft(self, userHash):
        """
        Retrieve the number of remaining creations for a given user.

        :param userHash: The hash representing the user.
        :return: The number of remaining creations for the user.
        """
        return self.planService.getCreationsLeft(userHash)

    def addUserCreation(self, userHash):
        """
        Method to perform user creation for the given userHash.

        :param userHash: The user hash string for user creation.
        :return: None.
        """
        return self.planService.addUserCreation(userHash)


