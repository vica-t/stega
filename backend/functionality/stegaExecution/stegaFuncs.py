import os
import time
import random
from abc import ABC


class StegaFuncs(ABC):
    """

    .. module:: StegaFuncs
       :platform: Windows
       :synopsis: This module provides functionalities for handling file upload and deletion in a steganography application.

    .. class:: StegaFuncs
       :noindex:

       This class provides methods for saving and deleting files used in steganography applications.

       .. method:: __init__()

          Initializes the StegaFuncs object and creates the uploads folder if it does not exist.

       .. method:: getUploadsFolderPath()

          Returns the absolute path to the uploads folder directory.

          :return: The absolute path to the uploads folder directory.

       .. method:: saveFile(fileBytes, fileType='png')

          Saves the given file bytes to disk.

          :param fileBytes: The bytes of the file to be saved.
          :param fileType: The type of the file to be saved. Default is 'png'.
          :return: The file path where the file was saved, or None if there was an error.

       .. method:: getFilePathToSave(fileType)

          Returns the file path where the file will be saved.

          :param fileType: The type of file to be saved.
          :return: The file path where the file will be saved.

          This method generates a unique file name based on the current timestamp and a random number, and concatenates it with the uploads folder path to create the file path where the file will be saved.

       .. method:: deleteFile(filePath)

          Deletes a file specified by the provided file path.


          :param filePath: the path of the file to be deleted
          :return: True if the file is successfully deleted, False otherwise

    """

    def __init__(self):
        """
        Initializes an instance of the class.

        :param self: The object instance.
        :type self: object

        :return: None.
        :rtype: NoneType
        """
        super().__init__()
        self.uploadsFolderPath = self.getUploadsFolderPath()
        os.makedirs(self.uploadsFolderPath, exist_ok=True)
    
    
    
    def getUploadsFolderPath(self):
        """
        Returns the absolute path to the uploads folder directory.

        :return: The absolute path to the uploads folder directory.
        """
        dirPath = os.path.dirname(os.path.realpath(__file__))
        folderPath = os.path.join(dirPath, "../uploads")
        folderPath = os.path.abspath(folderPath)
        return folderPath
    
    
    
    def saveFile(self, fileBytes, fileType='png'):
        """
        Saves the given file bytes to disk.

        :param fileBytes: The bytes of the file to be saved.
        :param fileType: The type of the file to be saved. Default is 'png'.
        :return: The file path where the file was saved, or None if there was an error.
        """
        try:
            filePath = self.getFilePathToSave(fileType)
            print(filePath)
            with open(filePath, 'wb') as f:
                f.write(fileBytes)
            return filePath
        except Exception as e:
            print(e)
            return None
    
    def getFilePathToSave(self, fileType):
        """
        :param fileType: The type of file to be saved.
        :return: The file path where the file will be saved.

        This method generates a unique file name based on the current timestamp and a random number, and concatenates it with the uploads folder path to create the file path where the file will be saved.
        """
        print('getting fle path')
        fileName = str(time.time()).replace('.', '') + str(random.randint(0, 100000)) + '.' + fileType
        filePath = self.uploadsFolderPath + '/' + fileName
        return filePath
    
    def deleteFile(self, filePath):
        """
        Deletes a file specified by the provided file path.

        :param filePath: the path of the file to be deleted
        :return: True if the file is successfully deleted, False otherwise
        """
        try:
            os.remove(filePath)
            return True
        except Exception as e:
            print(filePath)
            print(e)
            return False
    
    








