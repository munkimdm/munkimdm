#!/usr/bin/env python3

import base64
import json
import logging
import os

import coloredlogs
import requests
from dotenv import load_dotenv
from flask import Flask, request, jsonify, make_response, abort
from flask_basicauth import BasicAuth
from healthcheck import HealthCheck

log = logging.getLogger()
logging.getLogger("requests").setLevel(logging.WARNING)
coloredlogs.install(
    fmt="[%(asctime)s] [%(levelname)-8s] %(message)s", level="INFO", logger=log
)

load_dotenv()

application = Flask(__name__)

application.config["BASIC_AUTH_USERNAME"] = os.getenv("BASIC_AUTH_USERNAME")
application.config["BASIC_AUTH_PASSWORD"] = os.getenv("BASIC_AUTH_PASSWORD")
basic_auth = BasicAuth(application)

healthz = HealthCheck()
application.add_url_rule("/healthz", "healthz", view_func=lambda: healthz.run())

supported_commands = [
    "InstallProfile",
    "RemoveProfile",
]


class InvalidUsage(Exception):
    status_code = 400

    def __init__(self, message, status_code=400, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload
        log.debug(message)

    def to_dict(self):
        rv = dict(self.payload or ())
        rv["error"] = self.message
        return rv


@application.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


@application.route("/api/<command>", methods=["GET", "POST"])
@basic_auth.required
def api(command):
    if command not in supported_commands:
        raise InvalidUsage("Command '{command}' not valid.")

    content = request.json
    if not request.json:
        raise InvalidUsage("No JSON payload present.")

    payload = {"request_type": command}
    payload_keys = [
        "udid",
        "pin",  # For DeviceLock
        "product_key",  # For ScheduleOSUpdate
        "install_action",  # For ScheduleOSUpdateScan
        "force",  # For ScheduleOSUpdateScan
        "identifier",  # For RemoveProfile
        "profile",  # For InstallProfile
    ]

    # extract the data from the profile
    valid_request = False
    for key in payload_keys:

        if key in content:

            if key == "profile":
                profile = os.path.join(
                    os.getenv("MUNKI_REPO_PATH"), "pkgs", "profiles", content["profile"]
                )
                try:
                    with open(profile, "rb") as f:
                        bytes = f.read()
                        payload["Payload"] = base64.b64encode(bytes).decode("ascii")
                except:
                    raise InvalidUsage(
                        f"Unable to extract profile '{content['profile']}' from {profile}."
                    )

            else:
                payload[key] = content[key]

            valid_request = True

    if not valid_request:
        raise InvalidUsage(
            f"Command '{command}' specified but no valid identifier found."
        )

    api_url = f"{os.getenv('MICROMDM_URL')}/v1/commands"
    log.debug(f"Posting to {api_url}, payload: \n{json.dumps(payload, indent=4)}")

    try:
        response = requests.post(
            api_url, auth=("micromdm", os.getenv("MICROMDM_KEY")), json=payload,
        )

    except requests.exceptions.RequestException as e:
        raise InvalidUsage(e)

    if response.status_code == 200:
        return f"Command '{command}' issued successfully."

    else:
        raise InvalidUsage(f"API returned status code {response.status_code}.")


if __name__ == "__main__":
    application.run(debug=True)
