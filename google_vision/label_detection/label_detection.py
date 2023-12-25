from google.cloud import vision
from google_vision.base import VisionBase
import dtlpy as dl


class ServiceRunner(VisionBase):
    """
    A class to hande label detection using Google Vision API.

    Attributes:
        vision_client (vision.ImageAnnotatorClient): A client for interacting with the Google Vision API.
    """

    def label_detection(self, item: dl.Item):
        """
        Detects and add labels for an image.

        Args:
            item (dl.Item): The item for label detection.
        """
        self.logger.info('Detecting labels')
        image = self.load_image(item)
        response = self.get_response(image, vision.Feature.Type.LABEL_DETECTION)

        builder = item.annotations.builder()
        for annotation in response.label_annotations:
            builder.add(annotation_definition=dl.Classification(label=annotation.description))
        item.annotations.upload(builder)
