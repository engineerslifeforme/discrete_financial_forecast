""" InterestProfile class """

import datetime
from decimal import Decimal

import streamlit as st

from common import date_id, f2d, future_value

PROFILE_TYPES = [
    'Constant',
    'Linear',
    #'Complex / Piece Wise',
]

PHASE_TYPES = [
    'Constant',
    'Linear',
]

DEFAULT_RATE = 2.0

def yearly_percentage_to_monthly(rate: float) -> float:
    return rate / 100.0 / 12.0

class InterestPhase:
    base_label = 'Default'

    def __init__(
        self,
        unique_id: int,
        prepend: str,
        phase_type: str = PHASE_TYPES[0],
        rate: float = DEFAULT_RATE):

        self.unique_id = unique_id
        self.phase_type = phase_type
        self.rate = rate
        self.prepend = prepend

    def to_dict(self) -> dict:
        data = {
            'phase_type': self.phase_type,
            'rate': self.rate,
        }
        data = self.update_dict(data)
        return data

    def update_dict(self, data: dict) -> dict:
        return data

    @property
    def label(self) -> str:
        return f'{self.prepend} {self.base_label} #{self.unique_id}'

    def get_profile(self) -> list:
        return []

    def configure(self):
        pass

class ConstantPhase(InterestPhase):
    base_label = 'Constant'

    def get_profile(self, start:datetime.date, end:datetime.date) -> list:
        start = date_id(start)
        end = date_id(end)
        current = start
        profile = []
        while current < end:
            # constant
            profile.append(yearly_percentage_to_monthly(self.rate))
            current += 1
        return profile

    def configure(self, location):
        self.rate = location.number_input(f'{self.label} Constant Rate (%/year)', value=self.rate, step=0.01)

    @property
    def monthly_rate(self) -> float:
        return yearly_percentage_to_monthly(self.rate)

class LinearPhase(InterestPhase):
    base_label = 'Linear'

    def __init__(
        self,
        *args,
        start_rate: float = DEFAULT_RATE,
        end_rate: float = DEFAULT_RATE,
        **kwargs):

        super().__init__(*args, **kwargs)
        self.start_rate = start_rate
        self.end_rate = end_rate

    def update_dict(self, data: dict) -> dict:
        data['start_rate'] = self.start_rate
        data['end_rate'] = self.end_rate

    @property
    def _start_rate(self) -> float:
        return yearly_percentage_to_monthly(self.start_rate)

    @property
    def _end_rate(self) -> float:
        return yearly_percentage_to_monthly(self.end_rate)

    def configure(self, location):
        left, right = location.columns(2)
        self.start_rate = left.number_input(f'{self.label} Start Rate (%/year)', value=self.start_rate, step=0.01)
        self.end_rate = right.number_input(f'{self.label} End Rate (%/year)', value=self.end_rate, step=0.01)

    def get_profile(self, start: datetime.date, end: datetime.date) -> list:
        start = date_id(start)
        end = date_id(end)

        increment = (self._end_rate - self._start_rate) / (end - start)

        current = start
        profile = []
        while current < end:
            profile.append(self._start_rate + ((current - start) * increment))
            current += 1
        return profile

PHASE_MAP = {
    PHASE_TYPES[0]: ConstantPhase,
    PHASE_TYPES[1]: LinearPhase
}      

class InterestProfile:
    description = """ `Interest Profiles` allow the application of different rates of appreciation
for `Income`, `Expense`, and `Transfer` transactions as well as the value of `Accounts`, `Assets`, and `Liabilities`.

For example, a "Groceries" `Expense` can be set to an `Interest Profile` of "Inflation" causing the bill to increase
over time through the forecast at the defined %/year interest rate.  Similarly (and hopefully at a minimum), `Income` sources
can simultaneously be assigned "Inflation" causing the `Income` to proportionally grow over time.

Some `Liabilities` such as mortgages and loans do not increase over time and therefore can use a "No Interest" `Interest Profile`.

`Accounts` that are invested can use a different (and hopefully higher) appreciation rate `Interest Profile`.

** It is recommended (but not required) that you do not remove or rename the "Inflation" and "No Interest" `Interest Profiles`.
Do feel free to change the "Inflation" rate if you disagree with the default.**

**Note:** Only `Accounts`, `Assets`, and `Liabilities` with positive, non-zero balances will accrue interest."""

    def __init__(
        self,
        unique_id: int,
        configuration,
        name: str = None,
        profile_type: str = PROFILE_TYPES[0],
        profile_phases: list = None):
        
        self.unique_id = unique_id
        self.configuration = configuration
        self.label = f'Interest Profile #{self.unique_id}'
        if name is None:
            self.name = f'Interest Profile #{unique_id}'
        else:
            self.name = name
        self.profile_type = profile_type
        self.interest_phases = self.initialize_phases(profile_phases)        
        

    @property
    def start(self) -> datetime.date:
        return self.configuration.start

    @property
    def end(self) -> datetime.date:
        return self.configuration.end
    
    def initialize_phases(self, phases: list) -> list:
        new_list = []
        if phases is not None:
            for i, phase in enumerate(phases):
                new_list.append(PHASE_MAP[phase['phase_type']](
                    i+1,
                    self.label,
                    **phase,
                ))
        else:
            return None
        return new_list

    def to_dict(self) -> dict:
        return {
            'name': self.name,
            'profile_type': self.profile_type,
            'profile_phases': [phase.to_dict() for phase in self.interest_phases],
        }

    def get_profile(self) -> list:
        profile = []
        for phase in self.interest_phases:
            profile.extend(phase.get_profile(self.start, self.end))
        return profile

    def configure(self, location):
        location.markdown('---')
        left, right = location.columns(2)
        self.name = left.text_input(f'{self.label} Name', value=self.name)
        self.profile_type = right.selectbox(f'{self.label} Type', options=PROFILE_TYPES, index=PROFILE_TYPES.index(self.profile_type))
        # Need a none
        if self.profile_type == PROFILE_TYPES[0]: # Constant
            create_default = False
            if self.interest_phases is not None:
                first_phase = self.interest_phases[0]
                if first_phase.phase_type != PHASE_TYPES[0] or len(self.interest_phases) > 1: # bad
                    create_default = True
                else: # good
                    first_phase.configure(location)
            else:
                create_default = True
            if create_default:
                phase = ConstantPhase(
                    1,
                    self.label,
                )
                phase.configure(location)
                self.interest_phases = [phase]
        elif self.profile_type == PROFILE_TYPES[1]: # Linear
            create_default = False
            if self.interest_phases is not None:
                first_phase = self.interest_phases[0]
                if first_phase.phase_type != PHASE_TYPES[1] or len(self.interest_phases) > 1: # bad
                    create_default = True
                else: # good
                    first_phase.configure(location)
            else:
                create_default = True
            if create_default:
                phase = LinearPhase(
                    1,
                    self.label,
                )
                phase.configure(location)
                self.interest_phases = [phase]
        # elif Piecewise
            # handle the dates here, not in phases

    def calculate_future_value(self, value: Decimal, period_index: int) -> Decimal:
        if self.profile_type == PROFILE_TYPES[0]: # Constant:
            result = round(future_value(value, self.interest_phases[0].monthly_rate, period_index), 2)
        else:
            counter = 0
            profile = self.get_profile()
            current_value = float(value)
            while counter < period_index:
                current_value = current_value * (1.0 + profile[counter])
                counter += 1
            result = round(f2d(current_value), 2)
        return result
