""" Transaction Object """

import streamlit as st
from decimal import Decimal
import datetime

from common import (
    INFLATION_LABEL,
    f2d,
    NEGATIVE_ONE,
    date_id,
    dstr,
    get_date,
    DATE_TYPES,
)
from Configuration import Configuration
from Change import Change

ZERO = Decimal('0.00')
DURATION_OPTIONS = [
    'Forever', 
    'Date Range', 
    'End Date Only', 
    'Start Date Only',
    'One Time',
]
FREQUENCIES = [
    'Daily',
    'Weekly',
    'Biweekly',
    'Monthly',
    'Every X Months',
    'Yearly',
]

class Transaction:
    transaction_type = 'Transaction'

    def __init__(
        self,
        unique_id: int,
        plan,
        name: str = None,
        amount: float = 0.0,
        frequency: str = FREQUENCIES[3],
        source_account: str = None,
        destination_account: str = None,
        duration: str = DURATION_OPTIONS[0],
        start: datetime.date = None,
        end: datetime.date = None,
        month_gap: int = None,
        interest_profile: str = None,
        milestone_start: str = None,
        milestone_end: str = None):
        
        self.unique_id = unique_id
        self.configuration = plan.configuration
        self.asset_list = plan.account_names
        if name is None:
            self.name = f'{self.transaction_type} #{unique_id}'
        else:
            self.name = name
        self.amount = self.calculate_amount(f2d(amount))
        self.frequency = frequency
        asset_list = plan.account_names
        self.source_account = self.set_source_account(source_account, asset_list)
        self.destination_account = self.set_destination_account(destination_account, asset_list)
        self.duration = duration
        self.start = start
        self.end = end
        if self.duration == DURATION_OPTIONS[4]: # one time
            self.end = self.start
        self.month_gap = month_gap
        if self.frequency == FREQUENCIES[5]: #yearly
            self.month_gap = 12
        if interest_profile is None:
            self.interest_profile = plan.interest_profile_names[0]
        else:
            self.interest_profile = interest_profile
        self.month_count = 0
        self.plan = plan
        self.milestone_start = milestone_start
        if self.milestone_start is not None:
            self.start = plan.get_milestone(self.milestone_start).date
        self.milestone_end = milestone_end
        if self.milestone_end is not None:
            self.end = plan.get_milestone(self.milestone_end).date
    
    def to_dict(self):
        data = {
            'name': self.name,
            'amount': self.display_amount,
            'frequency': self.frequency,
            'duration': self.duration,
            'interest_profile': self.interest_profile,
        }
        other_values = {
            'source_account': self.source_account,
            'destination_account': self.destination_account,
            'start': self.start,
            'end': self.end,
            'month_gap': self.month_gap,
            'milestone_end': self.milestone_end,
            'milestone_start': self.milestone_start,
        }
        for key in other_values:
            value = other_values[key]
            if value is not None:
                data[key] = value
        if self.frequency == FREQUENCIES[5]: # yearly
            del(data['month_gap']) # Only used for internal purposes
        if self.duration == DURATION_OPTIONS[4]: # one time
            del(data['end']) # only used for internal purposes
        if self.milestone_start is not None:
            del(data['start'])
        if self.milestone_end is not None:
            del(data['end'])
        return data

    def configure(self, location):
        label = f'{self.transaction_type} #{self.unique_id}'
        location.markdown('---')
        left, right = location.columns(2)
        self.name = left.text_input(f'{label} Name', value=self.name)
        interest_profile_names = self.plan.interest_profile_names
        self.interest_profile = right.selectbox(f'{label} Interest Profile', options=interest_profile_names, index=interest_profile_names.index(self.interest_profile))
        left, middle, right = location.columns(3)
        self.frequency = left.selectbox(f'{label} Frequency', options=FREQUENCIES, index=FREQUENCIES.index(self.frequency))
        if self.frequency == FREQUENCIES[4]: # Multi-month
            if self.month_gap is None:
                default = 2
            else:
                default = self.month_gap
            self.month_gap = int(middle.number_input(f'{label} Months Between', value=default, step=1, min_value=1))
        elif self.frequency == FREQUENCIES[5]: # Yearly
            self.month_gap = 12
        else:
            self.month_gap = None
        self.amount = self.calculate_amount(f2d(
            right.number_input(f'{label} Amount ($/Frequency)', value=self.display_amount, min_value=0.0, step=0.01)
        ))
        if self.month_gap is None:
            monthly_cost = self.monthly_amount
        else:
            monthly_cost = f2d(float(self.monthly_amount) / float(self.month_gap))
        location.markdown(f'Monthly Cost: {dstr(monthly_cost)}')        
        self.source_account, self.destination_account = self.configure_source_destination(location, label)
        self.duration = location.selectbox(f'{label} Duration', options=DURATION_OPTIONS, index=DURATION_OPTIONS.index(self.duration))
        if self.duration == DURATION_OPTIONS[2]: # end only
            self.end, self.milestone_end = get_date(location, f'{label} End Date', self.plan, default_date=self.end, default_milestone=self.milestone_end)
        elif self.duration == DURATION_OPTIONS[3]: # start only
            self.start, self.milestone_start = get_date(location, f'{label} Start Date', self.plan, default_date=self.start, default_milestone=self.milestone_start)
        elif self.duration == DURATION_OPTIONS[1]: # range            
            self.start, self.milestone_start = get_date(location, f'{label} Start Date', self.plan, default_date=self.start, default_milestone=self.milestone_start)
            self.end, self.milestone_end = get_date(location, f'{label} End Date', self.plan, default_date=self.end, default_milestone=self.milestone_end)
        elif self.duration == DURATION_OPTIONS[4]: # one time
            self.start, self.milestone_start = get_date(location, f'{label} One Time Date', self.plan, default_date=self.start, default_milestone=self.milestone_start)
            self.end = self.start
        


    @property
    def monthly_amount(self) -> Decimal:
        float_amount = float(self.amount)
        if self.frequency == FREQUENCIES[0]: # Daily
            value = f2d(float_amount * 365.0 / 12.0)
        elif self.frequency == FREQUENCIES[1]: # Weekly
            value = f2d(float_amount * 52.0 / 12.0)
        elif self.frequency == FREQUENCIES[2]: # Biweekly
            value = f2d(float_amount * 26.0 / 12.0)
        elif self.frequency in [FREQUENCIES[3], FREQUENCIES[4], FREQUENCIES[5]]: # Monthly , Multiple
            value = self.amount
        else:
            st.error('Cannot compute monthly amount')
        return value
    
    @property
    def start_dateid(self) -> int:
        if self.start is None:
            return date_id(self.configuration.start)
        else:
            return date_id(self.start)

    @property
    def end_dateid(self) -> int:
        if self.end is None:
            return date_id(self.configuration.end)
        else:
            return date_id(self.end)

    @property
    def display_amount(self):
        return float(self.amount)

    def calculate_amount(self, amount: Decimal) -> Decimal:
        return amount

    def set_source_account(self, source_account: str, asset_list: list) -> str:
        return None

    def set_destination_account(self, destination_account: str, asset_list: list) -> str:
        return None

    def configure_source_destination(self):
        return None, None

    @property
    def active_account(self) -> str:
        return self.destination_account

    def date_pass(self, date: int) -> bool:
        date_pass = True
        if self.start is not None:
            if date < date_id(self.start):
                date_pass = False
        if self.end is not None:
            if date > date_id(self.end):
                date_pass = False
        return date_pass

    def update(self, statement_date: datetime.date, period_index: int, plan) -> list:
        if not self.date_pass(date_id(statement_date)):
            return []
        
        self.month_count += 1
        if self.month_gap is not None:
            if self.month_count<self.month_gap:
                return []
            else:
                self.month_count = 0

        account = plan.get_account(self.active_account)
        amount = plan.get_interest_profile(self.interest_profile).calculate_future_value(self.monthly_amount, period_index)
        account.balance += amount
        return [Change(
            self.transaction_type,
            self.name,
            amount,
            statement_date,
            self.active_account,
        )]

