""" Financial Planning App """

import datetime

import streamlit as st
import pandas as pd
import plotly.express as px
import time

from calculate import calculate
from view_configuration import view_configuration
from common import dstr, ZERO
from visualize import visualize_transactions

VERSION = '0.2.0'

st.set_page_config(layout='wide')

f""" # Discrete Financial Forecast"""

st.sidebar.markdown('Thanks for using!')
st.sidebar.markdown(
    '<a href="https://www.buymeacoffee.com/creativerigor" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/default-orange.png" alt="Buy Me A Coffee" height="41" width="174"></a>',
    unsafe_allow_html=True,
)
st.sidebar.markdown('---')
st.sidebar.markdown(f"v{VERSION}")

disable_calculation = st.checkbox('Temporarily Disable Plan Calculation', help=""" The plan will recalculate with each change.  When quickly entering a lot
of data this can get annoying.  The checkbox above will disable calculations (which
will reduce but not completely eliminate this behavior).  Just don't
forget to reactive or there will be no results.""")

plan = view_configuration()

if disable_calculation:
    st.stop()
st.sidebar.markdown('# Plan Execution Results')
start = time.time()
balance_log, transactions_df = calculate(plan)
# Due to streamlit cache requirements of output
tranactions = transactions_df.copy(deep=True)
st.markdown(f'Calculation time: {round(time.time() - start, 1)} seconds')
final_balance =  dstr(balance_log.loc[balance_log['type'] == 'TOTAL', 'balance'].max())
st.sidebar.markdown(f"Final Balance: {final_balance}")

st.sidebar.markdown('# Data Downloads')
st.sidebar.download_button('Balance Log (CSV)', balance_log.to_csv(), file_name=f'{datetime.datetime.today().date()}_balance_log.csv')
st.sidebar.download_button('Transaction Log (CSV)', transactions_df.to_csv(), file_name=f'{datetime.datetime.today().date()}_transaction_log.csv')

if len(tranactions) > 0:
    tranactions['date'] = pd.to_datetime(tranactions['date'])

st.markdown('# Results Visualization')
st.info("""When the graph sections are displayed, they will be re-executed with each modification of the financial plan.

It is recommended to have all graphs off when making many changes to the financial plan.""")

if len(tranactions) < 1:
    st.warning('Please add some income or expenses to see results Visualization')
    st.stop()

if st.checkbox('Show Summary Account View?'):
    
    st.plotly_chart(px.line(
        balance_log,
        x='date',
        y='balance',
        color='account',
        title='Account, Asset, Liability Balances Over Time',
        labels={
            'date': 'Statement Date',
            'balance': 'Balance ($)',
            'account': 'Account, Asset, or Balance',
        }
    ), use_container_width=True)

with st.expander('Expense Views'):
    st.markdown('## Expense Views')
    expenses = tranactions.loc[tranactions['amount'] < ZERO]
    visualize_transactions(expenses, plan, 'Expense')

with st.expander('Income Views'):
    st.markdown('## Income Views')
    incomes = tranactions.loc[tranactions['amount'] > ZERO]
    visualize_transactions(incomes, plan, 'Income')


