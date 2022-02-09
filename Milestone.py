""" Milestone Class """

import datetime

import streamlit as st

class Milestone:
    description = """`Milestones` are simply named dates that can be used later in the definition of `Income`, `Expenses` and `Transfers`.
        
**Milestones are optional**
"""

    def __init__(
        self,
        unique_id: int,
        configuration_start: datetime.date,
        configuration_end: datetime.date,
        name: str = None,
        date: datetime.date = None):

        self.unique_id = unique_id
        self.configuration_start = configuration_start
        self.configuration_end = configuration_end
        if name is None:
            self.name = f'Milestone #{unique_id}'
        else:
            self.name = name
        if date is None:
            self.date = self.configuration_start
        else:
            self.date = date        

    def to_dict(self) -> dict:
        return {
            'name': self.name,
            'date': self.date,
        }

    def configure(self, location):
        label = f'Milestone #{self.unique_id}'
        location.markdown('---')
        left, right = location.columns(2)
        self.name = left.text_input(f'{label} Name', value=self.name)
        self.date = right.date_input(f'{label} Date', value=self.date, min_value=self.configuration_start, max_value=self.configuration_end)

