# -*- coding: utf-8 -*-

"""
Receipt parameters handler
"""

from decimal import Decimal
import json

from datetime import datetime
from django_countries.fields import Country, country_to_text
from django.template.loader import render_to_string
import arrow


class ReceiptEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return arrow.get(o).isoformat()
        if isinstance(o, Decimal):
            return str(o)
        if isinstance(o, Country):
            return country_to_text(o)
        return json.JSONEncoder.default(self, o)


class ReceiptParams(object):
    def __init__(self, source_json=None):
        self.params = {
            'order_number': '',
            'receipt_number': '',
            'receipt_date': '',
            'order_date': '',
            'first_name': '',
            'last_name': '',
            'mobile': '',
            'email': '',
            'telephone': '',
            'company': '',
            'street': '',
            'city': '',
            'postal_code': '',
            'country': '',
            'items': [],
            'transaction_url': '',
            'total': Decimal('0.00'),
        }
        if source_json:
            self.params.update(json.loads(source_json))
            for m in ['receipt_date', 'order_date']:
                self.params[m] = arrow.get(self.params[m]).datetime
            for k in range(len(self.params['items'])):
                item = self.params['items'][k]
                for m in ['price', 'total']:
                    item[m] = Decimal(item[m])
            self.params['total'] = Decimal(self.params['total'])

    def receipt_number(self, var: int):
        self.params['receipt_number'] = var

    def receipt_date(self, var: datetime):
        self.params['receipt_date'] = var

    def order_date(self, var: datetime):
        self.params['order_date'] = var

    def order_number(self, var: int):
        self.params['order_number'] = var

    def first_name(self, var: str):
        self.params['first_name'] = var

    def last_name(self, var: str):
        self.params['last_name'] = var

    def email(self, var: str):
        self.params['email'] = var

    def mobile(self, var: str):
        self.params['mobile'] = var

    def telephone(self, var: str):
        self.params['telephone'] = var

    def company(self, var: str):
        self.params['company'] = var

    def street(self, var: str):
        self.params['street'] = var

    def city(self, var: str):
        self.params['city'] = var

    def postal_code(self, var: str):
        self.params['postal_code'] = var

    def country(self, var: str):
        self.params['country'] = var

    def transaction_url(self, var: str):
        self.params['transaction_url'] = var

    def add_item(self, item_id: int, name: str, price: Decimal, amount: int, tax: str):
        """
        Add an item to the bought list, and increment total cost calculator

        :param item_id: Item store ID
        :param name: Item name
        :param price: Item price
        :param amount: Item amount
        :param tax: Tax (for display purposes, not used in calculations)
        """
        item_total = price * amount
        self.params['items'].append({
            'id': item_id,
            'name': name,
            'price': price,
            'amount': amount,
            'total': item_total,
            'tax': tax
        })
        self.params['total'] += item_total

    def get_json(self) -> str:
        """
        Returns a JSON representation of the params data
        :return: JSON string
        """
        return json.dumps(self.params, cls=ReceiptEncoder)

    def get_body(self) -> str:
        """
        Retusns a formatted receipt
        :return: Formatted receipt string
        """
        return render_to_string('store/receipt.email', self.params)
