import hashlib
from reedsolo import RSCodec, ReedSolomonError


class ReedSolomonExecuter:
    """
    ReedSolomonExecuter

    This class provides methods for encoding and decoding data using Reed-Solomon error correction.

    """

    def __init__(self):
        """
        Initializes a new instance of the class.
        """
        pass
    
    
    
    def encodeData(self, byteData, correctionBytesNum):
        """
        :param byteData: The data to be encoded as bytes.
        :param correctionBytesNum: The number of correction bytes to be added for error correction.
        :return: The encoded data as bytes and the additional data.
        """
        correctionBytesNum = int(correctionBytesNum)
        coder = RSCodec(correctionBytesNum)
        encData = coder.encode(byteData)
        encData = bytes(encData)
        additionalData = self.getAdditionalData(byteData, correctionBytesNum)
        return encData, additionalData
    

    
    def getAdditionalData(self, byteData, correctionBytesNum):
        """
        Method: getAdditionalData

        Parameters:
            :param byteData: The byte data to be used for generating additional data.
            :param correctionBytesNum: The number of correction bytes for the additional data.

        Return:
            :return: The generated additional data, which is a combination of the data hash and the correction bytes number.

        """
        correctionBytesNum = str(correctionBytesNum).zfill(3)
        dataHash = self.hashData(byteData)
        additionalData = dataHash + correctionBytesNum
        return additionalData
    
    def hashData(self, byteData):
        """
        :param byteData: The input byte data to be hashed.
        :return: The MD5 hash value as a hexadecimal string.
        """
        md5Hash = hashlib.md5()
        md5Hash.update(byteData)
        md5Hash = md5Hash.hexdigest()
        return md5Hash
    
    
    
    def decodeData(self, encData, additionalData):
        """
        This method decodes the encoded data using Reed-Solomon error correction.

        :param encData: The encoded data.
        :param additionalData: The additional data used for error correction.
        :return: The decoded data if successful, None otherwise.
        """
        try:
            dataHash, correctionBytesNum = self.getDataFromAdditionalData(additionalData)
            coder = RSCodec(correctionBytesNum)
            byteData, _, _ = coder.decode(encData)
            byteData = bytes(byteData)

            if not self.checkData(byteData, dataHash):
                print('data not decoded correctly')
                return None
            return byteData
        except ReedSolomonError:
            # data too corrupted
            print('reed solomon error')
            return None
    
    
    def getDataFromAdditionalData(self, additionalData):
        """

        :param additionalData: The additional data from which to extract the data hash and correction bytes number.
        :return: A tuple consisting of the extracted data hash and correction bytes number.

        """
        dataHash = additionalData[:32]
        correctionBytesNum = int(additionalData[32:])
        return dataHash, correctionBytesNum

    def checkData(self, binData, dataHash):
        """
        Check if the hash of the binary data matches the given data hash.

        :param binData: The binary data to be hashed.
        :param dataHash: The expected hash value for the binary data.
        :return: True if the hash of the binary data matches the given data hash, False otherwise.
        """
        return self.hashData(binData) == dataHash
    

