import os
import math
import shutil
import zipfile
from backend.functionality.stegaExecution.aesEncryption import Encrypter
from backend.functionality.userValidation import UserValidationController as UserValidation
from backend.functionality.stegaExecution.fileAuthentication import SendFileAuthenticator
from backend.functionality.stegaExecution.reedSolomon import ReedSolomonExecuter
from backend.functionality.stegaExecution.steganography import ImageSteganographyInserter
from backend.functionality.stegaExecution.stegaFuncs import StegaFuncs


class SteganographyInserter(StegaFuncs):
    """Constructor for SteganographyInserter class.

    Args:
        databaseHandler: An instance of database handler.

    Attributes:
        encrypter: An instance of the Encrypter class.
        userValidation: An instance of the UserValidation class.
        fileAuthenticator: An instance of the SendFileAuthenticator class.
        reedSolomonExecuter: An instance of the ReedSolomonExecuter class.
        imageInserter: An instance of the ImageSteganographyInserter class.
        textInserter: An instance of the TextSteganographyInserter class.
    """

    def __init__(self):
        super().__init__()
        self.emptyUploadFolder()
        # aes encrypter
        self.encrypter = Encrypter()
        # user validation
        self.userValidation = UserValidation()
        # file authenticator
        self.fileAuthenticator = SendFileAuthenticator()
        # reed solomon encrypter
        self.reedSolomonExecuter = ReedSolomonExecuter()
        # image ins
        self.imageInserter = ImageSteganographyInserter()
    
    
    def emptyUploadFolder(self):
        """
        Deletes all files and folders within the specified upload folder.

        :return: None
        """
        for filename in os.listdir(self.uploadsFolderPath):
            filePath = os.path.join(self.uploadsFolderPath, filename)
            try:
                if os.path.isfile(filePath) or os.path.islink(filePath):
                    os.unlink(filePath)  # remove the file or link
                elif os.path.isdir(filePath):
                    shutil.rmtree(filePath)  # remove the directory and all its contents
            except Exception as e:
                print('Failed to delete ' + filePath)
                print(e)
    
    
    
    def run(self, dataFile, dataFileType, mediumFile, intendedUsersList):
        """
        :param dataFile: File containing the data to be encrypted and inserted into the medium file.
        :param dataFileType: Type of the data file.
        :param mediumFile: File where the data will be inserted.
        :param intendedUsersList: List of intended users for the encrypted data.
        :return: mediumFileBytes: The contents of the medium file after the data has been inserted.
                 authenticator: The generated authenticator for the inserted data.

        """
        print('start')
        if len(intendedUsersList) == 0 or len(intendedUsersList) > 3:
            print('Wrong user list')
            return None
        # save files
        dataFilePath = self.saveFile(dataFile, dataFileType)
        if not dataFilePath:
            print('couldnt save data file')
            return None
        mediumFilePath = self.saveFile(mediumFile)
        if not mediumFilePath:
            print('couldnt save medium file')
            return None
        # zip data
        byteData, zipFilePath = self.zipDataFile(dataFilePath)
        print('zipped data: ' + zipFilePath)
        print(len(byteData))
        # get file capacity (inserter)
        fileCapacity, additionalData = self.getFileCapacity(mediumFilePath)
        print('got file capacity')
        print(fileCapacity)
        # check file capacity
        bigEnough, correctionBytesNum = self.checkFileCapacity(fileCapacity, byteData)
        if not bigEnough:
            print('File not big enough')
            return -1
        print('file big enough')
        # encrypt data (encrypter)
        key, byteData, reedSolomonAdditionData = self.encodeData(byteData, correctionBytesNum)
        print('encrypted data')
        print(len(byteData))
        # remake data into 10
        binData = self.convertByteToBinData(byteData)
        print('converted data to 01')
        print(len(binData))
        # insert data (inserter)
        insertResult = self.insertData(mediumFilePath, binData, additionalData)
        print('inserted data')
        if not insertResult:
            #print('Couldn\'t insert data into file')
            print('Couldn\'t complete task')
            return None
        # generate authenticator (authenticator)
        authenticator = self.generateFileAuthenticator(key, intendedUsersList, insertResult, reedSolomonAdditionData)
        print('generated authenticator')
        # read file bytes
        try:
            with open(mediumFilePath, 'rb') as f:
                mediumFileBytes = f.read()
            if not self.deleteFile(dataFilePath) or not self.deleteFile(mediumFilePath) or not self.deleteFile(zipFilePath):
                print('couldnt delete files')
            print('done')
            return mediumFileBytes, authenticator
        except:
            print('failed last step')
            return None
    

    
    # remake bytes to 10
    def convertByteToBinData(self, byteData):
        """
        Converts a list of byte values into a binary string representation.

        :param byteData: A list of byte values to be converted.
        :return: A binary string representing the byte values.

        """
        binData = ''.join(format(byte, '08b') for byte in byteData)
        return binData
    
    
    # zip file
    def zipDataFile(self, dataFilePath):
        """
        Zip the data file.

        :param dataFilePath: The path of the data file to be zipped.
        :return: A tuple containing the bytes of the zipped file and the path of the zipped file.
        """
        # input_file output_zip
        # zip data file
        zipFilePath = self.getZipFileName(dataFilePath)
        self.convertFileToZip(dataFilePath, zipFilePath)
        # convert to bytes
        zipBytes = self.getZipFileBytes(zipFilePath)
        return zipBytes, zipFilePath
    
    def getZipFileName(self, dataFilePath):
        """

        :param dataFilePath: The file path of the data file.
        :return: The name of the zip file.

        """
        dataFileName = dataFilePath.split('.')[0]
        zipFileName = dataFileName + '.zip'
        return zipFileName
    
    def convertFileToZip(self, filePath, zipFilePath):
        """
        :param filePath: Path of the file to be converted to zip.
        :param zipFilePath: Path where the zip file will be created.
        :return: None

        Converts the given file to a zip file and saves it to the specified location.
        The file will be added to the zip with its original base name.

        """
        with zipfile.ZipFile(zipFilePath, 'w') as zipf:
            baseName = os.path.basename(filePath)
            zipf.write(filePath, arcname=baseName)
    
    def getZipFileBytes(self, zipFilePath):
        """

        :param zipFilePath: A string indicating the path to the zip file.
        :return: A bytes object containing the contents of the zip file.

        """
        with open(zipFilePath, 'rb') as file:
            zipBytes = file.read()
        return zipBytes
    
    
    
    # encode
    def encodeData(self, byteData, correctionBytesNum):
        """
        Encodes the given byte data using AES encryption and Reed-Solomon error correction.

        :param byteData: The byte data to be encoded.
        :param correctionBytesNum: The number of correction bytes to be added.
        :return: A tuple containing the encryption key, encoded byte data, and Reed-Solomon additional data.
        """
        key, byteData = self.aesEncodeData(byteData)
        print('aes done')
        print(len(byteData))
        byteData, reedSolomonAdditionalData = self.reedSolomonEncodeData(byteData, correctionBytesNum)
        print('reed solo done')
        print(len(byteData))
        return key, byteData, reedSolomonAdditionalData
    
    # aes encode
    def aesEncodeData(self, byteData):
        """
        :param byteData: The data to be encrypted using AES encryption.
        :return: A tuple containing the encryption key and the encrypted data.
        """
        key, byteData = self.encrypter.run(byteData)
        return key, byteData
    
    # reed solomon encode
    def reedSolomonEncodeData(self, byteData, capacity):
        """
        Encode the given byte data using Reed-Solomon encoding.

        :param byteData: The byte data to be encoded.
        :param capacity: The desired capacity of the encoded data.
        :return: A tuple containing the encoded data and the additional Reed-Solomon data.
        """
        encData, reedSolomonAdditionData = self.reedSolomonExecuter.encodeData(byteData, capacity)
        return encData, reedSolomonAdditionData
    
    
    # authenticator
    def generateFileAuthenticator(self, key, intendedUsersList, additionalData, reedSolomonAdditionalData):
        """
        :param key: The encryption key used to generate the file authenticator.
        :param intendedUsersList: A list of usernames of the intended users who can access the file.
        :param additionalData: Additional data that may be used to generate the file authenticator.
        :param reedSolomonAdditionalData: Additional data specific to Reed-Solomon encoding, if applicable.
        :return: The generated file authenticator.

        """
        intendedUserHashesList = [self.userValidation.getUsernameHash(username) for username in intendedUsersList]
        authenticator = self.fileAuthenticator.generateAuthenticator(key, intendedUserHashesList, additionalData, reedSolomonAdditionalData)
        return authenticator
    
    
    # file capacity
    def getFileCapacity(self, filePath):
        """
        :param filePath: The file path of the image file.
        :return: A tuple containing the capacity of the image file in bytes and additional data.
        """
        capacity, additionalData = self.imageInserter.getImageFileCapacity(filePath)
        return capacity, additionalData
    
    def checkFileCapacity(self, capacity, byteData):
        """
        Check if the given file capacity is sufficient to store the given byte data.

        :param capacity: The file capacity in bits.
        :param byteData: The byte data to be stored.
        :return: A tuple indicating whether the capacity is sufficient and the number of correction bytes needed.
        """
        capacity //= 8
        dataLen = len(byteData)
        if capacity < dataLen:
            return False, 0
        aesDataLen = dataLen//16 * 16 + 16 if dataLen%16!=0 else dataLen
        if capacity < aesDataLen:
            return False, 0
        correctionBytesNum = self.getNumberOfCorrectionBytes(aesDataLen, capacity)
        return correctionBytesNum>0, correctionBytesNum
    
    def getNumberOfCorrectionBytes(self, dataLen, capacity):
        """
        Returns the number of correction bytes needed for error correction within a given capacity.

        :param dataLen: The length of the data in bytes.
        :param capacity: The capacity in bits.
        :return: The number of correction bytes needed for error correction.
        """
        byteCapacity = capacity // 8
        # max of blocks the file can hold
        maxBlocks = byteCapacity // 255
        # min data piece per block
        minDataLen = math.ceil(dataLen / maxBlocks)
        # number of correction bytes per block
        numOfCorrectionBytesForData = 255 - minDataLen
        # no need for a single correction byte if the number is odd
        numOfCorrectionBytesForData = numOfCorrectionBytesForData // 2 * 2
        
        # for each byte two correction bytes are needed
        maxNeededCorrectionBytes = 255 / 3 * 2
        
        correctionBytesNum = min(numOfCorrectionBytesForData, maxNeededCorrectionBytes)
        return correctionBytesNum
    
    
    # insert
    def insertData(self, filePath, binData, additionalData):
        """
        Inserts binary data into a file at the specified file path along with additional data.

        :param filePath: The file path where the data needs to be inserted.
        :param binData: The binary data to be inserted into the file.
        :param additionalData: Additional data to be inserted along with the binary data.
        :return: The result of the insertion operation. Returns None if the data could not be inserted.
        """
        result = self.imageInserter.insertData(filePath, filePath, additionalData, binData) # result is len + magnitudes
        if not result:
            # couldn't insert data
            return None
        return result
    
 
 
 
 
 
    

# add size to image authenticator

# handle reedSolomonAdditionalData in recieveFileAuthenticator
# do hashData function in reedSolomonExecuter (md5)
# debug
# check with docx medium file

# docx medium removes pictures
# check links
