FROM python:3.8

WORKDIR /app
COPY ./requirements.txt ./
RUN pip install -r ./requirements.txt
COPY . .


#CMD ["python","webserver/notification_webserver.py"]
CMD ["gunicorn","--workers","3","--bind", "0.0.0.0:5000","--preload","-t 60","webserver.notification_webserver:app"]