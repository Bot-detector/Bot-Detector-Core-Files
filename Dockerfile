FROM python:3.10-slim

WORKDIR /code
COPY ./requirements.txt /code/requirements.txt

# install git & curl -- but why?
RUN apt update && \
    apt install git curl -y && \
    apt clean autoclean && \
    apt autoremove --yes && \
    rm -rf /var/lib/{apt,dpkg,cache,log}

RUN pip install --no-cache-dir -r /code/requirements.txt

COPY . /code

CMD ["uvicorn", "api.app:app", "--proxy-headers", "--host", "0.0.0.0", "--port", "5000", "--root-path", "/dev"]
