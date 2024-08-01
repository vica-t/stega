import smtplib
import configparser
from email.message import EmailMessage
import os
import sys
sys.path.append(os.path.abspath(''))
from backend.functionality.userValidation import UserValidationController


class EmailHandler:
    
    def __init__(self):
        self.userValidation = UserValidationController()
        self.email, self.password = self.getInfo()
    
    def getInfo(self):
        config = configparser.ConfigParser()
        dirPath = os.path.dirname(os.path.realpath(__file__))
        configFilePath = os.path.join(dirPath, "../../../config.ini")
        configFilePath = os.path.abspath(configFilePath)
        config.read(configFilePath)
        emailData = config['EMAIL']
        return emailData['email'], emailData['password']
    
    
    
    
    def verifyEmail(self, userHash, code):
        return self.userValidation.verifyEmail(userHash, code)
    


    def sendVerificationEmail(self, userHash):
        recepientEmail = self.userValidation.getEmailByUserHash(userHash)
        code = self.userValidation.getVerCode(userHash)
        message = self.getCodeMessage(recepientEmail, code)
        return self.sendMessage(message)
    
    
    def getCodeMessage(self, recepientEmail, code):
        msg = EmailMessage()
        msg['From'] = self.email
        msg['To'] = recepientEmail
        msg['Subject'] = 'STEGA - Email Verification'
        self.setCodeMessageBody(msg, code)
        return msg
    
    def setCodeMessageBody(self, msg, code):
        code = str(code)
        html_content = f"""
            <html lang="en">
            <head></head>
            <body style="font-family: Arial, sans-serif; background-color: #f6f6f6; margin: 0; padding: 0;">
                <div style="max-width: 600px; margin: 20px auto; background-color: #ffffff; padding: 20px; border-radius: 10px; box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);">
                    <h2 style="color: #333333;">Email Verification</h2>
                    <p style="font-size: 16px; color: #555555;">Hello,</p>
                    <p style="font-size: 16px; color: #555555;">Thank you for registering with our service. Please use the following code to verify your email address:</p>
                    <p style="font-size: 20px; font-weight: bold; color: #007BFF; text-align: center; margin: 20px 0;">{code}</p>
                    <p style="font-size: 16px; color: #555555;">Enter this code on the verification page to complete the process.</p>
                    <p style="font-size: 16px; color: #555555;">If you did not request this verification, please ignore this email.</p>
                </div>
            </body>
            </html>
        """
        msg.set_content("Please use the following code to verify your email: " + code)
        msg.add_alternative(html_content, subtype='html')
    
    
    
    def sendPasswordChangeEmail(self, userHash, link):
        recepientEmail = self.userValidation.getEmailByUserHash(userHash)
        message = self.getLinkMessage(recepientEmail, link)
        return self.sendMessage(message)
    
    
    def getLinkMessage(self, recepientEmail, link):
        msg = EmailMessage()
        msg['From'] = self.email
        msg['To'] = recepientEmail
        msg['Subject'] = 'STEGA - Reset Password'
        self.setLinkMessageBody(msg, link)
        return msg
    
    def setLinkMessageBody(self, msg, link):
        print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
        print(link)
        html_content = f"""
            <html lang="en">
            <head></head>
            <body style="font-family: Arial, sans-serif; background-color: #f6f6f6; margin: 0; padding: 0;">
                <div style="max-width: 600px; margin: 20px auto; background-color: #ffffff; padding: 20px; border-radius: 10px; box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);">
                    <h2 style="color: #333333;">Reset Password</h2>
                    <p style="font-size: 16px; color: #555555;">Hello,</p>
                    <a href="{link}" text-align: center;">Enter this link to set a new password.</a>
                    <p style="font-size: 16px; color: #555555;">If you did not request this verification, please ignore this email.</p>
                </div>
            </body>
            </html>
        """
        msg.set_content("Please use the following link to reset your password: " + link)
        msg.add_alternative(html_content, subtype='html')
    
    
    
    def sendMessage(self, message):
        smtpServer = 'smtp.gmail.com'
        smtpPort = 587
        smtpUsername = self.email
        smtpPassword = self.password

        try:
            with smtplib.SMTP(smtpServer, smtpPort) as server:
                print('started with')
                server.starttls()
                print('established connection')
                server.login(smtpUsername, smtpPassword)
                print('logged in')
                server.send_message(message)
                print('Email sent successfully!')
            return True
        except Exception as e:
            print(f'Failed to send email: {e}')
            return False
    

'''
e = EmailHandler()
print('start')
message = e.getMessage('aniramrum@gmail.com', 123456)
print('got message')
e.sendMessage(message)
'''

