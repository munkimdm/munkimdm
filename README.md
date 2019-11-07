# munkimdm

Flask app for connecting [Munki](https://github.com/munki/munki) and [MicroMDM](https://github.com/micromdm/micromdm).

## Background reading

- [Creating MunkiMDM Part I](https://joncrain.github.io/2018/11/01/micromdm_munki.html)
- [Creating MunkiMDM Part II](https://joncrain.github.io/2018/11/06/micromdm_munki_partii.html)
- [Creating MunkiMDM Part III](https://joncrain.github.io/2018/11/08/micromdm_munki_partiii.html)
- [MunkiMDM Update](https://joncrain.github.io/2019/01/29/micromdm_munki_update.html)

## Environment File

Environment variables should be stored in a `.env` file in the following format:

    BASIC_AUTH_USERNAME=username
    BASIC_AUTH_PASSWORD=password
    MICROMDM_URL=https://mdm.domain.org
    MICROMDM_TOKEN=mdm_token
    MUNKI_REPO_PATH=munki_path

## Running with Docker

To run the Flask application within Docker, all that is required is the following:

    docker-compose up --build

    Creating network "munkimdm_default" with the default driver
    Building munkimdm
    Step 1/5 : FROM python:3.7
     ---> 023b89039ba4
    Step 2/5 : WORKDIR /app
     ---> Using cache
     ---> 64bc1083763e
    Step 3/5 : COPY munkimdm/requirements.txt ./
     ---> Using cache
     ---> eda553a4bd87
    Step 4/5 : RUN pip install -r requirements.txt
     ---> Using cache
     ---> 5c48d425f9e8
    Step 5/5 : COPY munkimdm /app
     ---> Using cache
     ---> c911195a93a7
    Successfully built c911195a93a7
    Successfully tagged munkimdm_munkimdm:latest
    Creating munkimdm_munkimdm_1 ... done
    Attaching to munkimdm_munkimdm_1
    munkimdm_1  | [2019-11-06 20:00:54 +0000] [1] [INFO] Starting gunicorn 19.9.0
    munkimdm_1  | [2019-11-06 20:00:54 +0000] [1] [INFO] Listening at: http://0.0.0.0:8000 (1)
    munkimdm_1  | [2019-11-06 20:00:54 +0000] [1] [INFO] Using worker: sync
    munkimdm_1  | [2019-11-06 20:00:54 +0000] [8] [INFO] Booting worker with pid: 8
    ...

_Note_: this container is actively attached. If you would like to run it in the background you will need to pass the `-d` flag to `docker-compose`.

Afterwards, you can check on the status of the container using `docker-compose ps`:

           Name                      Command               State           Ports
    -------------------------------------------------------------------------------------
    munkimdm_munkimdm_1   gunicorn -b 0.0.0.0:8000 m ...   Up      0.0.0.0:8000->8000/tcp

## Submitting with Curl

     curl -H "Content-Type: application/json" -d '{"uddid": "example_udid"}' --user my_username:my_password http://localhost:5000/api/RestartDevice
