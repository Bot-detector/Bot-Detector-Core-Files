FROM python:3.10-slim as base

ARG api_port
ENV UVICORN_PORT ${api_port}

ARG root_path
ENV UVICORN_ROOT_PATH ${root_path}

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

# set the working directory
WORKDIR /project

# install dependencies
COPY ./requirements.txt /project
RUN pip install --no-cache-dir -r requirements.txt

# copy the scripts to the folder
COPY ./src /project/src

# production image
FROM base as production
# Creates a non-root user with an explicit UID and adds permission to access the /project folder
RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /project
USER appuser

CMD ["uvicorn", "api.app:app", "--proxy-headers", "--host", "0.0.0.0"]
