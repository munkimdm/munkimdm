#!/usr/bin/env python3

import base64
import json
import logging
import os

import coloredlogs
import requests
from dotenv import load_dotenv
from flask import Flask, request
from flask_basicauth import BasicAuth

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

supported_commands = [
    "RestartDevice",
    "InstallProfile",
    "RemoveProfile",
    "ShutDownDevice",
]


@application.route("/api/<command>", methods=["GET", "POST"])
@basic_auth.required
def api(command):
    if command not in supported_commands:
        return f"ERROR: Command '{command}' not valid.\n"

    content = request.json
    if not request.json:
        return f"ERROR: No JSON payload present.\n"

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
                    error_message = f"Unable to extract profile '{content['profile']}' from {profile}."
                    log.exception(error_message)
                    return f"ERROR: {error_message}\n"

            else:
                payload[key] = content[key]

            valid_request = True

    if not valid_request:
        error_message = f"Command '{command}' specified but no valid identifier found."
        log.error(error_message)
        return f"ERROR: {error_message}\n"

    api_url = f"{os.getenv('MICROMDM_URL')}/v1/commands"
    log.debug(f"Posting to {api_url}, payload: \n{json.dumps(payload, indent=4)}")

    try:
        response = requests.post(
            api_url, auth=("micromdm", os.getenv("MICROMDM_KEY")), json=payload,
        )

    except requests.exceptions.RequestException as e:
        log.exception(e)
        return f"ERROR: {e}\n"

    if response.status_code == 200:
        return f"Command '{command}' issued successfully."

    else:
        error_message = f"API returned status code {response.status_code}."
        log.error(error_message)
        return f"ERROR: {error_message}\n"


if __name__ == "__main__":
    application.run(debug=True)
