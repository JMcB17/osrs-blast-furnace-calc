from decimal import Decimal
import requests
import requests.compat

API_BASE_URL = 'https://secure.runescape.com/m=itemdb_oldschool/api/'


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

ratios = {
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
item_ids = {
    'Coins': None,
    'Adamantite ore': 449,
    'Coal': 453,
    'Stamina potion(4)': 12625,
}

time_ratio_seconds = 400
base_item = 'Adamantite ore'


def calc_item_quantity(item, quantity):
    return (Decimal(quantity) / Decimal(ratios[base_item])) * ratios[item]


def calc_total_expense(quantity, values):
    total = 0
    for item in ratios:
        item_quantity = calc_item_quantity(item, quantity)
        item_expense = item_quantity * values[item]
        total += item_expense

    return total


def main():
    coins_available = rs_notation_to_int(input('Coins in: '))

    print('Getting api last updated time')
    api_info = requests.get(requests.compat.urljoin(API_BASE_URL, 'info.json')).json()
    last_update_runeday = api_info['lastConfigUpdateRuneday']
    print(f'api last updated runescape day {last_update_runeday}')

    # values = {i: get_item_value(i, categories[i]) for i in categories}
    print('Getting item values from api')
    values = {i: get_item_value_by_id(item_ids[i]) for i in item_ids}

    quantity = inv_space
    while True:
        if (calc_total_expense(quantity, values)) >= coins_available:
            quantity -= inv_space
            break
        quantity += inv_space

    total_expense = calc_total_expense(quantity, values)
    print(f'Total expense: {total_expense}')
    for item in ratios:
        print(f'Quantity of {item}: {calc_item_quantity(item, quantity)}')


if __name__ == '__main__':
    main()
