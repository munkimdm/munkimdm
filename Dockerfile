FROM python:3.7

WORKDIR /app

COPY munkimdm/requirements.txt ./

RUN pip install -r requirements.txt

COPY munkimdm /app
