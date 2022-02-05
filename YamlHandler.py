""" Handle the configuration file """

import yaml
from jinja2 import Template

from common import f2d

TOP_KEYS = [
    'accounts',
    'incomes',
    'expenses',
    'transfers',
    'assets',
    'liabilities',
    'mortgages',
]
NEXT_KEYS = [
    'starting_balance',
    '$balance',
    'amount',
    'extra_principal',
]

def dump_yaml(data: dict) -> str:
    for key in TOP_KEYS:        
        for i, item in enumerate(data[key]):
            for next_key in NEXT_KEYS:
                try:
                    data[key][i][next_key] = float(item[next_key])
                except KeyError:
                    pass # Not a field that needs to be converted
    return yaml.safe_dump(data)

def split_constants(data: str) -> tuple:
    result = data.split('\n---\n')
    part_quantity = len(result)
    assert(part_quantity <= 2), 'More than one instance of --- in configuration data'
    if part_quantity == 1:
        return None, data
    elif part_quantity == 2:
        return result[0], result[1]

def load_yaml(upload_content: str) -> dict:
    constants, data = split_constants(upload_content)
    if constants is not None:
        data = Template(data).render(yaml.safe_load(constants))
    return yaml.safe_load(data) 

def configuration_update(config: dict) -> dict:
    config['$default_inflation'] = config.get('default_inflation', 2.0)/100.0
    return config

def clean(data: dict):
    for key in data:
        if type(data[key]) == list:
            for item in data[key]:
                item = _clean(item)
        elif type(data[key]) == dict:
            data[key] = _clean(data[key])
    return data

def _clean(data: dict) -> dict:
    remove_keys = [key for key in data if key[0] == '$']
    for key in remove_keys:
        data.pop(key)        
    return data

