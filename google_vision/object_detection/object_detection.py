from google_vision.base import VisionBase
import dtlpy as dl


class ServiceRunner(VisionBase):
    """
    A class to hande object detection using Google Vision API.

    Attributes:
        vision_client (vision.ImageAnnotatorClient): A client for interacting with the Google Vision API.
    """

    def obj_detection(self, item: dl.Item):
        """
        Detects and annotates objects within an image. For classes please check: https://cloud.google.com/vision/docs/object-localizer

        Args:
            item (dl.Item): The item containing the image for object detection.
        """
        self.logger.info('Detecting objects')
        height = item.height
        width = item.width
        image = self.load_image(item)
        objects = self.vision_client.object_localization(image=image).localized_object_annotations

        self.logger.info('Number of objects found: {}'.format(len(objects)))

        builder = item.annotations.builder()
        for object_ in objects:
            print(f"\n{object_.name} (confidence: {object_.score})")
            normalized_points = object_.bounding_poly.normalized_vertices
            x1 = normalized_points[0].x * width
            y1 = normalized_points[0].y * height
            x2 = normalized_points[2].x * width
            y2 = normalized_points[2].y * height
            builder.add(annotation_definition=dl.Box(left=x1, top=y1, right=x2, bottom=y2, label=object_.name))
        item.annotations.upload(builder)

        return item
