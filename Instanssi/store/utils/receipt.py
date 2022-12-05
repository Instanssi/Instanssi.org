"""
Receipt parameters handler
"""

import json
from datetime import datetime
from decimal import Decimal
from typing import Any, Optional, Union

import arrow
from django.template.loader import render_to_string
from django_countries.fields import Country


class ReceiptEncoder(json.JSONEncoder):
    def default(self, o: Any) -> Any:
        if isinstance(o, datetime):
            return arrow.get(o).isoformat()
        if isinstance(o, Decimal):
            return str(o)
        if isinstance(o, Country):
            return o.code
        return json.JSONEncoder.default(self, o)


class ReceiptParams:
    def __init__(self, source_json: Optional[Union[bytes, str]] = None) -> None:
        self.params = dict(
            order_number=0,
            receipt_number=0,
            receipt_date=None,
            order_date=None,
            first_name="",
            last_name="",
            mobile="",
            email="",
            telephone="",
            company="",
            street="",
            city="",
            postal_code="",
            country="",
            items=[],
            transaction_url="",
            total=Decimal("0.00"),
        )
        if source_json:
            self.params.update(json.loads(source_json))
            for m in ["receipt_date", "order_date"]:
                self.params[m] = arrow.get(self.params[m]).datetime
            for k in range(len(self.params["items"])):
                item = self.params["items"][k]
                for m in ["price", "total"]:
                    item[m] = Decimal(item[m])
            self.params["total"] = Decimal(self.params["total"])

    def receipt_number(self, var: int) -> None:
        self.params["receipt_number"] = var

    def receipt_date(self, var: Optional[datetime]) -> None:
        self.params["receipt_date"] = var

    def order_date(self, var: Optional[datetime]) -> None:
        self.params["order_date"] = var

    def order_number(self, var: int) -> None:
        self.params["order_number"] = var

    def first_name(self, var: str) -> None:
        self.params["first_name"] = var

    def last_name(self, var: str) -> None:
        self.params["last_name"] = var

    def email(self, var: str) -> None:
        self.params["email"] = var

    def mobile(self, var: str) -> None:
        self.params["mobile"] = var

    def telephone(self, var: str) -> None:
        self.params["telephone"] = var

    def company(self, var: str) -> None:
        self.params["company"] = var

    def street(self, var: str) -> None:
        self.params["street"] = var

    def city(self, var: str) -> None:
        self.params["city"] = var

    def postal_code(self, var: str) -> None:
        self.params["postal_code"] = var

    def country(self, var: str) -> None:
        self.params["country"] = var

    def transaction_url(self, var: str) -> None:
        self.params["transaction_url"] = var

    def add_item(self, item_id: int, name: str, price: Decimal, amount: int, tax: str) -> None:
        """
        Add an item to the bought list, and increment total cost calculator

        :param item_id: Item store ID
        :param name: Item name
        :param price: Item price
        :param amount: Item amount
        :param tax: Tax (for display purposes, not used in calculations)
        """
        item_total = price * amount
        self.params["items"].append(
            dict(id=item_id, name=name, price=price, amount=amount, total=item_total, tax=tax)
        )
        self.params["total"] += item_total

    def get_json(self) -> str:
        """Returns a JSON representation of the params data"""
        return json.dumps(self.params, cls=ReceiptEncoder)

    def get_body(self) -> str:
        """Returns a formatted receipt"""
        return render_to_string("store/receipt.email", self.params)
