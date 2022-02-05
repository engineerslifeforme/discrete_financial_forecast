""" Change Class """

from decimal import Decimal
import datetime

class Change:

    def __init__(
        self,
        change_type: str,
        name: str,
        amount: Decimal,
        date: datetime.date,
        account: str):

        self.type = change_type
        self.name = name
        self.amount = amount
        self.date = date
        self.account = account

    def to_dict(self) -> dict:
        return {
            'type': self.type,
            'name': self.name,
            'amount': self.amount,
            'date': self.date,
            'account': self.account,
        }
