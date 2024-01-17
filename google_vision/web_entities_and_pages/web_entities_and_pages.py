from google.cloud import vision
from google_vision.base import VisionBase
import dtlpy as dl


class ServiceRunner(VisionBase):
    """
    A class to hande web entities and pages detection using Google Vision API.

    Attributes:
        vision_client (vision.ImageAnnotatorClient): A client for interacting with the Google Vision API.
    """

    def web_detection(self, item: dl.Item):
        """
        Detects and and add to metadata web entities and pages within an image.

        Args:
            item (dl.Item): The item containing the image for logo detection.
        """
        self.logger.info('Detecting web informations')
        image = self.load_image(item)
        response = self.vision_client.web_detection(image=image)
        annotations = vision.AnnotateImageResponse.to_dict(response)
        if 'user' not in item.metadata:
            item.metadata['user'] = {}
        item.metadata['user']['google_vision_web_detection'] = annotations['web_detection']
        item.update()
        # add to user metadata

        return item
