FROM python:3.9-slim

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN apt update && apt install git curl -y

RUN pip install --no-cache-dir -r /code/requirements.txt

COPY . /code

RUN mkdir logs && mkdir exports

CMD ["uvicorn", "api.app:app", "--proxy-headers", "--host", "0.0.0.0", "--port", "5000", "--root-path", "/dev"]
