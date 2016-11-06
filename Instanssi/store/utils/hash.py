# -*- coding: utf-8 -*-

import hashlib


# for creating ticket key hash
def gen_sha(text):
    h = hashlib.sha1()
    if type(text) is str:
        text = text.encode()
    h.update(text)
    return h.hexdigest()
