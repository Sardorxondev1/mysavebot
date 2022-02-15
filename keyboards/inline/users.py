from aiogram.types.inline_keyboard import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.callback_data import CallbackData
from utils.db_api.commands import search_users

user_cd = CallbackData('users', 'user_id', 'func')


def callback(user_id='0', func='0'):
    return user_cd.new(user_id=user_id, func=func)


async def all_users(action):
    users = await search_users()
    markup = InlineKeyboardMarkup(row_width=2)
    for us in users:
        user_id = us.get['user_id']
        username = us.get['username']
        markup.insert(InlineKeyboardButton(text=f'@{username}', callback_data=callback(user_id)))
    return markup