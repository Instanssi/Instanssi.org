from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import BackendApplicationClient
import requests
import os
import json

# REMOVE THIS IN PRODUCTION! Allows testing locally.
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

# API URL (https for real instanssi site)
API_ADDR = "http://localhost:8000/api/v1"

# Test client ID and secret. Insert your own here.
CLIENT_ID = 'bj6oxteE47zxS1I1QAwPb77FAqd9m2nWk8tiKfIx'
CLIENT_SECRET = 'buV0Amz3HmjHri74UkH5OhVgT07iIpZC5onTey9S2w3obUQ2kLAoys0Tz3TAGppfgVBY4ozwZGRPvA7ua9Lf5jgLtQUy5BMgIkcPsvyHVoiX9gSiEOGsAzZ9zKO4ssvk'


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
    token = fetch_token('{}/oauth2/token/'.format(API_ADDR), CLIENT_ID, CLIENT_SECRET)
    print("Scope:        {}".format(token['scope']))
    print("Token type:   {}".format(token['token_type']))
    print("Expires at:   {}".format(token['expires_at']))
    print("Expires in:   {}".format(token['expires_in']))
    print("Access token: {}".format(token['access_token']))

    headers = {
        'Authorization': 'Bearer {}'.format(token['access_token'])
    }
    r = requests.get('{}/events/'.format(API_ADDR), headers=headers)
    print("Response:     {}".format(r.status_code))

    if r.status_code == 200:
        data = json.loads(r.content.decode())
        print("Data:\n{}".format(data))
    else:
        print("Data:         No data, wrong return code ({})".format(r.status_code))


main()
