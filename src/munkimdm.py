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
        return f"Command {command} not valid."

    content = request.json

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
                    log.exception(f"Unable to extract payload from {profile}.")
                    return

            else:
                payload[key] = content[key]

    api_url = f"{os.getenv('MICROMDM_URL')}/v1/commands"
    log.debug(f"Posting to {api_url}, payload: \n{json.dumps(payload, intent=4)}")

    response = requests.post(
        api_url, auth=("micromdm", os.getenv("MICROMDM_KEY")), json=payload,
    )
    if response.status_code != 200:
        log.error(f"API returned status code {response.status_code}.")
    else:
        return f"Command '{command}' issued successfully."


if __name__ == "__main__":
    application.run(debug=True)
