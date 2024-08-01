import os
import sys
sys.path.append(os.path.abspath(''))
from backend.functionality.database import DatabaseHandler


class PaymentHandler:
    """Handles payment for a user.

    This class provides methods to handle payment related tasks.

    """
    
    def __init__(self):
        self.dbHandler = DatabaseHandler()
    
    def pay(self, userHash, price):
        """
        :param userHash: The hash value of the user.
        :param price: The price of the item to be paid.
        :return: Boolean value indicating whether the payment was successful.
        """
        userExists = self.dbHandler.selectExists('users', 'username', userHash)
        return userExists
