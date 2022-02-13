""" Main view configuration """

import datetime

import streamlit as st
import yaml
from jinja2 import Template

from Plan import Plan
from YamlHandler import split_constants, load_yaml
from query_to_plan import query_to_plan

def configure_constants(constants: dict) -> dict:
    new_constants = {}
    keys_of_interest = st.multiselect('Constants to modify', options=list(constants.keys()))
    for key in constants:
        if key in keys_of_interest:
            value_type = type(constants[key])
            if value_type == datetime.date:
                new_value = st.date_input(f'{key}', value=constants[key])
            elif value_type == float:
                new_value = st.number_input(f'{key}', value=constants[key])
            else:
                st.error(f'Could match {key} {constants[key]} of type {value_type}')            
        else:
            new_value = constants[key]
        new_constants[key] = new_value
    return new_constants

def view_configuration() -> Plan:
    st.sidebar.markdown('# Editor Configuration')
    EDITOR_MODES = ['GUI Configuration', 'Manual Configuration', 'View Only', 'Plan Comparison', 'Documentation']
    editor_mode = st.sidebar.radio(' Editor Mode', options=EDITOR_MODES)

    previous_plan_upload = st.file_uploader('Previous Plan Upload')
    if previous_plan_upload is not None:
        upload_content = previous_plan_upload.getvalue().decode('utf-8')
    else:
        upload_content = None

    query_plan_dict = query_to_plan(st.experimental_get_query_params())
    #st.write(query_plan_dict)

    if editor_mode == EDITOR_MODES[0]: #GUI
        check_version = True
        if upload_content is not None:
            dict_plan = load_yaml(upload_content)
            st.info('Using uploaded config file, ignoring URL query parameters')
        elif len(query_plan_dict) > 0:
            dict_plan = query_plan_dict
            check_version = 'version' in dict_plan
            st.info('Using query parameters from URL')
        else:
            dict_plan = {}

        plan = Plan(dict_plan, check_version=False)
        plan.configure()
        plan_download_data = yaml.safe_dump(plan.to_dict())
    elif editor_mode in [EDITOR_MODES[1], EDITOR_MODES[2]]: # Config or None
        if upload_content is None:
            st.error(f' `{editor_mode}` Mode requires a previous plan to be uploaded.')
            st.stop()
        if editor_mode == EDITOR_MODES[1]: # config
            st.warning('`Config` Mode is an advanced mode.  You will see likely unhelpful errors for things like incorrect YAML formatting.')
            plan_content = st.text_area('Configuration File', value=upload_content, height=1000)
        else:
            plan_content = upload_content
        constants_str, data = split_constants(plan_content)
        if constants_str is not None:
            constants = yaml.safe_load(constants_str)
            if st.checkbox('Adjust Configuration File Constants?'):
                constants = configure_constants(constants)
        else:
            constants = {}
        data = Template(data).render(constants)
        plan = Plan(yaml.safe_load(data))
        plan_download_data = plan_content
    elif editor_mode == EDITOR_MODES[3]: # Plan Comparison
        st.markdown(""" ## Plan Comparison Coming Soon!
        
This page will provide the ability to compare multiple forecast config files""")
        st.stop()
    elif editor_mode == EDITOR_MODES[4]: # Documentation
        with open('docs.md', 'r') as fh:
            st.markdown(fh.read())
            st.stop()
    else:
        st.error(f'Unrecognized Editor Mode {editor_mode}')
        st.stop()

    #st.write(plan.to_dict())
    
    st.sidebar.markdown('# Plan Summary')
    st.sidebar.markdown(plan.configuration.summary)
    st.sidebar.write(plan.table_summary)
    st.sidebar.markdown('Save for later:')
    st.sidebar.download_button(
        'Configuration Download (YAML)', 
        data= plan_download_data,
        file_name=f'{datetime.datetime.today().date()}_plan.yaml',
    )
    return plan