from backend.functionality.userValidation.userValidationService import UserValidationService as UVService


class UserValidationController:

    def __init__(self):
        self.uvService = UVService()
    
    
    # sign up
    def signup(self, username, password, doublePassword):
        """
        Signs up a user with the provided username and password.

        :param username: The username of the user being signed up.
        :param password: The password for the user being signed up.
        :param doublePassword: The password entered again to confirm its accuracy.

        :return: The result of the signup process. Returns True if the signup is successful, False otherwise.

        """
        return self.uvService.signup(username, password, doublePassword)
    
    
    # login
    def login(self, username, password):
        """
        :param username: The username of the user.
        :param password: The password of the user.
        :return: The result of the login attempt.
        """
        return self.uvService.login(username, password)

    
    # verify email
    def verifyEmail(self, username, code):
        return self.uvService.verifyEmail(username, code)
    
    
    # get username hash
    def getUsernameHash(self, username):
        """
        :param username: the username for which the hash needs to be calculated
        :return: the hashed value of the username
        """
        salt = self.uvService.getSalt()
        usernameHash = self.uvService.getStringHash(username + salt)
        return usernameHash


    # get email by user hash
    def getEmailByUserHash(self, username):
        return self.uvService.getEmailByUserHash(username)
    
    
    # get user hash by email
    def getUserHashByEmail(self, email):
        return self.uvService.getUserHashByEmail(email)
    
    
    # save user to pass change table
    def saveUserToChangePass(self, username):
        return self.uvService.saveUserToChangePass(username)

    
    # get verification code
    def getVerCode(self, username):
        return self.uvService.getVerCode(username)
    
    
    # check if user in change pass table
    def validChangePassUser(self, username):
        return self.uvService.validChangePassUser(username)

    
    # update password of user
    def updateUserPassword(self, username, password, confirmPassword):
        return self.uvService.updateUserPassword(username, password, confirmPassword)


    
    
    