class Income(Transaction):
    transaction_type = 'Income'
    description = """`Income` sources define a periodic or single occurence positive transaction to an `Account`.
    
- `Interest Profile` - Each transaction will be adjusted according to the selected `Interest Profile`.
- `Frequency` - All Monthly and shorter frequencies will be converted to the equivalent Monthly cost since the forecast is executed on a monthly period.
- `Amount` - The amount of money added to the `Account` at the selected `Frequency`.
- `Destination Account` - The `Account` into which the `Amount` will be deposited.
- `Duration` - When the `Income` transaction should be executed, e.g. Forever, starting on a date/`Milestone`, between dates, etc.

**Note:** `Amount` should be set according to today's value.  The first (and following) transactions of an `Income` 
set to begin in 10 years with a positive, non-zero `Interest Profile` will be calculated to the Future Value with
compounding interest, i.e. it will be greater than the literal `Amount` entered."""

    def set_source_account(self, source_account: str, asset_list: list) -> str:
        return None

    def set_destination_account(self, destination_account: str, asset_list: list) -> str:
        if destination_account is None:
            return asset_list[0]
        else:
            return destination_account

    def configure_source_destination(self, location, label: str) -> tuple:
        if self.destination_account is not None:
            default = self.destination_account
        else:
            default = self.asset_list[0]
        destination = location.selectbox(f'{label} Destination Account', options=self.asset_list, index=self.asset_list.index(default))
        return None, destination        

