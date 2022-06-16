import requests
from flask_basicauth import BasicAuth
from nested_lookup import get_occurrence_of_value
from flask import Flask, request
from env import settings

app = Flask(__name__)

app.config['BASIC_AUTH_USERNAME'] = settings.get('basic_auth_user')
app.config['BASIC_AUTH_PASSWORD'] = settings.get('basic_auth_password')
basic_auth = BasicAuth(app)

supported_commands = ['InstallApplication', 'DisassociateApplication', 'InstallEnterpriseApplication', 'InstallProfile', 'RemoveProfile', 'EnableRemoteDesktop', 'DisableRemoteDesktop', 'RestartDevice', 'ShutDownDevice', 'EraseDevice' , 'ScheduleOSUpdate']

@app.route('/api/<command>', methods=['GET', 'POST'])
@basic_auth.required
def api(command):
    if command not in supported_commands:
        return 'Command %s not valid.\n' % command
    content = request.json
    def check(arg):
        if arg in content:
            payload[arg] = content[arg]
    def check_int(arg):
        if arg in content:
            payload[arg] = int(content[arg])
    payload = {
        'request_type': command
    }
    check('udid')
    check('pin')                        # For DeviceLock
    check('product_key')                # For ScheduleOSUpdate
    check('install_action')             # For ScheduleOSUpdateScan
    check('force')                      # For ScheduleOSUpdateScan
    check('payload')	                 # For InstallProfile
    check('identifier')                 # For RemoveProfile
    check('manifest_url')	             # For InstallEnterpriseApplication
    check('serial')                     # For InstallVPPApplication
    check_int('itunes_store_id')        # For InstallVPPApplication
    if 'InstallApplication' in command:
        options = {}
        options['purchase_method'] = int(1)
        payload['options'] = options
        # Get List of Licenses associated with Serial
        params = dict(
            sToken=settings.get('sToken'),
            serialNumber=content['serial']
        )
        resp = requests.get(url=settings.get('licensesurl'), json=params)
        data = resp.json()
        print(data)
        if get_occurrence_of_value(data, value=content['itunes_store_id']) == 0:
            # Assign this to this serial number
            print("Sending InstallApplication for VPP app")
            params = dict(
                sToken=settings.get('sToken'),
                associateSerialNumbers=[content['serial']],
                pricingParam="STDQ",
                adamIdStr=content['itunes_store_id']
                )
            print(requests.post(url=settings.get('manageurl'), json=params))
            print(params)
    if 'DisassociateApplication' in command:
        options = {}
        options['purchase_method'] = int(1)
        payload['options'] = options
        # Get List of Licenses associated with Serial
        params = dict(
            sToken=settings.get('sToken'),
            serialNumber=content['serial']
        )
        resp = requests.get(url=settings.get('licensesurl'), json=params)
        data = resp.json()
        print(data)
        if get_occurrence_of_value(data, value=content['itunes_store_id']) == 0:
            # Assign this to this serial number
            print("Sending InstallApplication for VPP app")
            params = dict(
                sToken=settings.get('sToken'),
                disassociateSerialNumbers=[content['serial']],
                pricingParam="STDQ",
                adamIdStr=content['itunes_store_id']
                )
            print(requests.post(url=settings.get('manageurl'), json=params))
            print(params)
    requests.post(
        '{}/v1/commands'.format(settings.get('micromdm_url')),
        auth=('micromdm', settings.get('micromdm_key')),
        json=payload
    )
    return 'Issuing %s: Success! \n' % payload

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
