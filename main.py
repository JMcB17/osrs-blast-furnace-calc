#!/usr/bin/env python

import math
import decimal
import time
import argparse

import requests
import requests.compat


# todo: calculate profit
# todo: print values got from api
# todo: crazy idea - download and parse wiki pages in the money making category to get item lists
# the biggest obstacle apart from a lot of work would probably be figuring out base_item
__version__ = '0.1.2'

API_BASE_URL = 'https://secure.runescape.com/m=itemdb_oldschool/api/'


parser = argparse.ArgumentParser()
parser.add_argument('coins_available', nargs='?')


def get_item_value_by_name(item_name, category=1):
    if category is None:
        return 1

    item_name = item_name.capitalize()

    url = requests.compat.urljoin(API_BASE_URL, 'catalogue/items.json')
    params = {
        'category': category,
        'alpha': item_name[0].lower(),
    }
    response = requests.get(url, params=params)
    items = response.json()['items']

    for item in items:
        if item['name'] == item_name:
            return item['current']['price']

    return None


def rs_notation_to_int(value_str):
    multipliers = {
        'k': 10**3,
        'm': 10**6,
        'b': 10**9,
    }

    value_str = value_str.replace(',', '')

    for multi in multipliers:
        if value_str.endswith(multi):
            value_str = value_str.rstrip(multi)
            value = int(value_str) * multipliers[multi]
            break
    else:
        value = int(value_str)

    return value


def get_item_value_by_id(item_id):
    if item_id is None:
        return 1

    url = requests.compat.urljoin(API_BASE_URL, 'catalogue/detail.json')
    params = {
        'item': item_id
    }
    response = requests.get(url, params=params)
    item = response.json()['item']
    value = item['current']['price']
    if type(value) == str:
        value = rs_notation_to_int(value)

    return value


inv_space = 27

item_ratios = {
    'Coins': 8000,
    'Adamantite ore': 300,
    'Coal': 900,
    'Stamina potion(4)': 1,
}
# categories = {
#     'Coins': None,
#     'Adamantite ore': 25,
#     'Coal': 25,
#     'Stamina potion(4)': 26,
# }
# categories = {
#     'Coins': None,
#     'Adamantite ore': 1,
#     'Coal': 1,
#     'Stamina potion(4)': 1,
# }

# https://www.reddit.com/r/2007scape/comments/3g06rq/guide_using_the_old_school_ge_page_api/
# https://pastebin.com/LhxJ7GRG
item_ids = {
    'Coins': None,
    'Adamantite ore': 449,
    'Coal': 453,
    'Stamina potion(4)': 12625,
    'Adamantite bar': 2361,
}

time_ratio_seconds = 400
base_item = 'Adamantite ore'
product_item = 'Adamantite bar'


def calc_item_quantity(item_ratio, quantity):
    quantity = decimal.Decimal(quantity)
    base_item_ratio = decimal.Decimal(item_ratios[base_item])

    item_quantity = (quantity / base_item_ratio) * item_ratio
    item_quantity = math.ceil(item_quantity)
    return item_quantity


def calc_total_expense(quantity, values):
    total = 0
    for item in item_ratios:
        item_quantity = calc_item_quantity(item_ratios[item], quantity)
        item_expense = item_quantity * values[item]
        total += item_expense

    return total


def get_quantity(coins_available, values):
    quantity = inv_space
    while True:
        if (calc_total_expense(quantity, values)) >= coins_available:
            quantity -= inv_space
            break
        quantity += inv_space

    return quantity


def main(coins_available=None):
    if coins_available is not None:
        print(f'Coins in: {coins_available}')
    else:
        args = parser.parse_args()
        if args.coins_available is not None:
            coins_available = args.coins_available
            print(f'Coins in: {coins_available}')
        else:
            coins_available = input('Coins in: ')
    if type(coins_available) == str:
        coins_available = rs_notation_to_int(coins_available)

    while True:
        print('\nGetting api last updated time')
        api_info = requests.get(requests.compat.urljoin(API_BASE_URL, 'info.json')).json()
        last_update_runeday = api_info['lastConfigUpdateRuneday']
        print(f'API last updated runescape day {last_update_runeday}')

        # values = {i: get_item_value(i, categories[i]) for i in categories}
        print('Getting item values from api\n')
        item_values = {i: get_item_value_by_id(item_ids[i]) for i in item_ids}

        quantity = get_quantity(coins_available, item_values)
        base_item_quantity = calc_item_quantity(item_ratios[base_item], quantity)
        product_gross = base_item_quantity * item_values[product_item]
        total_expense = calc_total_expense(quantity, item_values)
        profit = product_gross - total_expense

        time_seconds = calc_item_quantity(time_ratio_seconds, quantity)
        time_string = time.strftime('%H:%M', time.gmtime(time_seconds))
        profit_per_hour = int(decimal.Decimal(profit) / (decimal.Decimal(time_seconds) / decimal.Decimal(60**2)))

        print(
            '---Results---\n'
            f'Total expense: {total_expense}\n'
            f'Total gross: {product_gross}\n'
            f'Total profit: {profit}\n'
            f'Time to use up items: {time_seconds}s, {time_string}h\n'
            f'Profit per hour: {profit_per_hour}\n'
        )
        for item in item_ratios:
            print(f'Quantity of {item}: {calc_item_quantity(item_ratios[item], quantity)}')

        coins_available = product_gross
        if input('\nEnter to continue, Q then Enter to quit\n').lower() == 'q':
            break


if __name__ == '__main__':
    main()