class Expense(Transaction):
    transaction_type = 'Expense'
    description = """ `Expenses` are exactly the same as `Income` except that their value will be
removed from the balance of the `Source Account`."""

    @property
    def active_account(self) -> str:
        return self.source_account

    @property
    def display_amount(self):
        return float(self.amount * NEGATIVE_ONE)

    def calculate_amount(self, amount: Decimal) -> Decimal:
        return amount * NEGATIVE_ONE

    def set_source_account(self, source_account: str, asset_list: list) -> str:
        if source_account is None:
            return asset_list[0]
        else:
            return source_account

    def set_destination_account(self, destination_account: str, asset_list: list) -> str:
        return None

    def configure_source_destination(self, location, label: str) -> tuple:
        if self.source_account is not None:
            default = self.source_account
        else:
            default = self.asset_list[0]
        source = location.selectbox(f'{label} Source Account', options=self.asset_list, index=self.asset_list.index(default))
        return source, None

class Transfer(Transaction):
    transaction_type = 'Transfer'
    description = """`Transfers` are exactly the same as both `Income` and `Expense` except that there is both a
`Source Account` and `Destination Account`.  `Transfers` will result in 0 net change in the Net Worth, and they
are simply moving money between `Accounts`.

`Income` sources could be setup such that `Transfers` may be largely unnecessary, but use of `Transfers` may
make the forecast data easier to input and operation slightly more intuitive."""

    def set_source_account(self, source_account: str, asset_list: list) -> str:
        if source_account is None:
            return asset_list[0]
        else:
            return source_account

    def set_destination_account(self, destination_account: str, asset_list: list) -> str:
        if destination_account is None:
            return asset_list[0]
        else:
            return destination_account

    def configure_source_destination(self, location, label: str) -> tuple:
        if self.destination_account is not None:
            destination_default = self.destination_account
        else:
            destination_default = self.asset_list[0]
        left, right = location.columns(2)
        destination = right.selectbox(f'{label} Destination Account', options=self.asset_list, index=self.asset_list.index(destination_default))
        if self.source_account is not None:
            default = self.source_account
        else:
            default = self.asset_list[0]
        source = left.selectbox(f'{label} Source Account', options=self.asset_list, index=self.asset_list.index(default))
        return source, destination

    def update(self, statement_date: datetime.date, period_index: int, plan) -> list:
        if self.date_pass(date_id(statement_date)):
            amount = plan.get_interest_profile(self.interest_profile).calculate_future_value(self.monthly_amount, period_index)
            source_account = plan.get_account(self.source_account)
            source_account.balance -= amount
            destination_account = plan.get_account(self.destination_account)
            destination_account.balance += amount
            return [
                Change(
                    self.transaction_type,
                    self.name,
                    NEGATIVE_ONE * amount,
                    statement_date,
                    source_account.name,
                ),
                Change(
                    self.transaction_type,
                    self.name,
                    amount,
                    statement_date,
                    destination_account.name,
                )
            ]
        else:
            return []