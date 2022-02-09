""" Configuration Object """

import datetime

import streamlit as st

from common import get_month

class Configuration:

    def __init__ (
        self,
        start_year: int = None,
        start_month: int = 0,
        duration: int = 10):

        if start_year is None:
            start_year = datetime.datetime.today().year

        self.start_year = start_year
        self.start_month = start_month
        self.duration = duration

    @property
    def end_year(self) -> int:
        return self.start_year + self.duration
        
    @property
    def end_month(self) -> int:
        return self.start_month

    @property
    def start(self) -> datetime.date:
        return datetime.date(self.start_year, self.start_month+1, 1)

    @property
    def end(self) -> datetime.date:
        return datetime.date(self.end_year, self.end_month+1, 1)

    @property
    def display_date_range(self) -> str:
        return f'Plan configured from `{self.start_year}-{self.start_month+1}` to `{self.end_year}-{self.end_month+1}`'

    @property
    def summary(self) -> str:
        return f"""Configuration: `{self.start_year}-{self.start_month+1}` to `{self.end_year}-{self.end_month+1}` ({self.duration} Years)"""

    def to_dict(self) -> dict:
        return {
            'start_year': self.start_year,
            'start_month': self.start_month,
            'duration': self.duration,
        }

    def configure(self):
        st.markdown(""" This section simply configures the timeframe for your forecast.  The forecast will begin on the
selected `Starting Year` and `Starting Month` and run through the `Plan Duration` of years in monthly increments.

---""")
        left, middle, right = st.columns(3)
        self.start_year = int(left.number_input('Starting Year', min_value=1900, step=1, value=self.start_year))
        self.start_month = get_month(label='Starting Month', holder=middle, default=self.start_month)
        self.duration = int(right.number_input(label='Plan Duration (years)', value=self.duration, min_value=1, step=1))
        st.markdown(self.display_date_range)
        

        

    