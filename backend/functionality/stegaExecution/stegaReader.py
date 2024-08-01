from backend.functionality.stegaExecution.aesEncryption import Decrypter
from backend.functionality.stegaExecution.fileAuthentication import ReceiveFileAuthenticator
from backend.functionality.stegaExecution.reedSolomon import ReedSolomonExecuter
from backend.functionality.stegaExecution.steganography import ImageSteganographyReader
from backend.functionality.stegaExecution.stegaFuncs import StegaFuncs


class SteganographyReader(StegaFuncs):
    """
    :class SteganographyReader:

    Reader class to extract hidden data from steganography files.

    :ivar StegaFuncs decrypter: An instance of the Decrypter class for AES decryption.
    :ivar StegaFuncs fileAuthenticator: An instance of the ReceiveFileAuthenticator class for file authentication.
    :ivar StegaFuncs reedSolomonExecuter: An instance of the ReedSolomonExecuter class for Reed-Solomon decoding.
    :ivar StegaFuncs imageReader: An instance of the ImageSteganographyReader class for reading steganography data from images.

    Methods:
    =========

    __init__(self):
        Initializes the SteganographyReader class.

    run(self, modFile, metadata, userHash):
        Extracts hidden data from the steganography file.

        :param str modFile: The steganography file path.
        :param dict metadata: The metadata associated with the steganography file.
        :param str userHash: The user hash for authentication.
        :return: The extracted byte data, or None if the task couldn't be completed.

    checkFileAuthenticator(self, authenticator, userHash):
        Validates the file authenticator.

        :param dict authenticator: The authenticator data.
        :param str userHash: The user hash for authentication.
        :return: A tuple containing a boolean indicating if the authenticator is valid and the additional data.

    readData(self, filePath, additionalData):
        Reads steganography data from the given file path.

        :param str filePath: The file path.
        :param dict additionalData: The additional data required for reading the steganography data.
        :return: The binary data, or None if the data couldn't be read.

    decodeData(self, byteData, reedSolomonAdditionalData, aesKey):
        Decodes the byte data using Reed-Solomon and AES.

        :param bytes byteData: The byte data to decode.
        :param dict reedSolomonAdditionalData: The additional data required for Reed-Solomon decoding.
        :param str aesKey: The AES key for decryption.
        :return: The decoded byte data, or None if the data couldn't be decoded.

    convertBinToByteData(self, binData):
        Converts binary data to byte data.

        :param str binData: The binary data.
        :return: The converted byte data.

    saveDataToZipFile(self, filePath, byteData):
        Saves the byte data to a zip file.

        :param str filePath: The file path.
        :param bytes byteData: The byte data to save.
        :return: A tuple containing a boolean indicating if the zip file was saved and the zip file path.

    getZipFilePath(self, filePath):
        Generates the zip file path from the given file path.

        :param str filePath: The file path.
        :return: The zip file path.
    """

    def __init__(self):
        """
        Initializes the object.

        :return: None
        :rtype: None
        """
        super().__init__()
        # aes decrypter
        self.decrypter = Decrypter()
        # file authenticator
        self.fileAuthenticator = ReceiveFileAuthenticator()
        # reed solomon encrypter
        self.reedSolomonExecuter = ReedSolomonExecuter()
        # image ins
        self.imageReader = ImageSteganographyReader()
    
    
    
    def run(self, modFile, metadata, userHash):
        """

        :param modFile: The file to be processed.
        :param metadata: The metadata associated with the file.
        :param userHash: The hash value of the user.

        :return: The processed byte data.

        """
        # check authenticator (authenticator)
        validAuthenticator, dataFromAuth = self.checkFileAuthenticator(metadata, userHash)
        print('checked authenticatr')
        if not validAuthenticator:
            print('Couldn\'t complete task')
            return None
        # save file
        modFilePath = self.saveFile(modFile)
        if not modFilePath:
            print('couldnt save file')
            return None
        # extract data (reader)
        binData = self.readData(modFilePath, dataFromAuth['additionalData'])
        print('read data')
        if not binData:
            print('Couldn\'t complete task')
            return None
        # remake into bytes
        byteData = self.convertBinToByteData(binData)
        print('converted 10 to bytes')
        # decode data
        byteData = self.decodeData(byteData, dataFromAuth['reedSolomonAdditionalData'], dataFromAuth['aesKey'])
        print('decoded data')
        if not byteData:
            print('Couldn\'t complete task')
            return None
        if not self.deleteFile(modFilePath):
            print('couldnt delete files')
        print('done')
        return byteData
    
    
    '''
    def run(self, filePath, userHash):
        print('start')
        fileType = self.getFileType(filePath)
        print('file type: ' + fileType)
        # read authenticator from metadata (metadata handler)
        authenticator = self.getMetadata(fileType, filePath)
        print('got metadata')
        if authenticator == False:
            print('Couldn\'t complete task')
            return None
        if authenticator == None:
            print('File wasn\'t hiding information or was changed')
            return None
        # check authenticator (authenticator)
        validAuthenticator, dataFromAuth = self.checkFileAuthenticator(authenticator, userHash)
        print('checked authenticatr')
        if not validAuthenticator:
            print('Couldn\'t complete task')
            return None
        # extract data (reader)
        binData = self.readData(fileType, filePath, dataFromAuth['additionalData'])
        print('read data')
        # remake into bytes
        byteData = self.convertBinToByteData(binData)
        print('converted 10 to bytes')
        # decode data
        byteData = self.decodeData(byteData, dataFromAuth['reedSolomonAdditionalData'], dataFromAuth['aesKey'])
        print('decoded data')
        if not byteData:
            print('Cpuldn\'t complete task')
            return None
        # get zip file from byte data
        saved, zipFilePath = self.saveDataToZipFile(filePath, byteData)
        print('saved zip file from data')
        if not saved:
            print('Couldn\'t complete task')
            return None
        print('done')
        return zipFilePath
    #'''
    
    
    # authenticator
    def checkFileAuthenticator(self, authenticator, userHash):
        """
        :param authenticator: The authenticator to be checked.
        :param userHash: The hash of the user.

        :return: A tuple containing a boolean value indicating whether the authenticator is valid or not,
                 and the data associated with the authenticator.

        """
        # {'aesKey':aesKey, 'additionalData':additionalData, 'reedSolomonAdditionalData':reedSolomonAdditionalData}
        valid, data = self.fileAuthenticator.validateAuthenticator(authenticator, userHash)
        return valid, data
    
    
    # reader
    def readData(self, filePath, additionalData):
        """
        Reads data from a file.

        :param filePath: The path to the file to read from.
        :param additionalData: Additional data to pass to the `readData` method of the `imageReader` object.
        :return: The binary data read from the file. Returns `None` if an error occurs.
        """
        try:
            binData = self.imageReader.readData(filePath, additionalData)
            return binData
        except:
            return None
    
    
    # decode
    def decodeData(self, byteData, reedSolomonAdditionalData, aesKey):
        """
        Decodes the given byte data using Reed-Solomon error correction and AES decryption.

        :param byteData: The byte data to be decoded.
        :param reedSolomonAdditionalData: Additional data required for Reed-Solomon error correction.
        :param aesKey: The AES key used for decryption.
        :return: The decoded byte data.
        """
        byteData = self.reedSolomonDecodeData(byteData, reedSolomonAdditionalData)
        print('decoded reed solomon')
        if not byteData:
            print('Data was too corrupted')
            return None
        byteData = self.aesDecodeData(aesKey, byteData)
        print('aes decoded data')
        return byteData
    
    def reedSolomonDecodeData(self, byteData, additionalData):
        """
        Decode the given byte data using reed-solomon error correction algorithm.

        :param byteData: A list of bytes representing the encoded data.
        :param additionalData: Additional data required for error correction.
        :return: A list of bytes representing the decoded data.
        """
        byteData = self.reedSolomonExecuter.decodeData(byteData, additionalData)
        return byteData
    
    def aesDecodeData(self, key, byteData):
        """
        Decrypts byteData using the AES algorithm with the provided key.

        :param key: A string representing the encryption key.
        :param byteData: A bytes object containing the encrypted data.
        :return: A bytes object containing the decrypted data. Returns None if decryption fails.
        """
        try:
            byteData = self.decrypter.run(key, byteData)
            return byteData
        except:
            return None
    
    
    
    # remake 10 to bytes
    def convertBinToByteData(self, binData):
        """

        Converts binary data into byte data.

        :param binData: The binary data to be converted.
        :return: The byte data resulting from the conversion.

        """
        byteData = b''
        for i in range(0, len(binData), 8):
            binToConvert = binData[i : i+8]
            byteInt = int(binToConvert, 2)
            byteValue = byteInt.to_bytes(1, byteorder='big')
            byteData += byteValue
        return byteData
    
    
    # remake bytes to zip
    def saveDataToZipFile(self, filePath, byteData):
        """
        Save the given byte data to a ZIP file at the specified file path.

        :param filePath: The file path where the ZIP file will be saved.
        :param byteData: The byte data to be written to the ZIP file.
        :return: A tuple indicating the success status and the path of the saved ZIP file.

        """
        try:
            zipFilePath = self.getZipFilePath(filePath)
            with open(zipFilePath, 'wb') as f:
                f.write(byteData)
            return True, zipFilePath
        except:
            return False, None
    
    def getZipFilePath(self, filePath):
        """
        Get the path of a .zip file based on the given file path.

        :param filePath: The file path of the original file.
        :return: The path of the .zip file.
        """
        filePath = ''.join(filePath.split('.')[:-1])
        zipFilePath = filePath + '.zip'
        return zipFilePath
    
    '''
    # unzip file
    def unzipDataFile(self, zipFilePath, newFilePath):
        try:
            with zipfile.ZipFile(zipFilePath, 'r') as zipFile:
                zipFile.extractall(newFilePath)
            return True
        except:
            return False
    '''
    




'''import time


r = SteganographyReader()
filePath = 'stegaExecution/modFile.png'
userHash = '0123456789012345678901'

start = time.time()
zipFilePath = r.run(filePath, userHash)
end = time.time()
print(zipFilePath)
print(str(round(end-start)) + ' seconds')'''




