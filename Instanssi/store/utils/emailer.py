# -*- coding: utf-8 -*-

"""
Mailer class sends emails with given parameters.
"""

from Instanssi.common.mail import Mailer
from decimal import Decimal


class ReceiptMailer(Mailer):
    def __init__(self, email_from, email_to, subject):
        super(ReceiptMailer, self).__init__('store/receipt.email', email_from, email_to, subject)
        self.params = {
            'ordernumber': '',
            'firstname': '',
            'lastname': '',
            'mobile': '',
            'email': '',
            'telephone': '',
            'company': '',
            'street': '',
            'city': '',
            'postalcode': '',
            'country': '',
            'items': [],
            'transactionurl': '',
            'total': Decimal('0.00'),
        }

    def ordernumber(self, var):
        self.params['ordernumber'] = var

    def firstname(self, var):
        self.params['firstname'] = var

    def lastname(self, var):
        self.params['lastname'] = var

    def email(self, var):
        self.params['email'] = var

    def mobile(self, var):
        self.params['mobile'] = var

    def telephone(self, var):
        self.params['telephone'] = var

    def company(self, var):
        self.params['company'] = var

    def street(self, var):
        self.params['street'] = var

    def city(self, var):
        self.params['city'] = var

    def postalcode(self, var):
        self.params['postalcode'] = var

    def country(self, var):
        self.params['country'] = var

    def transactionurl(self, var):
        self.params['transactionurl'] = var

    def add_item(self, id, name, price, amount):
        itemtotal = price * amount
        self.params['items'].append({
            'id': id,
            'name': name,
            'price': price,
            'amount': amount,
            'total': itemtotal,
        })
        self.params['total'] += itemtotal
