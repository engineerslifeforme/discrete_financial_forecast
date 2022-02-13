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
from query_to_plan import plan_to_query, plan_to_compressed_str

VERSION = '1.0.4'

st.set_page_config(page_title='Discrete Financial Forecast', layout='wide')

f""" # Discrete Financial Forecast """

with st.expander('Introduction', expanded=True):
    st.markdown("""Welcome to the Discrete Financial Forecast webapp.  This app attempts to perform a [Discrete-event simulation](https://en.wikipedia.org/wiki/Discrete-event_simulation)
of your finances (don't be intimidated).  The goal is to make very few assumptions about your data, so the "accuracy"
will depend on the level of detail you provide and how well you can predict your own financial behavior.

#### Getting Started 

Simply expand each of the categories below and begin entering your data.  There will be additional instructions
in each section.

This app does not retain any of your data once you leave, so you are encouraged to periodically save (`Configuration Download (YAML)`)
a configuration file for your forecast.  This file can then be uploaded to restart/review your plan at a later time using the
`Previous Plan Upload`.

Once you have some data entered, you can begin viewing in the `Results Visualization` section below.

If you run into an issue, please report it here: [Github Repo](https://github.com/engineerslifeforme/discrete_financial_forecast/issues).
Or you can review the source code if you are into that sort of thing.

#### Disclaimer

I am not a financial professional and:
> THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE. """)

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

if len(tranactions) > 0:
    tranactions['date'] = pd.to_datetime(tranactions['date'])

st.markdown('# Results')

st.markdown(f'Calculation time: {round(time.time() - start, 1)} seconds')
final_balance =  dstr(balance_log.loc[balance_log['type'] == 'TOTAL', 'balance'].max())
st.sidebar.markdown(f"Final Balance: {final_balance}")
st.markdown("""See the `Final Balance` in the sidbar on the left as well as download buttons for the resulting forecast data:

- `Balance Log (CSV)`: The balance of each account at each month interval
- `Transaction Log (CSV)`: Each transaction for each `Account` and `Liability`

You are highly encouraged to double check this app's math and/or experiment with different visualizations""")

st.sidebar.markdown('# Data Downloads')
balance_csv = balance_log.to_csv()
transaction_csv = transactions_df.to_csv()
st.sidebar.download_button('Balance Log (CSV)', balance_csv, file_name=f'{datetime.datetime.today().date()}_balance_log.csv')
st.sidebar.download_button('Transaction Log (CSV)', transaction_csv, file_name=f'{datetime.datetime.today().date()}_transaction_log.csv')

st.markdown('## Visualization')
st.info("""When the graph sections are displayed, they will be re-executed with each modification of the financial plan.

It is recommended to have all graphs off when making many successive changes to the financial plan.  Graphing can be left active
when iteratively changing values and reviewing their effects.""")

st.markdown("""The plots below are generated with the plotting library [plotly](https://plotly.com/).
They are interactive allowing click and drag zooming, hovering over points, and filtering by series by
clicking the legend.  Hovering over the graph will additionally provide a graph menu in the top right
with additional options, and an expand icon to view the graph(s) using the full browser window.""")

if len(tranactions) < 1:
    st.warning('Please add some income or expenses to see results Visualization')
else:
    if st.checkbox('Show Balance Summary View?'):

        st.markdown("""## Balance Summary View
        
`TOTAL` is the periodic sum of all `Accounts`, `Assets`, and `Liabilities` (negative value),
so Net Worth.""")
        
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

""" # Feedback

Feedback in welcome in the form of  [Github Issues](https://github.com/engineerslifeforme/discrete_financial_forecast/issues)
on this project.  creativerigor [at] gmail.com is also checked from time to time.

While [Buy me a coffee](https://www.buymeacoffee.com/creativerigor) may incentivize requested features, submitting the 
issue first just to check whether it is feasible and/or makes sense is recommended.  Expectation management."""

"""# Shareable Link """
st.markdown(f'Copy this link to share with others: [Shareable Link](http://localhost:8501/{plan_to_compressed_str(plan)})')

st.markdown("""**Note:** 

- This link simply allows others to see a copy of the forecast, i.e., changes made by others will not be reflected back.
- This link changes any time the plan is changed, i.e., you cannot just bookmark it.""")
