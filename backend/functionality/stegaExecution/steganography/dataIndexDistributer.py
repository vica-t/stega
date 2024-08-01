import numpy as np


class DataIndexDistributer:
    """

    DataIndexDistributer
    ===================

    The `DataIndexDistributer` class provides methods for calculating pixel coordinates based on image indexes.

    Methods
    -------

    getPixelCoords(imageWidth, imageHeight)
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    Calculates the pixel coordinates for an image given the image width and height.

    Parameters:
    - `imageWidth` (int): The width of the image.
    - `imageHeight` (int): The height of the image.

    Returns:
    - `coords` (numpy.ndarray): An array of coordinate tuples representing the pixel coordinates.

    getIndexes(n)
    ~~~~~~~~~~~~
    Generates even and odd numbers and interleaves them.

    Parameters:
    - `n` (int): The total number of indexes to generate.

    Returns:
    - `result` (numpy.ndarray): An array of indexes.

    calculatePixelCoordsByIndexes(imageWidth, indexes)
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    Computes the pixel coordinates given the image width and indexes.

    Parameters:
    - `imageWidth` (int): The width of the image.
    - `indexes` (numpy.ndarray): An array of indexes.

    Returns:
    - `pixelCoords` (numpy.ndarray): An array of coordinate tuples representing the pixel coordinates.

    """

    def getPixelCoords(self, imageWidth, imageHeigth):
        """
        Get the pixel coordinates based on the image width and height.

        :param imageWidth: The width of the image.
        :param imageHeight: The height of the image.
        :return: The pixel coordinates.
        """
        indexes = self.getIndexes(imageWidth*imageHeigth)
        coords = self.calculatePixelCoordsByIndexes(imageWidth, indexes)
        return coords
    
    def getIndexes(self, n):
        """
        Generate a list of indexes in a specific order.

        :param n: The length of the list.
        :return: The list of indexes.
        """
        # Generate all even and odd numbers
        evens = np.arange(0, n, 2)
        odds = np.arange(1, n, 2)
        
        # Interleave evens: one from the beginning, one from the end, alternately
        evenOrdered = np.empty_like(evens)
        evenOrdered[0::2] = evens[:len(evens)//2]
        evenOrdered[1::2] = evens[len(evens)//2:][::-1]

        # Interleave odds: starting from the center outward
        oddOrdered = np.empty_like(odds)
        mid = len(odds) // 2
        
        if len(odds) % 2 == 0:
            oddOrdered[0::2] = odds[mid:][::-1]
            oddOrdered[1::2] = odds[:mid]
        else:
            oddOrdered[0::2] = odds[mid:]
            oddOrdered[1::2] = odds[:mid][::-1]

        # Combine even and odd lists
        result = np.concatenate((evenOrdered, oddOrdered))
        return result

    def calculatePixelCoordsByIndexes(self, imageWidth, indexes):
        """
        Calculate the pixel coordinates based on the given indexes and image width.

        :param imageWidth: The width of the image.
        :param indexes: The indexes of the pixels.
        :return: The pixel coordinates as a numpy array of coordinate tuples.
        """
        # Compute the row (i // imageWidth) and column (i % imageWidth) coordinates
        rows = indexes // imageWidth
        cols = indexes % imageWidth
        
        # Combine rows and cols into a single array of coordinate tuples
        pixelCoords = np.column_stack((rows, cols))
        print(pixelCoords)
        return pixelCoords

