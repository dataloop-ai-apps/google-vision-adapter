import json
import os
import dtlpy as dl
from google.cloud import vision


class ServiceRunner(dl.BaseServiceRunner):
    def __init__(self, integration_name):
        credentials = os.environ.get(integration_name)
        credentials = json.loads(credentials)
        self.vision_client = vision.ImageAnnotatorClient.from_service_account_info(credentials)

    def obj_detection(self, item):
        height = item.height
        width = item.width
        image_path = item.download()
        with open(image_path, "rb") as image_file:
            content = image_file.read()

        image = vision.Image(content=content)
        objects = self.vision_client.object_localization(image=image).localized_object_annotations

        print(f"Number of objects found: {len(objects)}")

        builder = item.annotations.builder()
        for object_ in objects:
            print(f"\n{object_.name} (confidence: {object_.score})")
            normalized_points = object_.bounding_poly.normalized_vertices
            x1 = normalized_points[0].x * width
            y1 = normalized_points[0].y * height
            x2 = normalized_points[2].x * width
            y2 = normalized_points[2].y * height
            builder.add(annotation_definition=dl.Box(top=y1,
                                                     left=x1,
                                                     bottom=y2,
                                                     right=x2,
                                                     label=object_.name))
        item.annotations.upload(builder)
