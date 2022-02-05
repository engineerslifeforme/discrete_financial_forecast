""" Common Functions """

import datetime
from decimal import Decimal
import math

import streamlit as st

MONTHS = [
    'January',
    'February',
    'March',
    'April',
    'May',
    'June',
    'July',
    'August',
    'September',
    'October',
    'November',
    'December',
]
INFLATION_LABEL = 'Inflation'
NEGATIVE_ONE = Decimal('-1.0')
ZERO = Decimal('0.00')

def get_month(label: str = 'Month', holder = None, default: int = 0) -> int:
    if holder is None:
        location = st
    else:
        location = holder
    return MONTHS.index(location.selectbox(label, options=MONTHS, index=default))

def date_id(date: datetime.date) -> int:
    return year_month_id(date.year, date.month)

def year_month_id(year: int, month: int) -> int:
    return year*12 + month

def id_to_date(date_id: int) -> datetime.date:
    month = (date_id % 12)
    year = int((date_id - month) / 12)
    return datetime.date(year, month + 1, 1)

def get_growth_rate(label_prepend: str = '', default_type: str = None, default_growth: float = None):
    left, middle, right = st.columns(3)
    options = ['None', 'Inflation', 'Custom']
    if default_type is not None:
        default_type = options.index(default_type)
    else:
        default_type = 1
    growth_type = left.radio(f'{label_prepend} Growth', options=options, index=default_type)
    if growth_type == 'None':
        growth = None
    elif growth_type == 'Inflation':
        growth = None
    elif growth_type == 'Custom':
        if default_growth is not None:
            default_value = default_growth
        else:
            default_growth = 0.0
        growth = middle.number_input(f'{label_prepend} Growth Rate (%/year)', value=default_growth, step=0.01)
    else:
        st.error(f'Unknown growth rate type {growth_type}')
    return growth_type, growth

def f2d(value: float):
    return Decimal(str(value))

def future_value(investment: Decimal, rate: float, periods: int) -> Decimal:
    """ Compute future value
    :param investment: base amount
    :type investment: decimal
    :param rate: rate of change per period
    :type rate: decimal
    :param periods: number of periods into future
    :type periods: int
    :return: new future value
    :rtype: decimal
    https://www.investopedia.com/terms/f/futurevalue.asp#:~:text=Future%20value%20(FV)%20is%20the,be%20worth%20in%20the%20future.
    """
    return investment * f2d((1 + (rate * periods)))

def mortgage_payment(principal: Decimal, interest: float, periods: int) -> Decimal:
    return round((principal * f2d(interest))/f2d(1 - math.pow(1 + interest, -1 * periods)), 2)

def dstr(number) -> str:
    return "${:,.2f}".format(number)
