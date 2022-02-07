""" Plan Object """

import streamlit as st
import pandas as pd

from Configuration import Configuration
from Assets import Asset, Account, Liability
from Transaction import Income, Expense, Transfer
from Mortgage import Mortgage
from InterestProfile import InterestProfile
from Milestone import Milestone

class Plan:

    def __init__(self, saved_plan: dict):
        self.configuration = Configuration(**saved_plan.get('configuration', {}))
        self.milestones = [Milestone(i+1, self.configuration.start, self.configuration.end, **item) for i, item in enumerate(saved_plan.get('milestones', []))]
        self.interest_profiles = [InterestProfile(i+1, self.configuration.start, self.configuration.end, **item) for i, item in enumerate(saved_plan.get('interest_profiles', []))]
        if len(self.interest_profiles) < 1:
            self.interest_profiles.extend([                
                InterestProfile(
                    1,
                    self.configuration.start,
                    self.configuration.end,
                    name='No Interest',
                    profile_type='Constant',
                    profile_phases=[{'phase_type': 'Constant', 'rate': 0.0}]
                ),
                InterestProfile(
                    2,
                    self.configuration.start, 
                    self.configuration.end, 
                    name='Inflation', 
                    profile_type='Constant',
                    profile_phases=[{'phase_type': 'Constant', 'rate': 2.0}]
                )]
            )
        self.assets = [Asset(i+1, self, **item) for i, item in enumerate(saved_plan.get('assets', []))]
        self.accounts = [Account(i+1, self, **item) for i, item in enumerate(saved_plan.get('accounts', []))]
        self.liabilities = [Liability(i+1, self, **item) for i, item in enumerate(saved_plan.get('liabilities', []))]
        self.incomes = [Income(i, self, **item) for i, item in enumerate(saved_plan.get('incomes', []))]
        self.expenses = [Expense(i, self, **item) for i, item in enumerate(saved_plan.get('expenses', []))]
        self.transfers = [Transfer(i, self, **item) for i, item in enumerate(saved_plan.get('transfers', []))]
        self.mortgages = [Mortgage(i, self.account_names, self.liability_names, **item) for i, item in enumerate(saved_plan.get('mortgages', []))]
        self.all_lists = [
            ('Milestones', self.milestones),
            ('Interest Profiles', self.interest_profiles),
            ('Asset', self.assets),
            ('Account', self.accounts),
            ('Liability', self.liabilities),
            ('Income', self.incomes),
            ('Expense', self.expenses),
            ('Transfer', self.transfers),
            ('Mortgage', self.mortgages),
        ]

    def to_dict(self):
        return {
            'configuration': self.configuration.to_dict(),
            'milestones': [milestone.to_dict() for milestone in self.milestones],
            'interest_profiles': [profile.to_dict() for profile in self.interest_profiles],
            'assets': [asset.to_dict() for asset in self.assets],
            'accounts': [asset.to_dict() for asset in self.accounts],
            'liabilities': [asset.to_dict() for asset in self.liabilities],
            'incomes': [income.to_dict() for income in self.incomes],
            'expenses': [expense.to_dict() for expense in self.expenses],
            'transfers': [transfer.to_dict() for transfer in self.transfers],
            'mortgages': [mortgage.to_dict() for mortgage in self.mortgages],
        }

    @property
    def account_names(self) -> list:
        return [account.name for account in self.accounts]

    @property
    def liability_names(self) -> list:
        return [liability.name for liability in self.liabilities]

    @property
    def interest_profile_names(self) -> list:
        return [profile.name for profile in self.interest_profiles]

    @property
    def milestone_names(self) -> list:
        return [milestone.name for milestone in self.milestones]

    @property
    def table_summary(self) -> pd.DataFrame:
        data = [len(item_list) for _, item_list in self.all_lists]
        index = [name for name, _ in self.all_lists]
        frame = pd.DataFrame(data, index=index)
        frame.columns = ['Quantity']
        return frame

    def asset_builder(self, i: int, Builder):
        return Builder(i, self)

    def transaction_builder(self, i: int, Builder):
        return Builder(i, self)

    def mortgage_builder(self, i: int, Builder):
        return Builder(i, self.account_names, self.liability_names)

    def interest_profile_builder(self, i: int, Builder):
        return Builder(i, self.configuration.start, self.configuration.end)

    def get_account(self, account_name: str) -> Account:
        return self.accounts[self.account_names.index(account_name)]

    def get_liability(self, liability_name: str) -> Liability:
        return self.liabilities[self.liability_names.index(liability_name)]

    def get_interest_profile(self, profile_name: str) -> InterestProfile:
        return self.interest_profiles[self.interest_profile_names.index(profile_name)]

    def get_milestone(self, milestone_name: str) -> Milestone:
        return self.milestones[self.milestone_names.index(milestone_name)]

    def configure(self):
        with st.expander('Plan Configuration'):
            self.configuration.configure()
        asset_types = [
            ('Milestone', 0, self.milestones, 'milestones', Milestone, self.interest_profile_builder),
            ('Interest Profile', 1, self.interest_profiles, 'interest_profiles', InterestProfile, self.interest_profile_builder),
            ('Account', 1, self.accounts, 'accounts', Account, self.asset_builder),
            ('Asset', 0, self.assets, 'assets', Asset, self.asset_builder),
            ('Liability', 0, self.liabilities, 'liabilities', Liability, self.asset_builder),
            ('Income', 0, self.incomes, 'incomes', Income, self.transaction_builder),
            ('Expense', 0, self.expenses, 'expenses', Expense, self.transaction_builder),
            ('Transfer', 0, self.transfers, 'transfers', Transfer, self.transaction_builder),
            ('Mortgage', 0, self.mortgages, 'mortgages', Mortgage, self.mortgage_builder),
        ]
        for asset_name, min_quantity, asset_group, attribute_name, AssetType, builder in asset_types:
            with st.expander(f'{asset_name}(s)'):
                new_list = []
                header_info = st.empty()
                list_placeholder = st.container()
                st.markdown('---')
                quantity = int(st.number_input(f'{asset_name} Quantity', min_value=min_quantity, value=max(len(asset_group), min_quantity)))
                header_info = header_info.markdown(f'{quantity} Items defined for {asset_name}')
                for i in range(quantity):
                    try:
                        asset = asset_group[i]
                    except IndexError:
                        asset = builder(i+1, AssetType)
                    asset.configure(list_placeholder)
                    new_list.append(asset)
                setattr(self, attribute_name, new_list)
