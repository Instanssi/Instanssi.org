# -*- coding: utf-8 -*-

"""
Mailer class sends emails with given parameters.
"""

from django.template.loader import render_to_string
from django.core.mail import send_mail

class Mailer(object):
    def __init__(self, template, email_from, email_to, subject):
        self.subject = subject
        self.email_from = email_from
        self.email_to = email_to
        self.tpl = template
        self.params = {}

    def send(self):
        content = render_to_string(self.tpl, self.params)
        send_mail(self.subject, content, self.email_from, (self.email_to,))
