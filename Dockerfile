FROM python:3.7

WORKDIR /app

COPY src/requirements.txt ./

RUN pip install -r requirements.txt

COPY src /app

EXPOSE 8000
CMD [ "gunicorn", "-b", "0.0.0.0:8000", "-w", "4", "munkimdm:application" ]
