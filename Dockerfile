FROM python:latest
COPY . /
RUN pip3 install -r requirements.txt
EXPOSE 5000
CMD ["waitress-serve", "--port=5000", "--host=0.0.0.0", "app:app"]
 