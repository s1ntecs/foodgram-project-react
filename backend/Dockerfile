FROM python:3.9-slim
LABEL owner="sintecs@list.com"

WORKDIR /code
COPY requirements.txt .

RUN apt-get update && apt-get upgrade -y && \
    pip install --upgrade pip && pip install -r requirements.txt

COPY . ./


CMD gunicorn foodgram.wsgi:application --bind 0.0.0.0:8000