""" Account Object """

from decimal import Decimal
import datetime

import streamlit as st

from common import (
    f2d,
    get_growth_rate,
    INFLATION_LABEL,
    NEGATIVE_ONE,
)
from Configuration import Configuration
from Change import Change
from common import ZERO

class BaseAsset:
    asset_class = 'BaseAsset'
    support_minimum = False
    prioritized = False

    def __init__(
        self,
        unique_id: int,
        plan,
        name: str = None,
        starting_balance: float = 0.0,
        minimum_balance: float = 0.0,
        enforce_minimum_balance: bool = False,
        priority: int = None,
        interest_profile: str = None):

        self.unique_id = unique_id
        self.configuration = plan.configuration
        if name is None:
            self.name = f'{self.asset_class} #{unique_id}'
        else:
            self.name = name
        self.starting_balance = self.calculate_starting_balance(f2d(starting_balance))
        self.minimum_balance = f2d(minimum_balance)
        self.enforce_minimum_balance = enforce_minimum_balance
        self.balance = self.starting_balance
        if priority is None:
            self.priority = self.unique_id
        else:
            self.priority = priority
        self.unable_to_balance = False
        if interest_profile is None:
            self.interest_profile = plan.interest_profile_names[0]
        else:
            self.interest_profile = interest_profile
        self.plan = plan

    def calculate_starting_balance(self, starting_balance: Decimal) -> Decimal:
        return starting_balance

    @property
    def display_starting_balance(self):
        return float(self.starting_balance)

    def to_dict(self) -> dict:
        data = {
            'name': self.name,
            'starting_balance': self.display_starting_balance,
            'interest_profile': self.interest_profile,
        }
        if self.support_minimum:
            data['enforce_minimum_balance'] = self.enforce_minimum_balance
        if self.enforce_minimum_balance:
            data['minimum_balance'] = float(self.minimum_balance)
        if self.prioritized:
            data['priority'] = self.priority
        return data

    def configure(self, location):
        label = f'{self.asset_class} #{self.unique_id}'
        location.markdown('---')
        self.name = location.text_input(f'{label} Name', value=self.name)
        self.starting_balance = self.calculate_starting_balance(
            f2d(location.number_input(f'{label} locationarting Balance ($)', value=self.display_starting_balance, min_value=0.00, step=0.01))
        )
        if self.support_minimum:
            self.enforce_minimum_balance = location.checkbox(f'{label} Enforce Minimum Balance?', value=self.enforce_minimum_balance)
            if self.enforce_minimum_balance:
                location.info('When active `Enforce Minimum Balance` will pull from other assets each month according to priority to maintain minimum')
                self.minimum_balance = f2d(location.number_input(f'{label} Minimum Balance ($)', value=float(self.minimum_balance), step=0.01))
        if self.prioritized:
            self.priority = int(location.number_input(f'{label} Withdrawal Priority', value=self.priority, min_value=0, step=1))
        interest_profile_names = self.plan.interest_profile_names
        self.interest_profile = location.selectbox(f'{label} Interest Profile', options=interest_profile_names, index=interest_profile_names.index(self.interest_profile))
            
        self.balance = self.starting_balance

    def update(self, statement_date: datetime.date, period_index: int, plan) -> dict:
        interest = plan.get_interest_profile(self.interest_profile).get_profile()[period_index]
        update_amount = round(f2d(interest * float(self.balance)), 2)
        transactions = []
        if update_amount > ZERO:
            self.balance += update_amount
            transactions.append(Change(
                'interest',
                self.name + '_interest',
                update_amount,
                statement_date,
                self.name,
            ))
        if self.enforce_minimum_balance and not self.unable_to_balance:
            if self.balance < self.minimum_balance:
                delta_needed = self.minimum_balance - self.balance
                accounts_with_priority = [(account.name, account.priority) for account in plan.accounts if account.name != self.name]
                accounts_with_priority.sort(key = lambda x: x[1])
                i = 0
                while delta_needed > ZERO:
                    try:
                        account_name = accounts_with_priority[i][0]
                    except IndexError:
                        st.error(f'Unable to maintain minimum balance on account {self.name}')
                        self.unable_to_balance = True
                        break
                    account = plan.get_account(account_name)
                    balance = account.balance
                    if balance <= ZERO:
                        transfer_amount = ZERO
                    elif balance < delta_needed:
                        transfer_amount = balance
                    else: # plenty to transfer
                        transfer_amount = delta_needed
                    if transfer_amount != ZERO:
                        delta_needed -= transfer_amount
                        account.balance -= transfer_amount
                        self.balance += transfer_amount
                        transactions.extend([
                            Change(
                                'minimum_balance',
                                self.name + '_min_balance',
                                transfer_amount,
                                statement_date,
                                self.name,
                            ),
                            Change(
                                'minimum_balanceb',
                                self.name + '_min_balance',
                                NEGATIVE_ONE * transfer_amount,
                                statement_date,
                                account.name
                            )
                        ])
                    i += 1
                    

        return transactions


class Asset(BaseAsset):
    asset_class = 'Asset'

class Account(BaseAsset):
    asset_class = 'Account'
    support_minimum = True
    prioritized = True

class Liability(BaseAsset):
    asset_class = 'Liability'

    def calculate_starting_balance(self, starting_balance: Decimal) -> Decimal:
        return NEGATIVE_ONE * starting_balance

    @property
    def display_starting_balance(self):
        return float(self.starting_balance * NEGATIVE_ONE)