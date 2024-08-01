from backend.functionality.database.databaseHandler import DatabaseHandler as DbHandler
#from databaseHandler import DatabaseHandler as DbHandler


class UserValidationRepository:

    def __init__(self):
        self.dbHandler = DbHandler()
    
    
    def usernameExists(self, usernameHash):
        """
        Check if a username exists in the 'users' table.

        :param usernameHash: The hash of the username to check.
        :return: True if the username exists, False otherwise.
        """
        result = self.dbHandler.selectExists('users', 'username', usernameHash)
        return result
    
    def emailExists(self, email):
        result = self.dbHandler.selectExists('users', 'email', email)
        return result
    
    def getPasswordByUsername(self, usernameHash):
        """
        :param usernameHash: the hashed username
        :return: the password associated with the given username
        """
        result = self.dbHandler.select('users', ['password'], 'username', '=', usernameHash)
        return result
    
    def verifiedEmail(self, usernameHash):
        result = bool(self.dbHandler.select('users', ['verified'], 'username', '=', usernameHash))
        return result
    
    def getUserVerCode(self, usernameHash):
        result = self.dbHandler.select('changePass', ['verCode'], 'username', '=', usernameHash)
        return result
    
    def verifyEmail(self, usernameHash):
        if not self.removeUserFromChangePass(usernameHash):
            print('couldnt NULL ver code')
            return False
        print('removed user from change pass')
        return self.dbHandler.update('users', 'verified', 1, 'username', usernameHash)
    
    def getEmailByUserHash(self, usernameHash):
        result = self.dbHandler.select('users', ['email'], 'username', '=', usernameHash)
        return result
    
    def getUserHashByEmail(self, email):
        result = self.dbHandler.select('users', ['username'], 'email', '=', email)
        return result
    
    def saveUserToChangePass(self, usernameHash):
        if not self.dbHandler.selectExists('changePass', 'username', usernameHash):
            return self.dbHandler.insertInto('changePass', ['username'], [usernameHash])
        return True
    
    def validChangePassUser(self, username):
        return self.dbHandler.selectExists('changePass', 'username', username)
    
    def updateUserPassword(self, usernameHash, passwordHash):
        return self.dbHandler.update('users', 'password', passwordHash, 'username', usernameHash)
    
    def removeUserFromChangePass(self, usernameHash):
        return self.dbHandler.delete('changePass', 'username', usernameHash)
    
    def addNewUser(self, email, usernameHash, passwordHash, verCode):
        """
        Add a new user to the database.

        :param usernameHash: The hash of the username.
        :param passwordHash: The hash of the password.
        :return: The result of inserting the user into the database.

        """
        values = [email, usernameHash, passwordHash]
        if not self.dbHandler.insertInto('users', ['email', 'username', 'password'], values):
            return False
        values = [usernameHash, verCode]
        return self.dbHandler.insertInto('changePass', ['username', 'verCode'], values)
    



