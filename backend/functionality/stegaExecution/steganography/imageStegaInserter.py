import cv2
import numpy as np
from functools import partial
from backend.functionality.stegaExecution.steganography.imageStega import ImageSteganography
#from imageStega import ImageSteganography



class ImageSteganographyInserter(ImageSteganography):
    """
    Class to insert data into an image using steganography technique.

    :param ImageSteganography: Base class for image steganography
    """

    def __init__(self):
        """
        Constructor for the class.

        This method initializes an instance of the class and sets up any initial values or states.

        Parameters:
            self (object): The instance of the class.

        Returns:
            None
        """
        super().__init__()
    
    
    
    def getImageFileCapacity(self, imageFilePath):
        """
        Calculate the capacity of an image file.

        :param imageFilePath: The path to the image file.
        :return: A tuple containing the capacity and the block intensities and magnitudes.
        """
        imageFile = cv2.imread(imageFilePath)
        yColorChannel = self.getImageYColorChannel(imageFile)
        blockIntensities, capacity, blockMagnitudes = self.getImageBlockIntensities(yColorChannel)
        return capacity, [blockIntensities, blockMagnitudes]
    

    
    def getImageYColorChannel(self, imageFile):
        """
        :param imageFile: An input image file in BGR format.
        :return: The Y color channel of the input image file.

        This method converts the input image file from BGR to YCrCb color space using OpenCV's cv2.cvtColor function. It then splits the YCrCb image into different color channels using cv2.split function. Finally, it returns the Y channel of the color channels.

        """
        ycrcbImage = cv2.cvtColor(imageFile, cv2.COLOR_BGR2YCrCb)
        colorChannels = cv2.split(ycrcbImage)
        yChannel  = colorChannels[0]
        return yChannel
    
    
    
    def getImageBlockIntensities(self, yColorChannel):
        """
        :param yColorChannel: The luminance (Y) color channel of the image. This channel represents the brightness of pixels in the image.
        :return: A tuple containing the following:
                - blockIntensities: A dictionary mapping block coordinates to intensity values. Each block is represented as a dictionary with keys 'block', 'contrast', and 'intensity'.
                - capacity: The capacity of the image, calculated based on the channel blocks.
                - magnitudes: A list of magnitudes calculated for each channel block.
        """
        # [{'block':..., 'contrast':..., 'intensity':...}, ...]
        # divide into blocks
        channelBlocks = self.divideChannelToBlocks(yColorChannel)
        # calc contrast
        self.calcChannelBlocksContrasts(channelBlocks)
        # get percentages
        lowerPercentage, midPercentage = self.getIntensityPercentages()
        # classify
        self.classifyBlocksByIntensity(channelBlocks, lowerPercentage, midPercentage)
        # save
        # calc capacity
        capacity = self.getImageCapacity(channelBlocks)
        # save magnitudes
        magnitudes = self.saveChannelBlocksMagnitudes(channelBlocks)
        # reshape to be blockcoord:intesity
        blockIntensities = self.getBlockIntensityDictByChannelBlocks(channelBlocks)
        return blockIntensities, capacity, magnitudes
    
    
    def divideChannelToBlocks(self, channel):
        """
        Divides a given channel into 8x8 blocks.

        :param channel: The channel to be divided into blocks.
        :return: A list of dictionaries, each containing an 8x8 block, its coordinates, contrast, and intensity.
        """
        blocks = [] # block, coords, contrast, intensity, dct
        height, width = channel.shape[:2]
        # Adjust width and height to handle partial blocks
        width = (width // 8) * 8
        height = (height // 8) * 8
        # Iterate over the adjusted channel dimensions in 8x8 blocks
        for y in range(0, height, 8):
            for x in range(0, width, 8):
                # Extract the 8x8 block from the channel
                block = channel[y:y+8, x:x+8]
                blocks.append({'block':block, 'coords':(y/8, x/8), 'contrast':None, 'intensity':None})
        return blocks
    
    
    def calcChannelBlocksContrasts(self, channelBlocks):
        """
        Calculate the contrast for each block in the given channelBlocks.

        :param channelBlocks: A list of channel blocks.
        :type channelBlocks: list

        :return: None
        :rtype: None
        """
        for block in channelBlocks:
            contrast = self.getBlockContrast(block['block'])
            block['contrast'] = contrast
    
    def getBlockContrast(self, block):
        """
        :param block: A 2D array representing a block of pixel values.
        :return: The contrast value of the block.
        """
        mean = np.mean(block)
        sq_diffs = np.square(block - mean)
        variance = np.mean(sq_diffs)
        contrast = np.sqrt(variance)
        return contrast
    
    
    def getIntensityPercentages(self):
        """
        Return the intensity percentages of the color channels.

        This method returns a tuple containing the intensity percentages of the color channels. The first element of the tuple represents the intensity percentage for values ranging from 0 to x, where x is the value stored in `self.intensityPercentages[0]`. The second element of the tuple represents the intensity percentage for values ranging from x+1 to y, where y is the value stored in `self.intensityPercentages[1]`. The remaining values from y+1 to 100 are represented by the third element of the tuple.

        :return: A tuple containing the intensity percentages of the color channels.
        """
        # 0-x, x-y, y-100
        # x = 25, y = 50
        #mean, median = self.getContrastStatistics(dividedColorChannels)
        return self.intensityPercentages[0], self.intensityPercentages[1]
    
    
    def classifyBlocksByIntensity(self, channelBlocks, lowerPercentage, midPercentage):
        """
        :classifyBlocksByIntensity:
        Method to classify blocks in a given list based on their intensity values. Blocks are classified as 'l' for lower intensity, 'm' for mid intensity, and 'h' for higher intensity.

        :param channelBlocks: A list of dictionary objects representing blocks, each containing a 'contrast' value.
        :param lowerPercentage: The percentage of blocks to be classified as lower intensity.
        :param midPercentage: The percentage of blocks to be classified as mid intensity.
        :return: None

        """
        blockContrasts = [block['contrast'] for block in channelBlocks]
        lowerCount, midCount = self.getElementCountForPercentage(len(blockContrasts), lowerPercentage, midPercentage)
        # sort the list
        blockContrasts.sort()
        # divide into three lists
        lowerContrasts = blockContrasts[:lowerCount]
        midContrasts = blockContrasts[lowerCount:lowerCount+midCount]
        # go through check assign pop
        for block in channelBlocks:
            if block['contrast'] in lowerContrasts:
                block['intensity'] = 'l'
                lowerContrasts.remove(block['contrast'])
            elif block['contrast'] in midContrasts:
                block['intensity'] = 'm'
                midContrasts.remove(block['contrast'])
            else:
                block['intensity'] = 'h'
    
    def getElementCountForPercentage(self, totalElems, lowerPercentage, midPercentage):
        """
        Calculate the count of elements for given lower and mid percentages.

        :param totalElems: The total number of elements.
        :param lowerPercentage: The percentage of elements in the lower range.
        :param midPercentage: The percentage of elements in the mid range.
        :return: A tuple containing the count of elements in the lower and mid ranges.
        """
        lowerCount = round(lowerPercentage / 100 * totalElems)
        midCount = round(midPercentage / 100 * totalElems)
        return lowerCount, midCount
    
    
    def getImageCapacity(self, channelBlocks):
        """
        Calculate the image capacity based on the given list of channel blocks.

        :param channelBlocks: A list of channel blocks, each containing the intensity value.
        :type channelBlocks: list

        :return: The total image capacity.
        :rtype: int
        """
        capacity = 0
        for block in channelBlocks:
            intensity = block['intensity']
            capacity += self.embeddingMagnitude[intensity]
        capacity *= 8*8
        capacity *= 3
        return capacity
    
    
    def saveChannelBlocksMagnitudes(self, channelBlocks):
        """
        :param channelBlocks: A list of dictionaries representing channel blocks.
        :return: A list of magnitudes corresponding to the intensity values of the channel blocks.

        """
        magnitudes = []
        for block in channelBlocks:
            intensity = block['intensity']
            magnitude = self.embeddingMagnitude[intensity]
            magnitudes.append(magnitude)
        return magnitudes
    
    
    def getBlockIntensityDictByChannelBlocks(self, channelBlocks):
        """
        Build a dictionary of block intensities based on the given channel blocks.

        :param channelBlocks: A list of channel blocks.
        :type channelBlocks: list[dict]
        :return: A dictionary containing block intensities keyed by block coordinates.
        :rtype: dict[tuple[int], float]
        """
        blockIntensities = {}
        for block in channelBlocks:
            coords = tuple(int(c) for c in block['coords'])
            blockIntensities[coords] = block['intensity']
        return blockIntensities
    

    
    
    def insertData(self, imageFilePath, newImageFilePath, additionalData, binData):
        """
        Inserts data into an image file.

        :param imageFilePath: The path of the image file to read.
        :param newImageFilePath: The path of the new image file to write.
        :param additionalData: A tuple containing the block intensities and block magnitudes.
        :param binData: The binary data to insert into the image.
        :return: The additional data after modification, or None if an error occurred.
        """
        try:
            imageFile = cv2.imread(imageFilePath)
            colorChannels = self.getImageBgrColorChannels(imageFile)
            blockIntensities = additionalData[0]
            blockMagnitudes = additionalData[1]
            pixelCoordsToModify = self.getPixelCoords(imageFile.shape[1]//8*8, imageFile.shape[0]//8*8)
            pixelList = self.getPixelListToModify(colorChannels, pixelCoordsToModify, blockIntensities, binData)
            mappedLsbFunc = partial(self.mapEmbedDataInLsb)
            pixelList = list(map(mappedLsbFunc, pixelList))
            dividedPixelList = self.dividePixelListToColors(pixelList)
            self.modifyColorChannels(colorChannels, dividedPixelList)
            imageFile = self.mergeImage(colorChannels)
            cv2.imwrite(newImageFilePath, imageFile)
            blockMagnitudes = self.getBlockMagnitudesString(blockMagnitudes)
            additionalData = self.getAdditionalData(len(binData), blockMagnitudes)
            return additionalData
        except:
            return None
    
    
    def getPixelListToModify(self, colorChannels, pixelCoordsToModify, blockIntensities, binData):
        """
        :param colorChannels: List of color channels (e.g. ['b', 'g', 'r'])
        :param pixelCoordsToModify: List of pixel coordinates to modify (e.g. [(row1, col1), (row2, col2), ...])
        :param blockIntensities: Dictionary of block intensities (e.g. {'b': 0.5, 'g': 0.3, 'r': 0.8})
        :param binData: Binary data to hide in the pixels
        :return: List of pixel dictionaries with modified values, LSB numbers, and padded data

        """
        pixelList = []
        colors = ['b', 'g', 'r']
        dataPointer = 0
        for i in range(3):
            color = colors[i]
            for coord in pixelCoordsToModify:
                pixelDict = {
                    'row':coord[0],
                    'col':coord[1],
                    'color':color,
                    'value':None,
                    'lsbnum':None,
                    'data':None
                }
                pixelDict['value'], pixelDict['lsbnum'] = self.getPixelValueAndLsbNum(
                    colorChannels,
                    colors,
                    color,
                    pixelDict['row'],
                    pixelDict['col'],
                    blockIntensities
                )
                pixelDict['data'], dataPadded = self.padDataForLsbNum(
                    pixelDict['value'],
                    binData[dataPointer%len(binData) : dataPointer%len(binData)+pixelDict['lsbnum']],
                    pixelDict['lsbnum']
                )
                dataPointer += pixelDict['lsbnum']
                pixelList.append(pixelDict)
                color = self.getNextClorChannelToModify(color, colors)
                if len(binData) == dataPointer or dataPadded:
                    break
            if len(binData) == dataPointer or dataPadded:
                break
        return pixelList
    
    def padDataForLsbNum(self, num, binData, lsbNumToModify):
        """
        Pad the binary data to a specified number of least significant bits (LSBs) by adding leading zeros.

        :param num: The original number.
        :param binData: The original binary data.
        :param lsbNumToModify: The desired number of LSBs in the modified binary data.
        :return: A tuple containing the modified binary data and a flag indicating if modification was made.

        """
        if len(binData) == lsbNumToModify:
            return binData, False
        padLen = lsbNumToModify - len(binData)
        bestDiff = 300
        bestModBinData = ''
        for i in range(2 ** padLen):
            padBits = bin(i)[2:].zfill(padLen)
            modBinData = binData + padBits
            modNum = self.changeLsbs(num, modBinData)
            diff = abs(num - modNum)
            if diff < bestDiff:
                bestDiff = diff
                bestModBinData = modBinData
        return bestModBinData, True
    
    
    def mapEmbedDataInLsb(self, pixelDict):
        """

        :param pixelDict: A dictionary containing 'value' and 'data' keys.
                         'value' is the original pixel value.
                         'data' is the data to be embedded in the pixel value.
        :return: The modified pixelDict dictionary with the 'new' key containing
                 the pixel value after embedding the data.

        """
        pixelDict['new'] = self.embedDataInLsb(pixelDict['value'], pixelDict['data'])
        return pixelDict
    
    def embedDataInLsb(self, colorValue, binData):
        """
        Embeds binary data into the least significant bits (LSBs) of a color value.

        :param colorValue: The original color value.
        :type colorValue: int
        :param binData: The binary data to be embedded.
        :type binData: str
        :return: The modified color value with the data embedded in LSBs.
        :rtype: int
        """
        colorValue = min(self.changeLsbs(colorValue, binData), self.changeLsbs(255, binData))
        return colorValue
    
    def changeLsbs(self, num, lsbs):
        """
        Change the least significant bits (LSBs) of a given number.

        :param num: The number whose LSBs will be changed.
        :param lsbs: The new LSBs to be applied to the number.
        :return: The modified number with the new LSBs.

        """
        binNum = bin(num)[2:]
        binNum = binNum[:len(binNum)-len(lsbs) if len(binNum)>len(lsbs) else 0]
        binNum += lsbs
        num = int(binNum, base=2)
        return num
    
    
    def dividePixelListToColors(self, pixelList):
        """
        Divide a list of pixels into three colors - blue, green, and red.

        :param pixelList: A list of pixels, where each pixel is a dictionary with a 'color' key.
        :return: A dictionary containing the divided pixel list for each color.
            The dictionary has three keys - 'b' for blue, 'g' for green, and 'r' for red.
            Each key maps to a list of pixels of that color.
        """
        dividedPixelList = {'b':[], 'g':[], 'r':[]}
        for pixel in pixelList:
            dividedPixelList[pixel['color']].append(pixel)
        return dividedPixelList
    
    
    def modifyColorChannels(self, colorChannels, dividedPixelList):
        """
        Modify the color channels of an image based on a divided pixel list.

        :param colorChannels: A list representing the color channels of the image.
        :param dividedPixelList: A dictionary representing the divided pixel list.
        :return: None

        The method modifies the color channels of an image by assigning new pixel values based on the divided pixel list.
        It iterates over each color channel (red, green, blue) and assigns the new pixel values to the corresponding positions
        in the color channels list.

        """
        for i in range(3):
            color = list(dividedPixelList.keys())[i]
            for pixel in dividedPixelList[color]:
                colorChannels[i][pixel['row']][pixel['col']] = pixel['new']
    
    
    def mergeImage(self, colorChannels):
        """
        Merge the color channels into a single image.

        :param colorChannels: A list of color channel arrays (e.g., [red_channel, green_channel, blue_channel]).
        :type colorChannels: List[np.ndarray]

        :return: The merged image with the color channels stacked together.
        :rtype: np.ndarray
        """
        joinedImage = np.stack((colorChannels[0], colorChannels[1], colorChannels[2]), axis=-1)
        return joinedImage
    
    
    def getBlockMagnitudesString(self, blockMagnitudes):
        """
        Convert a list of block magnitudes to a string representation.

        :param blockMagnitudes: The list of block magnitudes.
        :type blockMagnitudes: list
        :return: The string representation of block magnitudes.
        :rtype: str
        """
        blockMagnitudes = [str(i) for i in blockMagnitudes]
        blockMagnitudes = ''.join(blockMagnitudes)
        return blockMagnitudes
    
    def getAdditionalData(self, dataLen, blockMagnitudes):
        """

        :param dataLen: The length of the data.
        :param blockMagnitudes: The magnitudes of the data blocks.
        :return: The additional data.

        """
        dataLen = str(dataLen).rjust(10)
        additionalData = dataLen + blockMagnitudes
        return additionalData
    

    
'''
c = ImageSteganographyInserter()
p = 'C:/Users/vicat/Dropbox/Vica_new/vica/computer/cyber/yud_bet/stega/backend/functionality/assets/greenCat.png'
pp = 'C:/Users/vicat/Dropbox/Vica_new/vica/computer/cyber/yud_bet/stega/backend/functionality/assets/greenCatAAA.png'
d = '11011110101011101010111010000101000111101101000010111001110101100011110101011011' * 46056 # 80*46056 = 3684480 handsome
d = d.encode()

def run():
    """
    Runs the method and returns the block magnitudes.

    :return: The block magnitudes.
    """
    capacity, additionalData = c.getImageFileCapacity(p)
    blockMagnitudes = c.insertData(p, pp, additionalData, d)


import cProfile
print('running')
cProfile.run('run()')
#'''












