import hashlib

import requests


class PaytrailException(Exception):
    pass


def validate_failure(order_no: str, timestamp: str, authcode: str, secret: str) -> bool:
    m = hashlib.md5()
    m.update("{}|{}|{}".format(order_no, timestamp, secret).encode("UTF-8"))
    return authcode == m.hexdigest().upper()


def validate_success(
    order_no: str, timestamp: str, paid: str, method: str, authcode: str, secret: str
) -> bool:
    m = hashlib.md5()
    m.update("{}|{}|{}|{}|{}".format(order_no, timestamp, paid, method, secret).encode("UTF-8"))
    return authcode == m.hexdigest().upper()


def request(api_url: str, rid: str, secret: str, data: dict) -> dict:
    req = requests.post(
        api_url,
        auth=(rid, secret),
        json=data,
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
            "X-Verkkomaksut-Api-Version": "1",
        },
    )

    # Send request, receive response
    message: dict = req.json()

    # Paytrail responded with error
    if req.status_code == 401:
        raise PaytrailException(message["errorMessage"], message["errorCode"])

    # No response from paytrail (other error)
    if req.status_code != 201:
        raise PaytrailException("HTTP request failure.", req.status_code)

    # Return parsed JSON
    return message
