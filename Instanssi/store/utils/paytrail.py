# -*- coding: utf-8 -*-

import hashlib
import requests


class PaytrailException(Exception):
    pass


def validate_failure(order_no, timestamp, authcode, secret):
    m = hashlib.md5()
    m.update('{}|{}|{}'.format(order_no, timestamp, secret).encode('UTF-8'))
    return authcode == m.hexdigest().upper()


def validate_success(order_no, timestamp, paid, method, authcode, secret):
    m = hashlib.md5()
    m.update('{}|{}|{}|{}|{}'.format(order_no, timestamp, paid, method, secret).encode('UTF-8'))
    return authcode == m.hexdigest().upper()


def request(rid, secret, data):
    req = requests.post(
        'https://payment.paytrail.com/api-payment/create',
        auth=(rid, secret),
        json=data,
        headers={
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'X-Verkkomaksut-Api-Version': '1',
        })

    # Send request, receive response
    message = req.json()

    # Paytrail responded with error
    if req.status_code == 401:
        raise PaytrailException(message['errorMessage'], message['errorCode'])

    # No response from paytrail (other error)
    if req.status_code != 201:
        raise PaytrailException('HTTP request failure.', req.status_code)

    # Return parsed JSON
    return message
