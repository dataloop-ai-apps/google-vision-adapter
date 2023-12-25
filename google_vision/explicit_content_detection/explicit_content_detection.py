from google.cloud import vision
from google_vision.base import VisionBase
import dtlpy as dl


class ServiceRunner(VisionBase):
    """
    A class to hande explicit content detection using Google Vision API.

    Attributes:
        vision_client (vision.ImageAnnotatorClient): A client for interacting with the Google Vision API.
    """

    def explicit_content_detection(self, item: dl.Item):
        """
        Detets explicit content within an image and if relevant, adds label to the item.
        Options are : "adult", "spoof", "medical", "violence", "racy".

        Args:
            item (dl.Item): The item containing the image for logo detection.
        """
        self.logger.info('Detecting explicit content')
        image = self.load_image(item)
        response = self.vision_client.safe_search_detection(image=image)
        safe = vision.AnnotateImageResponse.to_dict(response)
        builder = item.annotations.builder()
        for key, value in safe['safe_search_annotation'].items():
            if value > 3:
                builder.add(annotation_definition=dl.Classification(label=key))
        item.annotations.upload(builder)
