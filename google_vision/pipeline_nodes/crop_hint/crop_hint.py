from google.cloud import vision
import dtlpy as dl
import tempfile
import logging
import base64
import json
import os
import cv2

logger = logging.getLogger(name='google-vision')

class ServiceRunner(dl.BaseServiceRunner):
    """
    ServiceRunner handles image cropping using Google Vision API's crop hints.

    Attributes:
        vision_client (vision.ImageAnnotatorClient): Client for Google Vision API.
    """
    def __init__(self):
        """
        Initializes the ServiceRunner with Google Vision API credentials.
        """
        self.logger = logger
        self.logger.info('Initializing Google Vision API client')
        raw_credentials = os.environ.get("GCP_SERVICE_ACCOUNT", None)
        if raw_credentials is None:
            raise ValueError(f"Missing GCP service account json.")

        try:
            decoded_credentials = base64.b64decode(raw_credentials).decode("utf-8")
            credentials_json = json.loads(decoded_credentials)
            credentials = json.loads(credentials_json['content'])
        except Exception:
            raise ValueError("Unable to decode the service account JSON. "
                             "Please refer to the following guide for proper usage of GCP service accounts with "
                             "Dataloop: https://github.com/dataloop-ai-apps/google-vision-adapter/blob/main/README.md")

        self.vision_client = vision.ImageAnnotatorClient.from_service_account_info(credentials)
        
    def crop_hint(self, item: dl.Item, context: dl.Context):
        """
        Detects crop hints in an image and creates a new cropped image.

        Args:
            item (dl.Item): The item containing the image.
            context (dl.Context): The execution context coming from pipeline node.

        Returns:
            dl.Item: The item with the cropped image.
        """
        self.logger.info('Starting crop hint detection.')

        # Download and load the image
        image_path = item.download()
        cv2_im = cv2.imread(image_path)
        self.logger.info('Image downloaded and loaded.')

        # Prepare the image for Google Vision API
        with open(image_path, "rb") as image_file:
            content = image_file.read()
        self.logger.info('Image prepared for Google Vision API.')

        # Get the crop ratio from the context
        node = context.node
        width = node.metadata['customNodeConfig']['width']
        height = node.metadata['customNodeConfig']['height']
        ratio = width / height
        ratio = round(ratio, 2)
        self.logger.info(f'Using crop ratio: {ratio}')

        # Perform crop hint detection
        crop_hints = self._get_crop_hints(content, ratio)
        points = crop_hints[0].bounding_poly.vertices

        # Crop the image using the detected hints
        cropped_image = cv2_im[points[0].y:points[2].y, points[0].x:points[2].x]
        self.logger.info(f'Image cropped: {points[0].x}, {points[0].y}, {points[2].x}, {points[2].y}')

        # Save and upload the cropped image
        crop_item = self._save_and_upload_cropped_image(cropped_image, item, width, height)
        return crop_item

    def _get_crop_hints(self, content, ratio):
        """
        Gets crop hints from Google Vision API.

        Args:
            content (bytes): The image content.
            ratio (float): The aspect ratio for crop hints.

        Returns:
            List[vision.CropHint]: The crop hints.
        """
        image = vision.Image(content=content)
        crop_hints_params = vision.CropHintsParams(aspect_ratios=[ratio])
        image_context = vision.ImageContext(crop_hints_params=crop_hints_params)
        response = self.vision_client.crop_hints(image=image, image_context=image_context)
        return response.crop_hints_annotation.crop_hints

    def _save_and_upload_cropped_image(self, cropped_image, item, width, height):
        """
        Saves the cropped image and uploads it to Dataloop.

        Args:
            cropped_image (np.array): The cropped image.
            item (dl.Item): The original item.
            ratio (float): The crop ratio.

        Returns:
            dl.Item: The uploaded cropped image item.
        """
        temp_items_path = tempfile.mkdtemp()
        name, ext = os.path.splitext(item.name)
        cropped_image_path = f'{name}_cropped_w_{width}_h_{height}.jpg'
        file_path = os.path.join(temp_items_path, cropped_image_path)
        cv2.imwrite(file_path, cropped_image)
        # Handling cropped items remote path
        item_remote_path = item.filename.split('/')[:-1]
        # Check if item_remote_path is empty or contains only an empty string
        if not item_remote_path or item_remote_path == ['']:
            remote_path = '/'
        else:
            remote_path = '/'.join(item_remote_path)
        remote_path = f"{remote_path}/cropped_items" if remote_path != '/' else '/cropped_items'
        
        crop_item = item.dataset.items.upload(local_path=file_path, remote_path=remote_path)
        self.logger.info('Cropped image saved and uploaded.')
        return crop_item
