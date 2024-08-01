from datetime import datetime
from backend.functionality.serverConnectors.planHandle.planRepository import PlanRepository
from backend.functionality.serverConnectors.planHandle.paymentHandler import PaymentHandler


class PlanService:
    def __init__(self):
        self.planRepository = PlanRepository()
        self.paymentHandler = PaymentHandler()


    
    def loadPlans(self, userHash):
        """
        :param userHash: The unique hash value associated with the user.
        :return: A tuple containing a list of plans and the current plan ID. If no plans are available, returns None.
        :rtype: tuple
        """
        plans = self.planRepository.getAllPlans()
        if not plans:
            return None
        plans = [{'planId':plan[0], 'planName':plan[1], 'price':plan[2], 'filesPerDay':plan[3]} for plan in plans]
        currentPlanId = -1
        if userHash:
            currentPlanId = self.getCurrentPlanId(userHash)
            if currentPlanId == False and isinstance(currentPlanId, bool):
                return None
        return plans, currentPlanId
    
    
    def updatePlan(self, userHash, planId):
        """
            Update the plan for a user.

            :param userHash: The hash value of the user.
            :param planId: The ID of the new plan to update.
            :return: True if the plan is successfully updated, False otherwise.
        """
        planId = int(planId)
        currentPlanId = self.getCurrentPlanId(userHash)
        if currentPlanId == False and isinstance(currentPlanId, bool):
            return False
        currentPlanId = int(currentPlanId) if not currentPlanId == None else -1
        if planId <= currentPlanId:
            return True
        # pay
        price = self.planRepository.getPlanPrice(planId)
        if price == False and isinstance(price, bool):
            return False
        paymetSucceeded = self.paymentHandler.pay(userHash, price)
        if not paymetSucceeded:
            return False
        # if new one is bigger update to new plan id
        if self.planRepository.updatePlanForUser(userHash, planId) == False:
            return False
        return True
    
    
    def getCurrentPlanId(self, userHash):
        """
        Get the current plan ID for a given user hash.

        :param userHash: The hash value of the user.
        :return: The ID of the current plan for the user.
        """
        currentPlanId = self.planRepository.getCurrentPlanIdByUserHash(userHash)
        return currentPlanId

    
    def getCreationsLeft(self, userHash):
        """
        :param userHash: Unique identifier for the user.
        :return: The number of creations left for the user today.

        This method calculates the number of creations left for a user today based on their plan limit and the number of creations they have already made. If the user has no plan or if the user has exceeded their plan limit, it will return None. If the user has an unlimited plan, it will return -1.
        """
        # get creations left today
            # get limit
        creationsLimit = self.planRepository.getCreationLimitForUser(userHash)
        if not creationsLimit:
            return None
        userCreationsToday = self.getUserCreationsToday(userHash)
        if userCreationsToday == None:
            return None

        if creationsLimit == -1:
            return -1
        return creationsLimit - userCreationsToday
    
    def getUserCreationsToday(self, userHash):
        """
        :param userHash: The hash representing the user.
        :return: The number of creations made by the user today.

        This method retrieves the current date and compares it with the last creation date for the given user.
        If there is no last creation date stored for the user, the method returns None.
        If the last creation date does not match the current date, the method updates the creation count to 0 and returns 0.
        Otherwise, the method returns the number of creations made by the user today.
        """
        currentDate = datetime.now().date()
        # get last creation
        lastCreationDate = self.planRepository.getUserLastCreationDate(userHash)
        if not lastCreationDate:
            return None
        # if dont match update creations today to 0
        if lastCreationDate != currentDate:
            updated = self.planRepository.updateUserCreationCount(userHash, 0)
            if not updated:
                return None
            return 0
        return self.planRepository.getUserCreationCount(userHash)


    def addUserCreation(self, userHash):
        """
        :param userHash: The hash of the user to create.
        :return: Returns `True` if the user creation was successful, otherwise `False`.
        """
        updated = self.planRepository.updateLastCreation(userHash, datetime.now())
        if not updated:
            return False
        return self.planRepository.updateUserCreationCount(userHash)





