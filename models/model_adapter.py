from google.cloud import vision
import dtlpy as dl
import logging
import base64
import json
import os

from jupyter_client.adapter import adapters

logger = logging.getLogger(name="google-vision")


class ModelAdapter(dl.BaseModelAdapter):
    """
    A class to handle various image processing tasks using Google Vision API.

    Attributes:
        vision_client (vision.ImageAnnotatorClient): A client for interacting with the Google Vision API.
    """

    def load(self, local_path, **kwargs):
        """
        Initializes the ServiceRunner with Google Vision API credentials.
        """
        self.logger = logger
        self.logger.info("Initializing Google Vision API client")
        raw_credentials = os.environ.get("GCP_SERVICE_ACCOUNT", None)
        if raw_credentials is None:
            raise ValueError("Missing GCP service account json.")

        try:
            decoded_credentials = base64.b64decode(raw_credentials).decode("utf-8")
            credentials_json = json.loads(decoded_credentials)
            credentials = json.loads(credentials_json['content'])
        except (json.JSONDecodeError, UnicodeDecodeError, base64.binascii.Error) as exc:
            raise ValueError(
                "Unable to decode the service account JSON. "
                "Please refer to the following guide for proper usage of GCP service accounts with "
                "Dataloop: https://github.com/dataloop-ai-apps/google-vision-adapter/blob/main/README.md"
            ) from exc

        self.vision_client = vision.ImageAnnotatorClient.from_service_account_info(credentials)

    def prepare_item_func(self, item):
        """
        Loads an image from a given item.

        Args:
            item (dl.Item): An item from which to load the image.

        Returns:
            vision.Image: The loaded image ready for processing.
        """
        self.logger.info("Loading image from item: {}".format(item.id))
        image_path = item.download()
        with open(image_path, "rb") as image_file:
            content = image_file.read()

        return item, vision.Image(content=content)

    def get_response(self, image, type):
        """
        Gets a response from the Google Vision API.

        Args:
            image (vision.Image): The image to process.
            type (vision.Feature.Type): The type of processing to perform on the image.

        Returns:
            vision.AnnotateImageResponse: The response from the Google Vision API.
        """
        self.logger.info("Getting response from Google Vision API")
        request = vision.AnnotateImageRequest(image=image, features=[vision.Feature(type_=type)])
        return self.vision_client.annotate_image(request=request)

    def box_annotations(self, response, item: dl.Item, vision_type: str, item_annotation: dl.AnnotationCollection):
        self.logger.info(f"Detecting {vision_type}")

        if vision_type == "text":
            annotation_type = "text_annotations"
        elif vision_type == "face":
            annotation_type = "face_annotations"
        else:
            annotation_type = "logo_annotations"

        annotations = getattr(response, annotation_type, [])
        for annotation in annotations:
            label = annotation.description
            points = annotation.bounding_poly.vertices

            # if the model doesn't contain confidence
            confidence = round(getattr(annotation, "detection_confidence", 1.0), 3)
            # Add box annotations
            item_annotation.add(
                dl.Box(
                    left=max(points[0].x, 0),
                    top=max(points[0].y, 0),
                    bottom=min(points[2].y, item.height),
                    right=min(points[2].x, item.width),
                    label=label
                ),
                model_info={"name": self.model_entity.name, "model_id": self.model_entity.id, "confidence": confidence},
            )

        return item_annotation

    def object_detection(self, image, item: dl.Item, item_annotation: dl.AnnotationCollection):
        self.logger.info("Detecting objects")
        height = item.height
        width = item.width
        objects = self.vision_client.object_localization(image=image).localized_object_annotations
        self.logger.info("Number of objects found: {}".format(len(objects)))
        for object_ in objects:
            print(f"\n{object_.name} (confidence: {object_.score})")
            normalized_points = object_.bounding_poly.normalized_vertices
            x1 = normalized_points[0].x * width
            y1 = normalized_points[0].y * height
            x2 = normalized_points[2].x * width
            y2 = normalized_points[2].y * height
            item_annotation.add(
                dl.Box(left=x1, top=y1, right=x2, bottom=y2, label=object_.name),
                model_info={
                    "name": self.model_entity.name,
                    "model_id": self.model_entity.id,
                    "confidence": round(object_.score, 3),
                },
            )

        return item_annotation

    def explicit_content(self, image, item_annotation: dl.AnnotationCollection):
        self.logger.info("Detecting explicit content")
        likelihood_threshold = self.configuration.get(
            "likelihood_threshold", 0
        )  # default is 0, show likelihood for all categories
        response = self.vision_client.safe_search_detection(image=image)
        safe = vision.AnnotateImageResponse.to_dict(response)
        # Likelihood for each one of the categories
        for key, value in safe["safe_search_annotation"].items():
            if value >= likelihood_threshold:
                item_annotation.add(
                    annotation_definition=dl.Classification(label=key),
                    model_info={
                        "name": self.model_entity.name,
                        "model_id": self.model_entity.id,
                        "confidence": value / 5,  # Maximum value is 5
                    },
                )

        return item_annotation

    def web_detection(self, image, item: dl.Item, item_annotation: dl.AnnotationCollection):
        self.logger.info("Detecting web informations")
        response = self.vision_client.web_detection(image=image)
        annotations = vision.AnnotateImageResponse.to_dict(response)
        if "user" not in item.metadata:
            item.metadata["user"] = {}

        item.metadata["user"]["google_vision_web_detection"] = annotations["web_detection"]
        item.update()
        self.logger.info("Web detection was uploaded to item {item} metadata")

        return item_annotation

    def label_detection(self, image, item_annotation: dl.AnnotationCollection):
        self.logger.info("Detecting labels")
        response = self.vision_client.label_detection(image=image)
        label_annotations = response.label_annotations
        for annotation in label_annotations:
            item_annotation.add(
                dl.Classification(label=annotation.description),
                model_info={
                    "name": self.model_entity.name,
                    "model_id": self.model_entity.id,
                    "confidence": round(annotation.score, 3),
                },
            )

        return item_annotation

    def crop_hint(self, image, item: dl.Item, item_annotation: dl.AnnotationCollection):
        """
        Detects crop hints in an image and creates a new cropped image.

        Args:
            item (dl.Item): The item containing the image.
            context (dl.Context): The execution context coming from pipeline node.

        Returns:
            dl.Item: The item with the cropped image.
        """
        self.logger.info("Starting crop hint detection.")

        width = self.configuration.get("width", 1)
        height = self.configuration.get("height", 1)
        ratio = width / height
        ratio = round(ratio, 2)
        self.logger.info(f"Using crop ratio: {ratio}")

        # Perform crop hint detection
        crop_hints_params = vision.CropHintsParams(aspect_ratios=[ratio])
        image_context = vision.ImageContext(crop_hints_params=crop_hints_params)
        response = self.vision_client.crop_hints(image=image, image_context=image_context)
        crop_hints = response.crop_hints_annotation.crop_hints
        points = crop_hints[0].bounding_poly.vertices

        item_annotation.add(
            dl.Box(
                left=max(points[0].x, 0),
                top=max(points[0].y, 0),
                bottom=min(points[2].y, item.height),
                right=min(points[2].x, item.width),
                label="Cropped Hint",
                description="cropped_hint",
            ),
            model_info={"name": self.model_entity.name, 
                        "model_id": self.model_entity.id, 
                        "confidence": crop_hints[0].confidence},
        )

        return item_annotation

    def predict(self, batch, **kwargs):
        batch_annotations = list()
        vision_type = self.configuration.get("vision_type")
        if vision_type is None:
            raise ValueError("Vision type is not set. Please set the vision type in the model configuration.")

        for item, image in batch:
            item_annotation = dl.AnnotationCollection()

            #############
            # Crop Hint #
            #############

            if vision_type == "crop_hint":
                annotations = self.crop_hint(image=image, item=item, item_annotation=item_annotation)

            ##################
            # Classification #
            ##################

            # Explicit Content
            if vision_type == "explicit_content":
                annotations = self.explicit_content(image=image, item_annotation=item_annotation)

            # Label Detection
            elif vision_type == "label":
                annotations = self.label_detection(image=image, item_annotation=item_annotation)

            ######################
            # Upload to Metadata #
            ######################

            # Web Detection
            elif vision_type == "web_detection":
                annotations = self.web_detection(image=image, item=item, item_annotation=item_annotation)

            ####################
            # Object Detection #
            ####################

            # Object Detection
            elif vision_type == "object":
                annotations = self.object_detection(image=image, item=item, item_annotation=item_annotation)

            # Logo/Face/Text Detection
            else:
                vision_type_mapping = {
                    "text": vision.Feature.Type.TEXT_DETECTION,
                    "face": vision.Feature.Type.FACE_DETECTION,
                }
                if vision_type == "logo":
                    response = self.vision_client.logo_detection(image=image)
                else:
                    response = self.get_response(image, vision_type_mapping.get(vision_type))

                annotations = self.box_annotations(
                    response=response, item=item, vision_type=vision_type, item_annotation=item_annotation
                )

            batch_annotations.append(annotations)

        return batch_annotations
