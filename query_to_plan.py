""" Convert URL query to plan """

from urllib.parse import quote

def query_to_plan(params: dict) -> dict:
    saved_plan = {}
    for key in params:
        table, field_name = key.split('__')
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
