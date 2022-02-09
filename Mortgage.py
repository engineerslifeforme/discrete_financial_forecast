""" Mortgage Class """

from decimal import Decimal
import datetime

import streamlit as st

from common import f2d, mortgage_payment, ZERO, NEGATIVE_ONE
from Change import Change

class Mortgage:
    description = """`Mortgages` are a specialized type of transaction/`Expense`.  They offer
a more intuitive interface to define this special type of expense.

- `Original Length`: The original length in years of the mortgage (NOT the remaining time)
- `Rate`: The APR of the `Mortgage`
- `Original Loan Amount`: The original amounnt (NOT the remaining balance, which is the balance of the associated `Liability`)
- `Liability`: The `Liability` into which the principal portion of the `Mortgage` payment should be added.
- `Account Payment Source`: The `Account` from which the full `Mortgage` payment (principal and interest) should be taken.
- `Extra Principal`: Additional principal that will both increase the total payment and the principal payment toward the `Liability`.  0 is fine.

As implicitly stated above, the total mortgage payment will be calculated based on the original `Mortgage` details.
Each month during the forecast, the interest portion of the payment will be calculated based on the remaining
balance of the `Liability`.  The interest portion is effectively an `Expense` resulting in a negative effect
on Net Worth.  The principal portion of the payment will reduce the associated `Liability` resulting in
net 0 change in Net Worth (because the money was removed from the `Source Account`).  The `Mortgage`
payment will be executed in this fashion until the remaining balance becomes less than the payment.
At this point the `Liability` will be paid off (i.e. balance of 0), and no further payments will
be made."""

    def __init__(
        self,
        unique_id: int,
        account_list: list,
        liability_list: list,
        name: str = None,
        starting_balance: float = 0.0,
        length: int = 30,
        rate: float = 5.0,
        liability: str = None,
        source_account: str = None,
        extra_principal: float = 0.0):

        self.unique_id = unique_id
        self.liability_list = liability_list
        self.account_list = account_list
        if name is None:
            self.name = f'Mortgage #{unique_id}'
        else:
            self.name = name
        self.starting_balance = f2d(starting_balance)
        self.length = length
        self.rate = self.calculate_rate(rate)
        self.extra_principal = f2d(extra_principal)
        if liability is None:
            try:
                self.liability = liability_list[0]
            except IndexError:
                self.liability = None
        else:
            self.liability = liability
        if source_account is None:
            self.source_account = account_list[0]
        else:
            self.source_account = source_account

    @property
    def display_rate(self) -> float:
        return self.rate*12.0*100.0

    @property
    def payment(self) -> Decimal:
        return mortgage_payment(self.starting_balance, self.rate, self.length*12) + self.extra_principal

    def calculate_rate(self, rate: float) -> float:
        return rate/100.0/12.0

    def to_dict(self):
        return {
            'name': self.name,
            'starting_balance': float(self.starting_balance),
            'length': self.length,
            'rate': self.display_rate,
            'extra_principal': float(self.extra_principal),
            'liability': self.liability,
            'source_account': self.source_account,
        }

    def configure(self, location):
        if len(self.liability_list) < 1:
            location.error('At least one liability needs to be defined to be associated with the mortgage')
        else:
            label = f'Mortgage #{self.unique_id}'
            location.markdown('---')
            self.name = location.text_input(f'{label} Name', value=self.name)
            left, middle, right = location.columns(3)
            self.starting_balance = f2d(right.number_input(f'{label} Original Loan Amount ($)', value=float(self.starting_balance), min_value=0.0, step=0.01))
            self.length = int(left.number_input(f'{label} Original Length (Years)', value=self.length, min_value=1, step=1))
            self.rate = self.calculate_rate(middle.number_input(f'{label} Rate (%/year)', value=self.display_rate, min_value=0.0, step=0.01))
            left, right = location.columns(2)
            self.liability = left.selectbox(f'{label} Liability', options=self.liability_list, index=self.liability_list.index(self.liability))
            self.source_account = right.selectbox(f'{label} Account Payment Source', options=self.account_list, index=self.account_list.index(self.source_account))
            self.extra_principal = f2d(location.number_input(f'{label} Extra Principal ($/month)', value=float(self.extra_principal), min_value=0.0, step=0.01))
            location.markdown(f'Payment $ {self.payment}')

    def update(self, date: datetime.date, period_index: int, plan) -> list:
        changes = []
        if self.starting_balance > ZERO: # Not worth doing anything if not configured            
            liability = plan.get_liability(self.liability)
            abs_remaining_balance = abs(liability.balance)
            if abs_remaining_balance > Decimal('0.01'):                
                source = plan.get_account(self.source_account)
                if self.payment < abs_remaining_balance:
                    interest_payment = round(f2d(float(abs_remaining_balance) * self.rate), 2)
                    principal_payment = self.payment - interest_payment
                    total_payment = self.payment
                    close = False
                else:
                    principal_payment = abs_remaining_balance
                    interest_payment = ZERO
                    total_payment = abs_remaining_balance
                    close = True
                
                source.balance -= total_payment
                
                if interest_payment != ZERO:
                    changes.append(Change(
                        'mortgage_interest',
                        self.name,
                        NEGATIVE_ONE * interest_payment,
                        date,
                        source.name
                    ))
                changes.extend([
                    Change(
                        'mortgage_equity',
                        self.name,
                        NEGATIVE_ONE * principal_payment,
                        date,
                        source.name,
                    ),
                    Change(
                        'mortgage_equity',
                        self.name,
                        principal_payment,
                        date,
                        liability.name,
                    )
                ])
                liability.balance += principal_payment
                if close:
                    liability.balance = ZERO
        return changes
                
                


    