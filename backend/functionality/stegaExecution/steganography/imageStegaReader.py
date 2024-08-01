import cv2
from functools import partial
from backend.functionality.stegaExecution.steganography.imageStega import ImageSteganography



class ImageSteganographyReader(ImageSteganography):
    """
    Class for reading data from an image using steganography.

    Attributes:
        None

    Methods:
        readData(imageFilePath, additionalData): Read data from the image.
        getInfoFromAdditionalData(additionalData): Get information from additional data.
        getImageBlockIntensities(imageWidth, imageHeight, blockMagnitudes): Get block intensities for the image.
        getIntensityByMagnitude(magnitude): Get intensity value by magnitude.
        getPixelListToRead(colorChannels, pixelCoordsToRead, blockIntensities, dataLen): Get pixel list to read.
        mapExtractDataFromLsb(pixelDict): Map extracted data from LSB.
        readLsbs(num, numOfLsbs): Read LSBs from a number.
    """

    def __init__(self):
        """
        Initialize a new instance of the class.

        :param self: The current instance of the class.
        :type self: object

        :return: None
        """
        super().__init__()
    
    
    
    def readData(self, imageFilePath, additionalData):
        """
        Read data from an image file using additional data.

        :param imageFilePath: File path of the image to read from.
        :param additionalData: Additional data needed to extract the desired data from the image.
        :return: Extracted data from the image.
        """
        dataLen, blockMagnitudes = self.getInfoFromAdditionalData(additionalData)
        imageFile = cv2.imread(imageFilePath)
        colorChannels = self.getImageBgrColorChannels(imageFile)
        blockIntensities = self.getImageBlockIntensities(imageFile.shape[1], imageFile.shape[0], blockMagnitudes)
        pixelCoordsToRead = self.getPixelCoords(imageFile.shape[1]//8*8, imageFile.shape[0]//8*8)
        pixelList = self.getPixelListToRead(colorChannels, pixelCoordsToRead, blockIntensities, dataLen)
        mappedLsbFunc = partial(self.mapExtractDataFromLsb)
        extractedLsbs = list(map(mappedLsbFunc, pixelList))
        extractedData = ''.join(extractedLsbs)
        extractedData = extractedData[:dataLen]
        return extractedData
    
    
    def getInfoFromAdditionalData(Self, additionalData):
        """
        Extracts information from the given additionalData string.

        :param additionalData: A string containing additional data.
        :return: A tuple of two values - dataLen (an integer) and blockMagnitudes (a string).
        """
        # len is first 10
        # block magnitudes is else
        dataLen = int(additionalData[:10])
        blockMagnitudes = additionalData[10:]
        return dataLen, blockMagnitudes
    
    
    def getImageBlockIntensities(self, imageWidth, imageHeight, blockMagnitudes):
        """
        Get the block intensities for a given image based on block magnitudes.

        :param imageWidth: The width of the image in pixels.
        :param imageHeight: The height of the image in pixels.
        :param blockMagnitudes: The list of block magnitudes.
        :return: A dictionary of block intensities with the keys as (row, col) tuples and values as intensities.
        """
        # divide into coords by image size
        blockRows = imageHeight // 8
        blocksInRow = imageWidth // 8
        # go through block magnitudes and assign to each
        blockIntensities = {}
        magnitudesPointer = 0
        for row in range(blockRows):
            for col in range(blocksInRow):
                blockIntensities[(row,col)] = self.getIntensityByMagnitude(blockMagnitudes[magnitudesPointer])
                magnitudesPointer += 1
        return blockIntensities
    
    def getIntensityByMagnitude(self, magnitude):
        """
        :param magnitude: the magnitude value for which the intensity needs to be retrieved
        :return: the intensity value corresponding to the given magnitude

        """
        magnitude = int(magnitude)
        for key, value in self.embeddingMagnitude.items():
            if value == magnitude:
                return key
    
    
    def getPixelListToRead(self, colorChannels, pixelCoordsToRead, blockIntensities, dataLen):
        """
        Get the list of pixels to read.

        :param colorChannels: List of color channels.
        :type colorChannels: list

        :param pixelCoordsToRead: List of pixel coordinates to read.
        :type pixelCoordsToRead: list

        :param blockIntensities: Block intensities.
        :type blockIntensities: list

        :param dataLen: Data length.
        :type dataLen: int

        :return: List of pixels to read.
        :rtype: list
        """
        pixelList = []
        colors = ['b', 'g', 'r']
        for i in range(3):
            color = colors[i]
            for coord in pixelCoordsToRead:
                pixelDict = {
                    'row':coord[0],
                    'col':coord[1],
                    'value':None,
                    'lsbnum':None
                }
                pixelDict['value'], pixelDict['lsbnum'] = self.getPixelValueAndLsbNum(
                    colorChannels,
                    colors,
                    color,
                    pixelDict['row'],
                    pixelDict['col'],
                    blockIntensities
                )
                dataLen -= pixelDict['lsbnum']
                pixelList.append(pixelDict)
                color = self.getNextClorChannelToModify(color, colors)
                if dataLen <= 0:
                    break
            if dataLen <= 0:
                    break
        return pixelList
    
    
    def mapExtractDataFromLsb(self, pixelDict):
        """
        Extracts the least significant bits (LSBs) from the given pixel dictionary.

        :param pixelDict: The dictionary containing the pixel value and LSB number.
        :type pixelDict: dict
        :return: The extracted LSBs.
        :rtype: list
        """
        lsbs = self.readLsbs(pixelDict['value'], pixelDict['lsbnum'])
        return lsbs
    
    def readLsbs(self, num, numOfLsbs):
        """
        Reads the least significant bits (LSBs) of a given number.

        :param num: The number from which to read the LSBs.
        :param numOfLsbs: The number of LSBs to read.
        :return: A string representing the binary value of the LSBs.

        """
        binNum = bin(num)[2:]
        lsbs = binNum[-numOfLsbs:]
        lsbs = lsbs.zfill(numOfLsbs)
        return lsbs
    


# Example usage
# c = ImageSteganographyReader()
# p = 'path_to_input_image.png'
# additional_data = 'additional_data_string'

# extracted_data = c.readData(p, additional_data)
# print(extracted_data)



