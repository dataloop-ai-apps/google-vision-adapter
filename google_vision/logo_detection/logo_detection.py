from google_vision.base import VisionBase
import dtlpy as dl


class ServiceRunner(VisionBase):
    """
    A class to hande logo detection using Google Vision API.

    Attributes:
        vision_client (vision.ImageAnnotatorClient): A client for interacting with the Google Vision API.
    """

    def logo_detection(self, item: dl.Item):
        """
        Detects and annotates logos within an image.

        Args:
            item (dl.Item): The item containing the image for logo detection.
        """
        self.logger.info('Detecting logos')
        image = self.load_image(item)
        response = self.vision_client.logo_detection(image=image)

        builder = item.annotations.builder()
        self.add_box_annotation(item, builder, response.logo_annotations, "logo")

        return item
