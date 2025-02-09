# Google Vision Adapter

This repository provides an integration between **Dataloop** and the **Google Vision** API.

---

## Overview

- **Purpose**  
  Acts as an adapter that allows images or other media to be sent to the Google Vision API for analysis, inside a Dataloop pipeline node. It then returns structured results, such as labels, bounding boxes, recognized text, and more.

- **Technology Stack**  
  - **Python**
  - **Google Cloud Vision**

---

## Google Vision Functions Used

Below is a list of the main Google Vision detection nodes:

1. **Text Detection**  
   *Detects and extracts text from an image. Returns the recognized text along with bounding boxes for each piece of identified text.*

2. **Label Detection**  
   *Detects and extracts information about entities in an image, across a broad group of categories. Returns different labels found.*

3. **Face Detection**  
   *Detects human faces within an image. Returns bounding boxes for each face and can include additional attributes (e.g., likelihood of joy, sorrow, anger, and surprise).*

4. **Logo Detection**  
   *Identifies logos from well-known brands within the image. Returns bounding boxes and the corresponding brand names for each detected logo.*

5. **Object Detection**  
   *Performs object localization, returning bounding boxes and classification labels for each recognized object in the image.*

6. **Explicit Content Detection**  
   *Evaluates the image for explicit or sensitive content (e.g., adult, racy, violence). Returns labels of explicit content found.*

7. **Web Detection**  
   *Detects and add to metadata web entities and pages found within an image.*

8. **Crop Hints**  
   *Handles image cropping using Google Vision crop hints. Return cropped image.*

---
## Setting Up Your GCP Project

To use these nodes, you need a Google Cloud Platform (GCP) project. Follow these steps to get started:

### 1. Enable the Cloud Vision AI API
   - Navigate to the [Cloud Vision API](https://console.developers.google.com/apis/api/vision.googleapis.com) in the GCP Console.
   - Enable the Cloud Vision AI API.

### 2. Create a GCP [Service Account](https://docs.dataloop.ai/docs/private-key-integration?highlight=create%20service%20account)
   - Go to the IAM & Admin section in the GCP Console.
   - Create a new service account.
   - Generate a new key and download the service account JSON file.

## Integrating Google Cloud Vision AI API with Dataloop Platform

   - Visit the [Dataloop Marketplace](https://docs.dataloop.ai/docs/marketplace), under Applications tab.
   - Select the application and click on "Install" and then "Proceed".
![Marketplace](assets/marketplace.png)
   - Select an existing GCP integration or add a new one by importing the JSON file you previously downloaded.
![Create Integration](assets/add_integration.png)
   - Install the application.
![Integration](assets/add_integration_to_app.png)


## Use the application in a pipeline
   - After installing the application, you can use the relevant node in a pipeline under the category 'Google Vision'.
![Pipeline](assets/pipeline.png)

## License

The code in this repository is licensed under the [Apache License 2.0](LICENSE).

### Attributions & Disclaimer

This repository provides an integration between **Dataloop** and the **Google Vision API**. It acts as an adapter that allows images or other media to be sent to the Google Vision API for analysis within a **Dataloop pipeline node**. 

This repository is **not affiliated with Google**. It provides an adapter for Google Vision API, but does not include or distribute any proprietary Google code or intellectual property.

While the code in this repository is open-sourced under the **Apache License 2.0**, the **use of the Google Vision API is subject to Google's licensing terms**, including:

- [Google Cloud Platform Terms of Service](https://cloud.google.com/terms)
- [Google Vision API Pricing & Usage Terms](https://cloud.google.com/vision/pricing)

This application is provided **"as is"** under the terms of the **Apache License 2.0**. Dataloop makes no warranties or guarantees regarding its performance, functionality, or legal compliance when used with the Google Vision API.

### Additional Resources

For more information about the **Google Vision API**, please visit:
- [Google Vision API Overview](https://cloud.google.com/vision)
- [Google Vision API Documentation](https://cloud.google.com/vision/docs)
- [Google Vision API Pricing](https://cloud.google.com/vision/pricing)

---

For additional assistance or inquiries, please refer to the Dataloop documentation or contact support.
