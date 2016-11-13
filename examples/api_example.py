# -*- coding: utf-8 -*-

from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import BackendApplicationClient
import requests
import os
import json

# REMOVE THIS IN PRODUCTION! Allows testing locally.
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

# Test client ID and secret. Insert your own here.
CLIENT_ID = 'SM8GKdbouUAFOQ1TSAePpdmsTQ6j9un3l8VZ3uEu'
CLIENT_SECRET = 'MQGAOkpDl65qjLF1T4rZzTdRPNu32mi7V1uJKJUOEXt7ygoWELtaOz5w3sSQydvnLMGsC0ZByXeFHENheYUnNWfg8c9tVA4Svdj27Wj647tVuTkBJTLGP3v0cW3Hq5LM'


# Connects to an oauth2 token endpoint and fetches a token for using the api
# Note that the token may timeout, in which case you need to renew it
def fetch_token(url, client_id, client_secret):
    client = BackendApplicationClient(client_id=client_id)
    oauth = OAuth2Session(client=client)
    token = oauth.fetch_token(token_url=url,
                              client_id=client_id,
                              client_secret=client_secret)
    return token


def main():
    token = fetch_token('http://localhost:8000/api/oauth2/token/', CLIENT_ID, CLIENT_SECRET)
    print("Scope:        {}".format(token['scope']))
    print("Token type:   {}".format(token['token_type']))
    print("Expires at:   {}".format(token['expires_at']))
    print("Expires in:   {}".format(token['expires_in']))
    print("Access token: {}".format(token['access_token']))

    headers = {
        'Authorization': 'Bearer {}'.format(token['access_token'])
    }
    r = requests.get('http://localhost:8000/api/events/', headers=headers)
    print("Response:     {}".format(r.status_code))

    if r.status_code == 200:
        data = json.loads(r.content.decode())
        print("Data:\n{}".format(data))
    else:
        print("Data:         No data, wrong return code")

main()
