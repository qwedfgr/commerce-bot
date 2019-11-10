import os

import dotenv
import requests


def get_token():
    data = {
            'client_id': os.environ["MOLTIN_CLIENT_ID"],
            'client_secret': os.environ["MOLTIN_CLIENT_SECRET"],
            'grant_type': 'client_credentials',
            }

    response = requests.post('https://api.moltin.com/oauth/access_token', data=data)
    if response.ok:
        expires = response.json()['expires']
        token = response.json()['access_token']
    return token


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


def get_item_description(info):
    price = info['meta']['display_price']['with_tax']
    description = (f'{info["name"]}\n'
                   f'{info["description"]}\n'
                   f'{price["amount"]} {price["currency"]} за кг\n'
                   f'{info["meta"]["stock"]["level"]} кг на складе')
    return description


def get_file_by_id(image_id):
    headers = {'Authorization': f'Bearer {get_token()}'}
    response = requests.get(f'https://api.moltin.com/v2/files/{image_id}', headers=headers)
    response.raise_for_status()
    return response.json()['data']['link']['href']


def add_item_to_cart(item_id, quantity):
    dotenv.load_dotenv()
    headers = {
        'Authorization': get_token(),
        'Content-Type': 'application/json',
    }
    data = {"data": {"id": item_id, "type": "cart_item", "quantity": quantity}}
    response = requests.post('https://api.moltin.com/v2/carts/reference/items', headers=headers, data=data)





