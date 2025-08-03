from simple_salesforce import Salesforce
import subprocess
import json
import os


def connect_to_sf_environment(username: str, domain: str):
    env_name = username.lower()
    sfdx_cmd = subprocess.Popen(f'sf force:org:display --target-org {env_name} --json', shell=True,
                                stdout=subprocess.PIPE)
    sfdx_info = json.loads(sfdx_cmd.communicate()[0])

    if 'result' in sfdx_info:
        access_token = sfdx_info['result']['accessToken']
        instance_url = sfdx_info['result']['instanceUrl']
    else:
        # Sometimes the authentication fails, try to reauth again and get tokens
        client_id = os.environ.get(username.capitalize() + '_CLIENT_ID')
        username_email = os.environ.get(username.capitalize() + '_USERNAME')
        subprocess.Popen(f'sf org login jwt --client-id {client_id} --jwt-key-file server.key --username {username_email} --alias {env_name}', shell=True,
                                    stdout=subprocess.PIPE)

        sfdx_cmd = subprocess.Popen(f'sf force:org:display --target-org {env_name} --json', shell=True,
                                    stdout=subprocess.PIPE)
        sfdx_info = json.loads(sfdx_cmd.communicate()[0])
        access_token = sfdx_info['result']['accessToken']
        instance_url = sfdx_info['result']['instanceUrl']

    return access_token, instance_url