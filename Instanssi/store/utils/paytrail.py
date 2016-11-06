# -*- coding: utf-8 -*-

import base64
import hashlib
from http.client import HTTPSConnection
import json


class PaytrailException(Exception):
    pass


def validate_failure(order_no, timestamp, authcode, secret):
    m = hashlib.md5()
    m.update('%s|%s|%s' % (order_no, timestamp, secret))
    return authcode == m.hexdigest().upper()


def validate_success(order_no, timestamp, paid, method, authcode, secret):
    m = hashlib.md5()
    m.update('%s|%s|%s|%s|%s' % (order_no, timestamp, paid, method, secret))
    return authcode == m.hexdigest().upper()


def request(rid, secret, data):
    # Some basic data
    host = 'payment.paytrail.com'
    auth = 'Basic ' + base64.b64encode('{}:{}'.format(rid, secret).encode('UTF-8')).strip()
    body = json.dumps(data)
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'X-Verkkomaksut-Api-Version': '1',
        'Authorization': auth
    }

    # Send request, receive response
    c = HTTPSConnection(host, timeout=15)
    c.request('GET', '/api-payment/create', body=body, headers=headers)
    res = c.getresponse()
    message = json.loads(res.read())

    # Paytrail responded with error
    if res.status == 401:
        raise PaytrailException(message['errorMessage'], message['errorCode'])

    # No response from paytrail (other error)
    if res.status != 201:
        raise PaytrailException('HTTP request failure.', res.status)

    # Return parsed JSON
    return message
