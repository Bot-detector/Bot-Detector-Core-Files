FROM python:3.10-slim

ARG api_port
ENV UVICORN_PORT ${api_port}

ARG root_path
ENV UVICORN_ROOT_PATH ${root_path}

WORKDIR /project
COPY ./requirements.txt /project/requirements.txt

# required to install github.com/TheRealNoob/python-logging-loki.git
RUN apt update && \
    apt install git curl -y && \
    apt clean autoclean && \
    apt autoremove --yes && \
    rm -rf /var/lib/{apt,dpkg,cache,log}

RUN pip install --no-cache-dir -r /project/requirements.txt

COPY . /project/

CMD ["uvicorn", "api.app:app", "--proxy-headers", "--host", "0.0.0.0"] 
# CMD ["sh","-c", "uvicorn api.app:app --proxy-headers --host 0.0.0.0 --port ${port} --root-path ${path}"]