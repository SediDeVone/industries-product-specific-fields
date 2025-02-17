import requests


def authorize(authorize_record):
    params = {
        "grant_type": "password",
        "client_id": authorize_record.consumer_key,
        "client_secret": authorize_record.consumer_secret,
        "username": authorize_record.username,
        "password": authorize_record.password + authorize_record.security_token
    }

    r = requests.post("https://" + authorize_record.host + "/services/oauth2/token", params=params)
    access_token = r.json().get("access_token")
    instance_url = r.json().get("instance_url")

    return access_token, instance_url
