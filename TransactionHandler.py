""" Transaction Handler """

import datetime
from decimal import Decimal

import streamlit as st
import pandas as pd

from common import (
    f2d,
    select_frequency,
    get_growth_rate,
    date_id,
)

class TransactionHandler:

    def __init__(self, plan: dict):
        self.plan = plan
        configuration = plan['configuration']
        accounts = plan['accounts']
        self.start = datetime.date(configuration['start_year'], configuration['start_month']+1, 1)
        self.end = datetime.date(configuration['$end_year'], configuration['$end_month']+1, 1)
        self.default_inflation = configuration['$default_inflation']
        self.accounts = pd.DataFrame(accounts)

    def transaction_input(
        self,
        label: str = 'Transaction',
        destination_account: bool = False,
        existing: dict = None,
        factor: Decimal = None) -> dict:

        if factor is None:
            factor = Decimal('1.0')

        if existing is None:
            item = {}
        else:
            item = existing
        item['name'] = st.text_input(f'{label} Name', value=item.get('name', label))
        item['growth_type'], growth = get_growth_rate(label_prepend=label, default_type=item.get('growth_type', None), default_growth=item.get('growth', None))
        if growth is not None:
            item['growth'] = growth
        left, right = st.columns(2)
        item['amount'] = f2d(left.number_input(f'{label} Amount', min_value=0.0, value=float(item.get('amount', 0.00))))
        item['$amount'] = factor * item['amount']
        item['frequency'] = select_frequency(right, label_prepend=label, default=item.get('frequency', None))
        account_name_list = list(self.accounts['name'])
        item['source_account'] = left.selectbox(f'{label} Source Account', options=account_name_list, index=account_name_list.index(item.get('source_account', account_name_list[0])))
        if destination_account:   
            item['destination_account'] = right.selectbox(f'{label} Destination Account', options=account_name_list, index=account_name_list.index(item.get('destination_account', account_name_list[0])))
        duration_options = ['Forever', 'Date Range', 'End Date Only', 'Start Date Only']
        item['duration'] = st.radio(f'{label} Duration', options=duration_options, index=duration_options.index(item.get('duration', duration_options[0])))
        if item['duration'] == 'End Date Only':
            item['end'] = st.date_input(f'{label} End Date', value=item.get('end', self.end))
        if item['duration'] == 'Start Date Only':
            item['start'] = st.date_input(f'{label} Start Date', value=item.get('start', self.start))
        elif item['duration'] == 'Date Range':
            st.info('Only the month/year info is used.')
            left, right = st.columns(2)
            item['start'] = left.date_input(f'{label} Start Date', value=item.get('start', self.start))
            item['end'] = right.date_input(f'{label} End Date', value=item.get('end', self.end))
        return item

    def augment_configuration(self) -> dict:
        #Calculate start and end
        keys = ['incomes', 'expenses', 'transfers']
        for key in keys:
            for item in self.plan[key]:
                item['$start'] = date_id(item.get('start', self.start))
                item['$end'] = date_id(item.get('end', self.end))
        return self.plan

    def growth_update(self, items: list) -> list:
        for item in items:
            growth_type = item.get('growth_type', 'Inflation')
            if growth_type == 'Inflation':
                interest = self.default_inflation
            elif growth_type == 'None':
                interest = 0.0
            elif growth_type == 'Custom':
                interest = item.get('growth', self.default_inflation*100.0)/100.0
            else:
                st.error(f'Unknown Growth Type: {growth_type}')
            item['$interest'] = interest
        return items

