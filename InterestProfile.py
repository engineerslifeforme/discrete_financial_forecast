""" InterestProfile class """

import datetime
from decimal import Decimal

import streamlit as st

from common import date_id, f2d

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
        profile_start: datetime.date,
        profile_end: datetime.date,        
        start: datetime.date = None,
        end: datetime.date = None,
        phase_type: str = PHASE_TYPES[0],
        rate: float = DEFAULT_RATE):

        self.unique_id = unique_id
        self.profile_start = profile_start
        self.profile_end = profile_end
        self.phase_type = phase_type
        self.rate = rate
        self.start = start
        self.end = end
        self.prepend = prepend

    def to_dict(self) -> dict:
        data = {
            'phase_type': self.phase_type,
            'rate': self.rate,
        }
        if self.start is not None:
            data['start'] = self.start
        if self.end is not None:
            data['end'] = self.end
        data = self.update_dict(data)
        return data

    def update_dict(self, data: dict) -> dict:
        return data

    @property
    def _start(self) -> datetime.date:
        if self.start is None:
            return self.profile_start
        else:
            return self.start

    @property
    def _end(self) -> datetime.date:
        if self.end is None:
            return self.profile_end
        else:
            return self.end

    @property
    def label(self) -> str:
        return f'{self.prepend} {self.base_label} #{self.unique_id}'

    def get_profile(self) -> list:
        return []

    def configure(self):
        pass

class ConstantPhase(InterestPhase):
    base_label = 'Constant'

    def get_profile(self) -> list:
        start = date_id(self._start)
        end = date_id(self._end)
        current = start
        profile = []
        while current < end:
            # constant
            profile.append(yearly_percentage_to_monthly(self.rate))
            current += 1
        return profile

    def configure(self):
        self.rate = st.number_input(f'{self.label} Constant Rate (%/year)', value=self.rate, step=0.01)  

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

    def configure(self):
        left, right = st.columns(2)
        self.start_rate = left.number_input(f'{self.label} Start Rate (%/year)', value=self.start_rate, step=0.01)
        self.end_rate = right.number_input(f'{self.label} End Rate (%/year)', value=self.end_rate, step=0.01)

    def get_profile(self) -> list:
        start = date_id(self._start)
        end = date_id(self._end)

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

    def __init__(
        self,
        unique_id: int,
        start: datetime.date,
        end: datetime.date,
        name: str = None,
        profile_type: str = PROFILE_TYPES[0],
        profile_phases: list = None):
        
        self.unique_id = unique_id
        self.label = f'Interest Profile #{self.unique_id}'
        self.start = start
        self.end = end
        if name is None:
            self.name = f'Interest Profile #{unique_id}'
        else:
            self.name = name
        self.profile_type = profile_type
        self.interest_phases = self.initialize_phases(profile_phases)        

    def initialize_phases(self, phases: list) -> list:
        new_list = []
        if phases is not None:
            for i, phase in enumerate(phases):
                new_list.append(PHASE_MAP[phase['phase_type']](
                    i+1,
                    self.label,
                    self.start,
                    self.end,
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
            profile.extend(phase.get_profile())
        return profile

    def configure(self):
        st.markdown('---')
        left, right = st.columns(2)
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
                    first_phase.configure()
            else:
                create_default = True
            if create_default:
                phase = ConstantPhase(
                    1,
                    self.label,
                    self.start,
                    self.end,
                )
                phase.configure()
                self.interest_phases = [phase]
        elif self.profile_type == PROFILE_TYPES[1]: # Linear
            create_default = False
            if self.interest_phases is not None:
                first_phase = self.interest_phases[0]
                if first_phase.phase_type != PHASE_TYPES[1] or len(self.interest_phases) > 1: # bad
                    create_default = True
                else: # good
                    first_phase.configure()
            else:
                create_default = True
            if create_default:
                phase = LinearPhase(
                    1,
                    self.label,
                    self.start,
                    self.end,
                )
                phase.configure()
                self.interest_phases = [phase]
        # elif Piecewise
            # handle the dates here, not in phases

    def calculate_future_value(self, value: Decimal, period_index: int) -> Decimal:
        counter = 0
        profile = self.get_profile()
        current_value = float(value)
        while counter <= period_index:
            current_value = current_value * (1.0 + profile[counter])
            counter += 1
        return round(f2d(current_value), 2)