# -*- coding: utf-8 -*-

import httplib
import json
import string
import base64
import hashlib

class BitpayException(Exception):
    pass

def validate_failure(orderno, timestamp, authcode, secret):
    m = hashlib.md5()
    m.update('%s|%s|%s' % (orderno, timestamp, secret))
    return (authcode == m.hexdigest().upper())

def validate_success(orderno, timestamp, paid, method, authcode, secret):
    m = hashlib.md5()
    m.update('%s|%s|%s|%s|%s' % (orderno, timestamp, paid, method, secret))
    return (authcode == m.hexdigest().upper())

def request(key, data):
    # Some basic data
    host = 'bitpay.com'
    auth = 'Basic ' + string.strip(base64.encodestring(key + ':')) # Blank pw
    body = json.dumps(data)
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': auth
    }

    # Send request, receive response
    c = httplib.HTTPSConnection(host, timeout=15)
    c.request('POST', '/api/invoice', body=body, headers=headers)
    res = c.getresponse()
    message = json.loads(res.read())

    # Paytrail responded with error
    if res.status < 200 or res.status >= 400:
        raise BitpayException(message['errorMessage'], message['errorCode'])

    # No response from bitpay (other error)
    if message.status != 'new'
        raise BitpayException(u'Invcoice generation failure.', message.status)

    # Return parsed JSON
    return message
