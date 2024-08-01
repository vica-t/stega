import os
import re
import random
import hashlib
import configparser
from backend.functionality.userValidation.userValidationRepository import UserValidationRepository as UVRepository
#from userValidationRepository import UserValidationRepository as UVRepository


class UserValidationService:

    def __init__(self):
        self.uvRepository = UVRepository()
    
    
    
    # sign up
    def doSignupAction(self, email, usernameHash, passwordHash, doublePasswordHash):
        """
        This method performs the signup action by adding a new user to the database.

        :param usernameHash: The hash of the username.
        :param passwordHash: The hash of the password.
        :param doublePasswordHash: The hash of the password entered twice for confirmation.

        :return: True if the signup action was successful, False otherwise.
        """
        # check if username exists
        if self.usernameExists(usernameHash):
            return False
        # check if password matches
        if passwordHash != doublePasswordHash:
            return False
        # add new user to database
        return self.addNewUser(email, usernameHash, passwordHash)
    
    # signup with hashing
    def signup(self, username, password, doublePassword):
        """
        Method Name: signup

        Description: This method is used to sign up a user by creating a new account with the provided username, password, and doublePassword. It returns a tuple containing a boolean indicating if the sign up was successful and the username hash.

        Parameters:
        - username (str): The username to be used for the new account.
        - password (str): The password to be used for the new account.
        - doublePassword (str): The repeated password to confirm.

        Returns:
        - tuple: A tuple containing two elements:
          - signedUp (bool): True if the sign up was successful, False otherwise.
          - usernameHash (str): The hash value of the username.

        """
        salt = self.getSalt()
        usernameHash = self.getStringHash(username + salt)
        passwordHash = self.getStringHash(password + salt)
        doublePasswordHash = self.getStringHash(doublePassword + salt)
        signedUp = self.doSignupAction(username, usernameHash, passwordHash, doublePasswordHash)
        if signedUp:
            return signedUp, usernameHash, False, None
        return signedUp, None, False, None
    
    # login
    def doLoginAction(self, usernameHash, passwordHash):
        """
        Perform the login action for a user with the given username and password.

        :param usernameHash: The hash of the username.
        :param passwordHash: The hash of the password.
        :return: True if the login information is valid, False otherwise.
        """
        # find user in db and check password
        valid = self.validLoginInfo(usernameHash, passwordHash)
        return valid
    
    # login with hashing
    def login(self, username, password):
        """
        Log in the user with the given username and password.

        :param username: The user's username.
        :param password: The user's password.
        :return: A tuple containing a boolean indicating whether the login was successful and the user's username hash.
        """
        salt = self.getSalt()
        usernameHash = self.getStringHash(username + salt)
        passwordHash = self.getStringHash(password + salt)
        loggedIn = self.doLoginAction(usernameHash, passwordHash)
        if not loggedIn:
            return loggedIn, None, False
        # get verified
        verEmail = self.verifiedEmail(usernameHash)
        return loggedIn, usernameHash, verEmail

    
    # get md5 hash of a string
    def getStringHash(self, strToHash):
        """
        Calculate the SHA256 and MD5 hashes of a given string.

        :param strToHash: The string to be hashed.
        :return: The MD5 hash of the SHA256 hash of the given string.
        """
        shaHashStr = hashlib.sha256()
        shaHashStr.update(strToHash.encode('utf-8'))
        shaHashStr = shaHashStr.hexdigest()
        hashStr = hashlib.md5()
        hashStr.update(strToHash.encode('utf-8'))
        hashStr = hashStr.hexdigest()
        return hashStr

    # get salt from config file
    def getSalt(self):
        """
        Retrieves the salt value used for user validation from the config file.

        :return: The salt value.
        """
        config = configparser.ConfigParser()
        dirPath = os.path.dirname(os.path.realpath(__file__))
        configFilePath = os.path.join(dirPath, "../../config.ini")
        configFilePath = os.path.abspath(configFilePath)
        config.read(configFilePath)
        return config['USER_VALIDATION']['salt']
    
    
    # check if username exists (rep)
    def usernameExists(self, usernameHash):
        """
        Check if a username exists based on its hash.

        :param usernameHash: The hash of the username.
        :return: Return True if the username exists, False otherwise.
        """
        return self.uvRepository.usernameExists(usernameHash)
    
    # check if password matches format (regex)
    def validPasswordFormat(self, password):
        """
        Check if a password meets the specified format requirements.

        :param password: The password to be checked.
        :type password: str
        :return: True if the password meets all the requirements, False otherwise.
        :rtype: bool
        """
        patterns = []
        # must be between 8 and 20 characters
        patterns.append(r'^.{8,20}$')
        # must start with a letter (lowercase or uppercase)
        patterns.append(r'^[a-zA-Z]')
        # must include at least one lowercase letter
        patterns.append(r'.*[a-z]+.*')
        # must include at least one uppercase letter
        patterns.append(r'.*[A-Z]+.*')
        # must include at least one number
        patterns.append(r'.*\d+.*')
        # must include at least one special character ( allowed special characters: ~!@#$%^&*()-_+={}[]|/\:;<>,.? )
        patterns.append(r'.*[~!@#$%^&*()\[\]{}\|\\/\-+_=:;<>,.?]+.*')
        # must not include any spaces or special characters that are not the allowed ones, and any characters that are not english letters and numbers
        patterns.append(r'^[a-zA-Z0-9~!@#$%^&*()\[\]{}\|\\/\-+_=:;<>,.?]+$')
        # combine all patterns
        patterns = [re.compile(p) for p in patterns]
        # check password
        for p in patterns:
            if not p.match(password):
                return False
        return True
    
    # add new user to database
    def addNewUser(self, email,  usernameHash, passwordHash):
        """
        Add a new user to the system.

        :param usernameHash: The hash of the username.
        :param passwordHash: The hash of the password.
        :return: The added user.
        """
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        verCode = random.randint(1000, 999999)
        verCode = str(verCode).zfill(6)
        addedUser = self.uvRepository.addNewUser(email, usernameHash, passwordHash, verCode)
        return addedUser

    
    # get user and password (rep)
    def validLoginInfo(self, usernameHash, passwordHash):
        """
        Check if the provided username and password hashes are valid login information.

        :param usernameHash: The hash of the username.
        :param passwordHash: The hash of the password.
        :return: True if the login information is valid, False otherwise.
        """
        # find if username exists
        if not self.usernameExists(usernameHash):
            return False
        # get password by username
        savedPassword = self.getPasswordByUsername(usernameHash)
        # compare hashes
        if savedPassword != passwordHash:
            return False
        return True
    
    # get password saved for username (rep)
    def getPasswordByUsername(self, usernameHash):
        """
        :param usernameHash: The hash of the username used to retrieve the password.
        :return: The password associated with the specified username hash.
        """
        password = self.uvRepository.getPasswordByUsername(usernameHash)
        return password
    
    # get if user verified email
    def verifiedEmail(self, usernameHash):
        ver = self.uvRepository.verifiedEmail(usernameHash)
        return ver
    
    
    # verify user email
    def verifyEmail(self, usernameHash, code):
        code = int(code)
        print(type(code))
        # get the code of the username
        verCode = int(self.uvRepository.getUserVerCode(usernameHash))
        print(type(verCode))
        # compare
        if not code == verCode:
            print('not equal')
            return False
        # change to verified and empty code
        return self.uvRepository.verifyEmail(usernameHash)
    
    # get email by user hash
    def getEmailByUserHash(self, usernameHash):
        result = self.uvRepository.getEmailByUserHash(usernameHash)
        return result
        
    # get user hash by email
    def getUserHashByEmail(self, email):
        if not self.uvRepository.emailExists(email):
            return None
        result = self.uvRepository.getUserHashByEmail(email)
        return result

    
    # get ver code
    def getVerCode(self, usernameHash):
        result = self.uvRepository.getUserVerCode(usernameHash)
        return result
    

    # save user hash to pass change table
    def saveUserToChangePass(self, usernameHash):
        return self.uvRepository.saveUserToChangePass(usernameHash)
    
    
    # update password for user
    def updateUserPassword(self, usernameHash, password, confirmPassword):
        salt = self.getSalt()
        passwordHash = self.getStringHash(password + salt)
        confirmPasswordHash = self.getStringHash(confirmPassword + salt)
        if passwordHash != confirmPasswordHash:
            return False
        if not self.uvRepository.updateUserPassword(usernameHash, passwordHash):
            return False
        return self.uvRepository.removeUserFromChangePass(usernameHash)
    
    
    # check if user in change pass table
    def validChangePassUser(self, username):
        return self.uvRepository.validChangePassUser(username)



