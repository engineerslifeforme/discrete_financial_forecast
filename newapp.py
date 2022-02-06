""" Financial Planning App """

import datetime

import streamlit as st
import pandas as pd
import plotly.express as px
import time

from calculate import calculate
from view_configuration import view_configuration
from common import dstr

st.set_page_config(layout='wide')

""" # Financial Planner """

plan = view_configuration()

st.sidebar.markdown('# Plan Execution Results')
start = time.time()
balance_log, transactions_df = calculate(plan)
st.markdown(f'Calculation time: {round(time.time() - start, 1)} seconds')
final_balance =  dstr(balance_log.loc[balance_log['type'] == 'TOTAL', 'balance'].max())
st.sidebar.markdown(f"Final Balance: {final_balance}")

st.sidebar.markdown('# Data Downloads')
st.sidebar.download_button('Balance Log (CSV)', balance_log.to_csv(), file_name=f'{datetime.datetime.today().date()}_balance_log.csv')
st.sidebar.download_button('Transaction Log (CSV)', transactions_df.to_csv(), file_name=f'{datetime.datetime.today().date()}_transaction_log.csv')

st.markdown('# Results Configuration')
if st.checkbox('Live Results? (Slower)'):
    
    st.plotly_chart(px.line(
        balance_log,
        x='date',
        y='balance',
        color='account',
    ))