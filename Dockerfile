# Use an official Python runtime as a parent image
FROM shadimahameeddl/vision-test:latest

# Install any needed packages specified in requirements.txt
USER root
RUN apt-get update

RUN apt-get install libgl1-mesa-glx -y

# Install any Python packages
RUN pip install --no-cache-dir opencv-python

RUN useradd -m myuser
USER myuser