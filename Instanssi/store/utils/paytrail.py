# -*- coding: utf-8 -*-

import base64
import hashlib
import httplib
import json
import string


class PaytrailException(Exception):
    pass


def validate_failure(orderno, timestamp, authcode, secret):
    m = hashlib.md5()
    m.update('%s|%s|%s' % (orderno, timestamp, secret))
    return authcode == m.hexdigest().upper()


def validate_success(orderno, timestamp, paid, method, authcode, secret):
    m = hashlib.md5()
    m.update('%s|%s|%s|%s|%s' % (orderno, timestamp, paid, method, secret))
    return authcode == m.hexdigest().upper()


def request(id, secret, data):
    # Some basic data
    host = 'payment.paytrail.com'
    auth = 'Basic ' + string.strip(base64.encodestring(id + ':' + secret))
    body = json.dumps(data)
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'X-Verkkomaksut-Api-Version': '1',
        'Authorization': auth
    }

    # Send request, receive response
    c = httplib.HTTPSConnection(host, timeout=15)
    c.request('GET', '/api-payment/create', body=body, headers=headers)
    res = c.getresponse()
    message = json.loads(res.read())

    # Paytrail responded with error
    if res.status == 401:
        raise PaytrailException(message['errorMessage'], message['errorCode'])

    # No response from paytrail (other error)
    if res.status != 201:
        raise PaytrailException(u'HTTP request failure.', res.status)

    # Return parsed JSON
    return message
