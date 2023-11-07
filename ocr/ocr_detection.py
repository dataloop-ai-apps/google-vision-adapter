import json
import os
import dtlpy as dl
from google.cloud import vision


class ServiceRunner(dl.BaseServiceRunner):
    def __init__(self, integration_name):
        credentials = os.environ.get(integration_name)
        credentials = json.loads(credentials)
        self.vision_client = vision.ImageAnnotatorClient.from_service_account_info(credentials)

    def text_detection(self, item):
        image_path = item.download()
        with open(image_path, "rb") as image_file:
            content = image_file.read()

        image = vision.Image(content=content)
        request = vision.AnnotateImageRequest(image=image,
                                              features=[vision.Feature(type_=vision.Feature.Type.TEXT_DETECTION)])

        response = self.vision_client.annotate_image(request=request)

        builder = item.annotations.builder()
        for annotation in response.text_annotations:
            points = annotation.bounding_poly.vertices
            builder.add(annotation_definition=dl.Box(top=points[0].y,
                                                     left=points[0].x,
                                                     bottom=points[2].y,
                                                     right=points[2].x,
                                                     label=annotation.description))
        item.annotations.upload(builder)
