from google.cloud import vision
from google_vision.base import VisionBase
import dtlpy as dl


class ServiceRunner(VisionBase):
    """
    A class to hande text detection using Google Vision API.

    Attributes:
        vision_client (vision.ImageAnnotatorClient): A client for interacting with the Google Vision API.
    """

    def text_detection(self, item: dl.Item):
        """
        Detects and annotates text within an image.

        Args:
            item (dl.Item): The item containing the image for text detection.
        """
        self.logger.info('Detecting text')
        image = self.load_image(item)
        response = self.get_response(image, vision.Feature.Type.TEXT_DETECTION)
        builder = item.annotations.builder()
        self.add_box_annotation(item, builder, response.text_annotations, "text")

        return item
