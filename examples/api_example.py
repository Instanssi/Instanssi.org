import requests
import json
import logging

# API URL (https for real instanssi site)
API_ADDR = "http://localhost:8000/api/v1"

# Test token. Insert your own here.
TOKEN_KEY = "5a71a3d25146f3a308690b4d793da25d145f70976a7e8113967ed446e451f810"


def main():
    logging.basicConfig(level=logging.DEBUG)
    headers = {
        "Authorization": f"Token {TOKEN_KEY}",
        "Content-Type": "application/json",
    }
    r = requests.get(f"{API_ADDR}/admin/events/", headers=headers)
    print("Response:     {}".format(r.status_code))

    if r.status_code == 200:
        data = json.loads(r.content.decode())
        print("Data:\n{}".format(data))
    else:
        print("Data:         No data, wrong return code ({})".format(r.status_code))


if __name__ == "__main__":
    main()
