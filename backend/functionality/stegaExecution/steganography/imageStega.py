import cv2
from abc import ABC
import numpy as np
from backend.functionality.stegaExecution.steganography.dataIndexDistributer import DataIndexDistributer
#from dataIndexDistributer import DataIndexDistributer


class ImageSteganographya(ABC):
    """
    ImageSteganography is an abstract base class that provides methods for performing image steganography.

    Attributes:
        dataIndexDistributer (DataIndexDistributer): The object responsible for distributing data indexes.
        embeddingMagnitude (dict): A dictionary that maps embedding magnitudes 'l', 'm', and 'h' to their corresponding values.
        intensityPercentages (tuple): A tuple of two integers representing the minimum and maximum intensity percentages.

    Methods:
        __init__(): Initializes the ImageSteganography object.
        getImageBgrColorChannels(imageFile): Returns the BGR color channels of the given image file.
        getPixelCoords(imageWidth, imageHeight): Returns the pixel coordinates of an image with the given width and height.
        getPixelValueAndLsbNum(colorChannels, colors, color, row, col, blockIntensities): Returns the pixel value and the LSB number corresponding to the given parameters.
        getPixelValue(colorChannels, colors, color, row, col): Returns the pixel value of the specified color channel.
        getBlockCoordByPixelCoord(row, col): Returns the block coordinates corresponding to the given pixel coordinates.
        getNextClorChannelToModify(currentChannel, channelList): Returns the next color channel to modify.

    """

    def __init__(self):
        """
        Initializes the class with the provided parameters.

        :param self: The object instance.

        :return: None

        .. note::
            The method initializes the attributes of the class.
            - `dataIndexDistributer`: A DataIndexDistributer object.
            - `embeddingMagnitude`: A dictionary representing embedding magnitudes with 'l', 'm', and 'h' as keys and 3, 2, and 1
            as values respectively.
            - `intensityPercentages`: A tuple containing two integer values representing the minimum and maximum intensity percentages.

        """
        self.dataIndexDistributer = DataIndexDistributer()
        self.embeddingMagnitude = {'l':3, 'm':2, 'h':1}
        self.intensityPercentages = (5,80)
    
    
    
    def getImageBgrColorChannels(self, imageFile):
        """
        Split an image into its Blue, Green, and Red color channels.

        :param imageFile: The file path or image object.
        :return: A list of color channels that contains the Blue, Green, and Red channels.
        """
        colorChannels = cv2.split(imageFile)
        return colorChannels
        
    
    def getPixelCoords(self, imageWidth, imageHeight):
        """
        Get the pixel coordinates based on the given image width and height.

        :param imageWidth: The width of the image.
        :param imageHeight: The height of the image.
        :return: The pixel coordinates in a list format.
        """
        pixelCoords = self.dataIndexDistributer.getPixelCoords(imageWidth, imageHeight)
        return pixelCoords.tolist()
    
    
    def getPixelValueAndLsbNum(self, colorChannels, colors, color, row, col, blockIntensities):
        """
        Returns the pixel value and LSB (Least Significant Bit) number for a given color channel, color, row, column, and block intensities.

        :param colorChannels: The number of color channels in the image.
        :param colors: The number of colors per channel in the image.
        :param color: The specific color channel.
        :param row: The row number of the pixel.
        :param col: The column number of the pixel.
        :param blockIntensities: The block intensities of the image.
        :return: A tuple containing the pixel value and LSB number.
        """
        pixelValue = self.getPixelValue(colorChannels, colors, color, row, col)
        blockCoord = self.getBlockCoordByPixelCoord(row, col)
        lsbNum = self.embeddingMagnitude[blockIntensities[blockCoord]]
        return pixelValue, lsbNum
    
    def getPixelValue(self, colorChannels, colors, color, row, col):
        """
        :param colorChannels: List of color channels
        :param colors: List of available colors
        :param color: Color to retrieve the pixel value for
        :param row: Row index of the pixel
        :param col: Column index of the pixel
        :return: The pixel value for the specified color at the given row and column indices
        """
        pixelValue = colorChannels[colors.index(color)][row][col]
        return pixelValue
    
    def getBlockCoordByPixelCoord(self, row, col):
        """
        Calculate the block coordinates based on the given pixel coordinates.

        :param row: The row pixel coordinate.
        :param col: The column pixel coordinate.
        :return: The block coordinates.
        """
        blockCoord = (row//8, col//8)
        return blockCoord
    

    def getNextClorChannelToModify(self, currentChannel, channelList):
        """
        :param currentChannel: The current color channel to modify.
        :param channelList: The list of color channels.
        :return: The next color channel to modify.

        """
        curChannelIndex = channelList.index(currentChannel)
        nextChannelIndex = curChannelIndex+1 if curChannelIndex+1 < 3 else 0
        nextChannel = channelList[nextChannelIndex]
        return nextChannel





class ImageSteganography(ABC):
    def __init__(self):
        self.dataIndexDistributer = DataIndexDistributer()
        self.embeddingMagnitude = {'l': 3, 'm': 2, 'h': 1}
        self.intensityPercentages = (5, 80)
    
    def getImageBgrColorChannels(self, imageFile):
        """
        Split an image into its Blue, Green, and Red color channels.

        :param imageFile: The file path or image object.
        :return: A list of color channels that contains the Blue, Green, and Red channels.
        """
        return cv2.split(imageFile)
    
    def getPixelCoords(self, imageWidth, imageHeight):
        """
        Get the pixel coordinates based on the given image width and height.

        :param imageWidth: The width of the image.
        :param imageHeight: The height of the image.
        :return: The pixel coordinates in a NumPy array format.
        """
        pixelCoords = self.dataIndexDistributer.getPixelCoords(imageWidth, imageHeight)
        return pixelCoords
    
    def getPixelValueAndLsbNum(self, colorChannels, colors, color, row, col, blockIntensities):
        """
        Returns the pixel value and LSB (Least Significant Bit) number for a given color channel, color, row, column, and block intensities.

        :param colorChannels: The number of color channels in the image.
        :param colors: The number of colors per channel in the image.
        :param color: The specific color channel.
        :param row: The row number of the pixel.
        :param col: The column number of the pixel.
        :param blockIntensities: The block intensities of the image.
        :return: A tuple containing the pixel value and LSB number.
        """
        pixelValue = self.getPixelValue(colorChannels, colors, color, row, col)
        blockCoord = self.getBlockCoordByPixelCoord(row, col)
        lsbNum = self.embeddingMagnitude[blockIntensities[blockCoord]]
        return pixelValue, lsbNum
    
    def getPixelValue(self, colorChannels, colors, color, row, col):
        """
        :param colorChannels: List of color channels
        :param colors: List of available colors
        :param color: Color to retrieve the pixel value for
        :param row: Row index of the pixel
        :param col: Column index of the pixel
        :return: The pixel value for the specified color at the given row and column indices
        """
        return colorChannels[colors.index(color)][row, col]
    
    def getBlockCoordByPixelCoord(self, row, col):
        """
        Calculate the block coordinates based on the given pixel coordinates.

        :param row: The row pixel coordinate.
        :param col: The column pixel coordinate.
        :return: The block coordinates.
        """
        return row // 8, col // 8
    
    def getNextClorChannelToModify(self, currentChannel, channelList):
        """
        :param currentChannel: The current color channel to modify.
        :param channelList: The list of color channels.
        :return: The next color channel to modify.
        """
        curChannelIndex = channelList.index(currentChannel)
        nextChannelIndex = (curChannelIndex + 1) % len(channelList)
        return channelList[nextChannelIndex]

