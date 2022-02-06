""" Plan computation """

import streamlit as st
import pandas as pd
from stqdm import stqdm

from Plan import Plan
from common import year_month_id, id_to_date, ZERO

def calculate(plan: Plan) -> tuple:
    start_date_id = year_month_id(plan.configuration.start_year, plan.configuration.start_month)
    end_date_id = year_month_id(plan.configuration.end_year, plan.configuration.end_month)

    current_date_id = start_date_id
    balance_log = []
    transactions = []

    for current_date_id in stqdm(range(start_date_id, end_date_id)):
        periods_since_start = current_date_id - start_date_id
        statement_date = id_to_date(current_date_id + 1) # Show balance as the first of the following month
        
        total = ZERO
        for asset_list in [plan.accounts, plan.assets, plan.liabilities]:
            for asset_item in asset_list:
                transactions.extend(asset_item.update(statement_date, periods_since_start, plan))

        for transaction_list in [plan.incomes, plan.expenses, plan.transfers, plan.mortgages]:
            for item in transaction_list:
                transactions.extend(item.update(statement_date, periods_since_start, plan))

        for asset_list in [plan.accounts, plan.assets, plan.liabilities]:
            for asset_item in asset_list:
                total += asset_item.balance
                balance_log.append({
                    'balance': asset_item.balance,
                    'date': statement_date,
                    'account': asset_item.name,
                    'type': asset_item.asset_class,
                })
        balance_log.append({
            'balance': total,
            'date': statement_date,
            'account': 'TOTAL',
            'type': 'TOTAL',
        })

    st.sidebar.markdown(f'Months assessed: {end_date_id - start_date_id}')
    balance_log = pd.DataFrame(balance_log)
    transactions_df = pd.DataFrame([change.to_dict() for change in transactions])
    return balance_log, transactions_df