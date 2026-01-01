FROM hub.dataloop.ai/dtlpy-runner-images/cpu:python3.10_opencv

RUN apt-get update && apt-get install libgl1-mesa-glx -y
COPY requirements.txt /tmp
RUN ${DL_PYTHON_EXECUTABLE} -m pip install -r /tmp/requirements.txt


# docker build --no-cache -t gcr.io/viewo-g/piper/agent/runner/apps/google-vision:0.0.1 -f Dockerfile .
# docker run -it gcr.io/viewo-g/piper/agent/runner/apps/google-vision:0.0.1 bash
# docker push gcr.io/viewo-g/piper/agent/runner/apps/google-vision:0.0.1
