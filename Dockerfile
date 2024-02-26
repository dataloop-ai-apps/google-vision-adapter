FROM dataloopai/dtlpy-agent:cpu.py3.8.opencv4.7

USER root
RUN apt-get update && apt-get install libgl1-mesa-glx -y
USER 1000
COPY requirements.txt /tmp
RUN pip install --user -r /tmp/requirements.txt


# docker build --no-cache -t gcr.io/viewo-g/piper/agent/runner/cpu/google_vision:0.4.0 -f Dockerfile .
# docker run -it gcr.io/viewo-g/piper/agent/runner/cpu/google_vision:0.4.0 bash
# docker push gcr.io/viewo-g/piper/agent/runner/cpu/google_vision:0.4.0
