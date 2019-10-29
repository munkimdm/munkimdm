#!/usr/bin/env python3

from flask import Flask, request
import base64
import requests
from env import settings
from flask_basicauth import BasicAuth

application = Flask(__name__)

application.config['BASIC_AUTH_USERNAME'] = settings.get('basic_auth_user')
application.config['BASIC_AUTH_PASSWORD'] = settings.get('basic_auth_password')
basic_auth = BasicAuth(application)

supported_commands = ['RestartDevice','InstallProfile','RemoveProfile','ShutDownDevice'...]

@application.route('/api/<command>', methods=['GET', 'POST'])
@basic_auth.required
def api(command):
    if command not in supported_commands:
        return 'Command %s not valid.\n' % command
    content = request.json
    def check(arg):
        if arg in content:
            payload[arg] = content[arg]
    payload = {
        'request_type': command
    }
    check('udid')
    check('pin')                # For DeviceLock
    check('product_key')        # For ScheduleOSUpdate
    check('install_action')     # For ScheduleOSUpdateScan
    check('force')              # For ScheduleOSUpdateScan
    check('identifier')         # For RemoveProfile
    if 'profile' in content:    # For InstallProfile
        profile = ('/path_to/munki_repo/pkgs/profiles/%s' % content['profile'])
        with open(profile, "rb") as f:
            bytes = f.read()
            payload['Payload'] = base64.b64encode(bytes).decode('ascii')
    requests.post(
        '{}/v1/commands'.format(settings.get('micromdm_url')),
        auth=('micromdm', settings.get('micromdm_key')),
        json=payload
    )
    return 'Issuing %s: Success! \n' % command

if __name__ == '__main__':
    application.run(debug=True)
