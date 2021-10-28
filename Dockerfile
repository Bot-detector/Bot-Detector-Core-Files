FROM python:3.9

WORKDIR /home

COPY . .

RUN pip3 install -r requirements.txt --no-cache-dir

RUN mkdir logs

CMD ["gunicorn","--bind","0.0.0.0:4000","app:app"]