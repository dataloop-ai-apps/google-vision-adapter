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

    def add_box_annotation(self, item: dl.Item, builder: dl.AnnotationCollection, annotations, vision_type):
        """
        Adds a box annotation to a given annotation builder.

        Args:
            item (dl.Item): The item to which the annotation is related.
            builder (dl.AnnotationCollection) : The annotation builder to which the box annotation will be added.
            annotations : The annotations from the Google Vision API.
            vision_type (str): The type of processing to perform on the image.
        """
        self.logger.info('Adding box annotation')
        for annotation in annotations:
            if vision_type == 'text':
                label = 'text'
                description = annotation.description
            else:
                label = annotation.description
                description = None

            points = annotation.bounding_poly.vertices
            builder.add(annotation_definition=dl.Box(left=max(points[0].x, 0), top=max(points[0].y, 0), bottom=min(points[2].y, item.height), right=min(points[2].x, item.width), label=label, description=description))
        item.annotations.upload(builder)
        self.logger.info('Box annotation added')
