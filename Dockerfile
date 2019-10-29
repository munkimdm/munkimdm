FROM python:3.7

WORKDIR /app

COPY src/requirements.txt ./

RUN pip install -r requirements.txt

COPY src /app

EXPOSE 8080
CMD [ "python", "munkimdm.py" ]
