#!/usr/bin/env python3

def obj_to_tuple(obj: dict) -> dict:
    """ Parse JSON object and format it for insert_data method

    Parameters:
        obj (dict): The JSON object that should be formatted

    Returns:
        dict: JSON object with keys and values formatted for insert_data method """

    keys = ''
    values = ''
    for key, value in obj.items():
        keys = f'{keys},{key}' if keys != '' else key
        values = f'{values}, :{key}' if values != '' else f':{key}'

    return {"keys": keys, "values": values}


def obj_to_string(update_config: dict) -> str:
    update_string = ''
    index = 0
    for key, value in update_config.items():
        update_string = update_string + f"{key}='{value}'," if index < len(
            update_config) - 1 else update_string + f"{key}='{value}'"
        index = index + 1

    return update_string
