# -*- coding: utf-8 -*-

import httplib
import json
import string
import base64


class BitpayException(Exception):
    pass


def request(key, data):
    # Some basic data
    host = 'bitpay.com'
    auth = 'Basic ' + string.strip(base64.encodestring(key + ':'))  # Blank pw
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

    # Bitpay responded with error
    if res.status < 200 or res.status >= 400:
        raise BitpayException("Http request error", res.status)

    # No response from bitpay (other error)
    if message['status'] != 'new':
        raise BitpayException(u'Invoice generation failure.', message.status)

    # Return parsed JSON
    return message
