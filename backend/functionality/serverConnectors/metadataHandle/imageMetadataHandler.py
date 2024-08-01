from PIL import Image, PngImagePlugin, UnidentifiedImageError
#from metadataHandler import MetadataHandler


class ImageMetadataHandler:
    """A class that handles image metadata.

    This class provides methods to retrieve and add metadata to an image file.

    """
    def __init__(self):
        """
        Constructor for the class.

        :param self: The instance of the class being created.
        :type self: object
        """
        pass
    
    
    
    def getMetadata(self, filePath):
        """
        Returns the requested metadata from an image file.

        :param filePath: str - The file path of the image.
        :return: str - The requested metadata value.
                 If the metadata is not found, returns 0.
                 If the image file couldn't be opened, returns -1.
                 If an unknown error occurs, returns -2.
        """
        try:
            with Image.open(filePath) as imageFile:
                metadata = imageFile.text
            reqMetadata = metadata['identifier']
            return reqMetadata
        except KeyError:
            print('Requested metadata not found')
            return 0
        except UnidentifiedImageError:
            print('Couldn\'t open image')
            return -1
        except Exception as e:
            print('Unknown error')
            print(e)
            return -2
    
    
    def addMetadata(self, filePath, data):
        """
        :param filePath: str - The path of the image file to add metadata to.
        :param data: str - The metadata to be added.
        :return: int - Returns 1 if metadata is successfully added, -1 if the image file cannot be opened, -2 for unknown errors.
        """
        try:
            with Image.open(filePath) as imageFile:
                existingMetadata = imageFile.info.copy()
                updatedMetadata = PngImagePlugin.PngInfo()
                identifier = False
                for key, value in existingMetadata.items():
                    if key == 'identifier':
                        if not identifier:
                            updatedMetadata.add_text('identifier', data)
                            identifier = True
                    else:
                        updatedMetadata.add_text(str(key), str(value))
                if not identifier:
                    updatedMetadata.add_text('identifier', data)
                imageFile.save(filePath, pnginfo=updatedMetadata)
            return 1
        except UnidentifiedImageError:
            print('Couldn\'t open image')
            return -1
