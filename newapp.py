""" Financial Planning App """

import datetime

import streamlit as st
import pandas as pd
import plotly.express as px
import time

from calculate import calculate
from view_configuration import view_configuration
from common import dstr, ZERO

st.set_page_config(layout='wide')

""" # Discrete Financial Forecast """

disable_calculation = st.checkbox('Temporarily Disable Plan Calculation')
st.info(""" The plan will recalculate with each change.  When quickly entering a lot
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
    ))

with st.expander('Expense Views'):
    st.markdown('## Expense Views')
    expenses = tranactions.loc[tranactions['amount'] < ZERO]
    if len(expenses) > 0:
        expense_types = expenses['type'].unique()
        displayed_types = st.multiselect('Expense Types to Display', options=expense_types, default=expense_types)
        displayed_expenses = expenses.loc[expenses['type'].isin(displayed_types)]
        displayed_expenses['abs_amount'] = displayed_expenses['amount'].abs()
        
        if st.checkbox('Expense Time View'):
            options = [year for year in range(plan.configuration.start.year, plan.configuration.end.year + 1)]
            selected_year = st.selectbox('Expense Year', index=0, options=options)
            displayed_expenses['year'] = displayed_expenses['date'].dt.year
            displayed_expenses['float_amount'] = displayed_expenses['abs_amount'].astype(float)
            st.plotly_chart(px.bar(
                displayed_expenses.loc[displayed_expenses['year'] == selected_year, :],
                x='date',
                y='abs_amount',
                color='name',
            ))

        if st.checkbox('Total Expenses'):
            # TODO: Need to group here
            st.plotly_chart(px.bar(
                displayed_expenses.groupby('name').sum().reset_index(drop=False),
                x='name',
                y='abs_amount',
                color='name',
            ))
    else:
        st.warning('The current plan to does have any expenses!')
    