# -*- coding: utf-8 -*-

# for creating ticket key hash
def gen_sha(text):
    h = hashlib.sha1()
    h.update(text)
    return h.hexdigest()