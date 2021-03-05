# -*- coding: utf-8 -*-

import requests


class BitpayException(Exception):
    pass


def request(key, data):
    req = requests.post(
        'https://bitpay.com/api/invoice',
        auth=(key, ''),
        json=data,
        headers={
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        })

    # Bitpay responded with error
    if req.status_code < 200 or req.status_code >= 400:
        raise BitpayException("Http request error", req.status_code)

    # Send request, receive response
    message = req.json()

    # No response from bitpay (other error)
    if message['status'] != 'new':
        raise BitpayException('Invoice generation failure.', message.status)

    # Return parsed JSON
    return message
