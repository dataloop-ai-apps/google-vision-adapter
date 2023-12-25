import json
import os
import dtlpy as dl
from google.cloud import vision
import logging

logger = logging.getLogger(name='google-vision')


class VisionBase(dl.BaseServiceRunner):
    """
    A class to handle various image processing tasks using Google Vision API.

    Attributes:
        vision_client (vision.ImageAnnotatorClient): A client for interacting with the Google Vision API.
    """

    def __init__(self, integration_name):
        """
        Initializes the ServiceRunner with Google Vision API credentials.

        Args:
            integration_name (str): The name of the environment variable that contains the Vision API credentials.
        """
        self.logger = logger
        self.logger.info('Initializing Google Vision API client')
        self.logger.info('Loading credentials from environment variable: {}'.format(integration_name))
        credentials = os.environ.get(integration_name)
        credentials = json.loads(credentials)
        self.vision_client = vision.ImageAnnotatorClient.from_service_account_info(credentials)

    def load_image(self, item):
        """
        Loads an image from a given item.

        Args:
            item (dl.Item): An item from which to load the image.

        Returns:
            vision.Image: The loaded image ready for processing.
        """
        self.logger.info('Loading image from item: {}'.format(item.id))
        image_path = item.download()
        with open(image_path, "rb") as image_file:
            content = image_file.read()
        return vision.Image(content=content)

    def get_response(self, image, type):
        """
        Gets a response from the Google Vision API.

        Args:
            image (vision.Image): The image to process.
            type (vision.Feature.Type): The type of processing to perform on the image.

        Returns:
            vision.AnnotateImageResponse: The response from the Google Vision API.
        """
        self.logger.info('Getting response from Google Vision API')
        request = vision.AnnotateImageRequest(image=image,
                                              features=[vision.Feature(type_=type)])
        return self.vision_client.annotate_image(request=request)

    def add_box_annotation(self, builder: dl.AnnotationCollection, x1, y1, x2, y2, label):
        """
        Adds a box annotation to a given annotation builder.

        Args:
            item (dl.Item): The item to which the annotation is related.
            builder (dl.AnnotationCollection) : The annotation builder to which the box annotation will be added.
            x1 (float): The x-coordinate of the top left corner of the box.
            y1 (float): The y-coordinate of the top left corner of the box.
            x2 (float): The x-coordinate of the bottom right corner of the box.
            y2 (float): The y-coordinate of the bottom right corner of the box.
            label (str): The label for the box annotation.
        """
        self.logger.info('Adding box annotation')
        builder.add(annotation_definition=dl.Box(top=y1,
                                                 left=x1,
                                                 bottom=y2,
                                                 right=x2,
                                                 label=label))
