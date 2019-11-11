import logging
import os

import dotenv
import redis
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackQueryHandler, CommandHandler, MessageHandler
from telegram.ext import Filters, Updater

import moltin

_database = None


def start(bot, update):
    items = moltin.get_items()
    items_buttons = [InlineKeyboardButton(item['name'], callback_data=item['id']) for item in items]
    keyboard = [items_buttons, [InlineKeyboardButton('Корзина', callback_data='cart')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    chat_id, user_reply = get_chat_id_and_reply(update)
    bot.send_message(chat_id=chat_id, text='Выберите товар', reply_markup=reply_markup)
    return "HANDLE_MENU"


def handle_menu(bot, update):
    item_id = update.callback_query.data
    item_info = moltin.get_items(item_id=item_id)[0]
    description = moltin.get_item_description(item_info)

    message = update.callback_query.message

    quantities = [1, 5, 10]
    quantities_buttons = [InlineKeyboardButton(f'{q} кг', callback_data=f'{item_id} {q}') for q in quantities]
    keyboard = [
        quantities_buttons,
        [InlineKeyboardButton('Назад', callback_data='menu')],
        [InlineKeyboardButton('Корзина', callback_data='cart')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    image_id = item_info['relationships']['main_image']['data']['id']
    file_url = moltin.get_file_by_id(image_id)
    bot.delete_message(chat_id=message.chat_id, message_id=message.message_id)

    bot.send_photo(chat_id=message.chat_id, photo=file_url, caption=description, reply_markup=reply_markup)

    return 'HANDLE_DESCRIPTION'


def handle_description(bot, update):
    chat_id, data = get_chat_id_and_reply(update)
    if data == 'menu':
        return start(bot, update)
    elif data == 'cart':
        handle_cart(bot, update)
    else:
        moltin.add_item_to_cart(chat_id, *data.split())
        return 'HANDLE_DESCRIPTION'


def handle_cart(bot, update):
    chat_id, user_reply = get_chat_id_and_reply(update)
    cart = moltin.get_cart(chat_id)
    print(cart)

def handle_users_reply(bot, update):
    db = get_database_connection()

    chat_id, user_reply = get_chat_id_and_reply(update)

    if user_reply == '/start':
        user_state = 'START'
    else:
        user_state = db.get(chat_id)
    states_functions = {
        'START': start,
        'HANDLE_MENU': handle_menu,
        'HANDLE_DESCRIPTION': handle_description,
        'HANDLE_CART': handle_cart
    }
    state_handler = states_functions[user_state]

    try:
        next_state = state_handler(bot, update)
        db.set(chat_id, next_state)
    except Exception as err:
        print(err)


def get_chat_id_and_reply(update):
    if update.message:
        user_reply = update.message.text
        chat_id = update.message.chat_id
    elif update.callback_query:
        user_reply = update.callback_query.data
        chat_id = update.callback_query.message.chat_id
    else:
        return
    return chat_id, user_reply


def get_database_connection():
    global _database
    if _database is None:
        _database = redis.Redis(host=os.environ['HOST'],
                                password=os.environ['PASSWORD_REDIS'],
                                port=os.environ['PORT'],
                                decode_responses=True, db=0
                                )
    return _database


def main():
    dotenv.load_dotenv()
    token = os.getenv("TOKEN_TG")
    updater = Updater(token)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CallbackQueryHandler(handle_users_reply))
    dispatcher.add_handler(MessageHandler(Filters.text, handle_users_reply))
    dispatcher.add_handler(CommandHandler('start', handle_users_reply))
    updater.start_polling()


if __name__ == '__main__':
    main()
