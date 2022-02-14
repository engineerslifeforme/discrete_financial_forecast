""" Convert URL query to plan """

from urllib.parse import quote
import zlib
import binascii
import base64

import yaml

KEYMAP = {
    'accounts': 0,
    'enforce_minimum_balance': 1,
    'interest_profile': 2,
    'minimum_balance': 3,
    'name': 4,
    'priority': 5,
    'starting_balance': 6,
    'assets': 7,
    'configuration': 8,
    'duration': 9,
    'start_month': 10,
    'start_year': 11,
    'expenses': 12,
    'amount': 13,
    'frequency': 14,
    'milestone_end': 15,
    'source_account': 16,
    'milestone_start': 17,
    'incomes': 18,
    'destination_account': 19,
    'interest_profiles': 20,
    'profile_phases': 21,
    'phase_type': 22,
    'rate': 23,
    'profile_type': 24,
    'liabilities': 25,
    'milestones': 26,
    'date': 27,
    'mortgages': 28,
    'extra_principal': 29,
    'length': 30,
    'liability': 31,
    'transfers': 32,
    'version': 33,
}

def query_to_plan(params: dict) -> dict:
    saved_plan = {}
    if 'compressed' in params:
        saved_plan = compressed_str_to_plan(params['compressed'][0])
    else:
        for key in params:
            try:
                table, field_name = key.split('__')
            except ValueError:
                continue
            if table == 'configuration':
                if table not in saved_plan:
                    saved_plan[table] = {field_name: convert_value(params[key][0])}
                else:
                    saved_plan[table][field_name] = convert_value(params[key][0])
            else:
                if table not in saved_plan:
                    saved_plan[table]= []
                for i, item in enumerate(params[key]):
                    try:
                        saved_plan[table][i][field_name] = convert_value(item)
                    except IndexError:
                        saved_plan[table].append({field_name: convert_value(item)})

        try:
            new_list = []
            for profile in saved_plan['interest_profiles']:
                item = {}
                if 'name' in profile:
                    item['name'] = profile['name']
                if 'profile_type' in profile:
                    item['profile_type'] = profile['profile_type']
                if 'rate' in profile:
                    item['profile_phases'] = [{'rate': float(profile['rate'])}]
                    if 'profile_type' in profile:
                        item['profile_phases'][0]['phase_type'] = profile['profile_type']
                new_list.append(item)
            saved_plan['interest_profiles'] = new_list
        except KeyError:
            pass # No interest profiles provided

    return saved_plan

def convert_value(value: str):
    if value.isnumeric() and '.' in value:
        return float(value)
    elif value.isnumeric():
        return int(value)
    else:
        return value

def plan_to_query(plan_dict: dict) -> str:
    params = []
    for table in plan_dict:
        if table == 'configuration':
            for key in plan_dict[table]:
                params.append(f'{table}__{key}={quote(str(plan_dict[table][key]))}')
        elif table == 'version':
            pass # don't need version
        else:
            for item in plan_dict[table]:
                for key in item:
                    if key == 'profile_phases':
                        params.append(f"{table}__rate={quote(str(item[key][0]['rate']))}")
                    else:
                        try:
                            params.append(f'{table}__{key}={quote(str(item[key]))}')
                        except:
                            import pdb;pdb.set_trace()
    return '?'+'&'.join(params)

def plan_to_compressed_str(plan) -> str:
    plan_dict = plan.to_dict()
    smaller = replace_keys(plan_dict)
    plan_str = yaml.dump(smaller).encode()
    compressed = zlib.compress(plan_str)
    return '?compressed='+base64.urlsafe_b64encode(compressed).decode()

def replace_keys(dictionary: dict, reverse:bool =False) -> dict:
    new_dict = {}
    if reverse:
        key_map = {v: k for k, v in KEYMAP.items()}
    else:
        key_map = KEYMAP
    for key in dictionary:
        thing = dictionary[key]
        newid = key_map[key]
        new_dict[newid] = thing
        if type(thing) == list:
            new_list = []
            for item in thing:
                fixed_item = replace_keys(item, reverse=reverse)
                new_list.append(fixed_item)
            new_dict[newid] = new_list
        elif type(thing) == dict:
            new_dict[newid] = replace_keys(thing, reverse=reverse)
    return new_dict

def compressed_str_to_plan(compressed_str: str) -> dict:
    raw_dict = zlib.decompress(base64.urlsafe_b64decode(compressed_str.encode()))
    return replace_keys(yaml.safe_load(raw_dict), reverse=True)

