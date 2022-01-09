FROM python:3.10-slim

ARG api_port
ENV port ${api_port}

ARG root_path
ENV path ${root_path}

WORKDIR /root
COPY ./requirements.txt /root/requirements.txt

# required to install github.com/TheRealNoob/python-logging-loki.git
RUN apt update && \
    apt install git curl -y && \
    apt clean autoclean && \
    apt autoremove --yes && \
    rm -rf /var/lib/{apt,dpkg,cache,log}

RUN pip install --no-cache-dir -r /root/requirements.txt

COPY . /root/

CMD uvicorn api.app:app --proxy-headers --host 0.0.0.0 --port ${port} --root-path ${path}
