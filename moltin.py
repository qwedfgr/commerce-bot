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

    response = requests.get('https://api.moltin.com/v2/products', headers=headers, params=params )
    if response.ok:
        return response.json()
    else:
        return None


def main():
    dotenv.load_dotenv()

    print(get_token())
    headers = {
        'Authorization': get_token(),
        'Content-Type': 'application/json',
    }

    data = '{"data": {"id": "397e3ce8-55b8-4999-87e1-1127fb324704","type": "cart_item","quantity": 1}}'

    response = requests.post('https://api.moltin.com/v2/carts/reference/items', headers=headers, data=data)
    print(response)
    print(response.content)
    response = requests.get('https://api.moltin.com/v2/carts/:reference', headers=headers)

    print(response)
    print(response.content)
    print(get_items())


if __name__ == '__main__':
    main()



