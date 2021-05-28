FROM python:3

WORKDIR /home

COPY . .
RUN pip3 install -r requirements.txt --no-cache-dir

CMD ["python3", "app.py"]