""" Visualization """

import streamlit as st
import pandas as pd
import plotly.express as px

def visualize_transactions(transactions: pd.DataFrame, plan, label: str):
    if len(transactions) > 0:
        expense_types = transactions['type'].unique()
        displayed_types = st.multiselect(f'{label} Types to Display', options=expense_types, default=expense_types)
        displayed_transactions = transactions.loc[transactions['type'].isin(displayed_types)]
        displayed_transactions['abs_amount'] = displayed_transactions['amount'].abs()
        
        if st.checkbox(f'{label} Time View'):
            options = [year for year in range(plan.configuration.start.year, plan.configuration.end.year + 1)]
            selected_year = st.selectbox(f'{label} Year', index=0, options=options)
            displayed_transactions['year'] = displayed_transactions['date'].dt.year
            displayed_transactions['float_amount'] = displayed_transactions['abs_amount'].astype(float)
            st.plotly_chart(px.bar(
                displayed_transactions.loc[displayed_transactions['year'] == selected_year, :],
                x='date',
                y='abs_amount',
                color='name',
            ))

        if st.checkbox(f'Total {label}(s)'):
            # TODO: Need to group here
            st.plotly_chart(px.bar(
                displayed_transactions.groupby('name').sum().reset_index(drop=False),
                x='name',
                y='abs_amount',
                color='name',
            ))
    else:
        st.warning('The current plan to does have any expenses!')