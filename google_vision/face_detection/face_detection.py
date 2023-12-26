import dtlpy as dl
from google.cloud import vision
from google_vision.base import VisionBase


class ServiceRunner(VisionBase):
    """
    A class to hande face detection using Google Vision API.

    Attributes:
        vision_client (vision.ImageAnnotatorClient): A client for interacting with the Google Vision API.
    """

    def face_detection(self, item: dl.Item):
        """
        Detects and annotates faces within an image.

        Args:
            item (dl.Item): The item containing the image for face detection.
        """
        self.logger.info('Detecting faces')
        image = self.load_image(item)
        response = self.get_response(image, vision.Feature.Type.FACE_DETECTION)

        builder = item.annotations.builder()
        self.add_box_annotation(item, builder, response.face_annotations, "face")
