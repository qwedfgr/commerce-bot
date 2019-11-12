import os

import requests


def get_token():
    data = {
            'client_id': os.environ["MOLTIN_CLIENT_ID"],
            'client_secret': os.environ["MOLTIN_CLIENT_SECRET"],
            'grant_type': 'client_credentials',
            }

    response = requests.post('https://api.moltin.com/oauth/access_token', data=data)
    if response.ok:
        token = response.json()['access_token']
    return token if response.ok else None


def get_items(item_id=None):
    params = None
    headers = {'Authorization': f'Bearer {get_token()}'}
    if item_id:
        params = {'id': item_id, }
    response = requests.get('https://api.moltin.com/v2/products', headers=headers, params=params)
    if response.ok:
        return response.json()['data']
    else:
        return None


def get_item_description(info, is_cart=False):
    price = info['meta']['display_price']['with_tax']
    description = (f'{info["name"]}\n'
                   f'{info["description"]}\n')
    if is_cart:
        description += (f'{price["unit"]["formatted"]} за кг\n'
                        f'Всего в корзине: {price["value"]["formatted"]}\n\n')
    else:
        description += (f'{price["amount"]} {price["currency"]} за кг\n'
                        f'{info["meta"]["stock"]["level"]} кг на складе\n')
    return description


def get_file_by_id(image_id):
    headers = {'Authorization': f'Bearer {get_token()}'}
    response = requests.get(f'https://api.moltin.com/v2/files/{image_id}', headers=headers)
    response.raise_for_status()
    return response.json()['data']['link']['href']


def add_item_to_cart(chat_id, item_id, quantity):
    headers = {
        'Authorization': get_token(),
        'Content-Type': 'application/json',
    }
    data = {'data': {'id': item_id, 'type': 'cart_item', 'quantity': int(quantity)}}
    response = requests.post(f'https://api.moltin.com/v2/carts/:{chat_id}/items', headers=headers, json=data)


def get_cart(chat_id):
    headers = {
        'Authorization': get_token(),
        'Content-Type': 'application/json',
    }
    response = requests.get(f'https://api.moltin.com/v2/carts/:{chat_id}/items', headers=headers)
    response.raise_for_status()
    items = response.json()['data']
    cart = ''
    buttons = []
    if not items:
        return 'Корзина пуста', buttons
    for item in items:
        cart += get_item_description(item, True)
        buttons.append([f'Убрать из корзины {item["name"]}', item['id']])
    total = response.json()['meta']['display_price']['with_tax']['formatted']
    cart += f'Всего: {total}'
    return cart, buttons


def delete_item_from_cart(chat_id, item_id):
    headers = {
        'Authorization': get_token(),
        'Content-Type': 'application/json',
    }
    response = requests.delete(f'https://api.moltin.com/v2/carts/:{chat_id}/items/{item_id}', headers=headers)
    response.raise_for_status()


