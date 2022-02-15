import logging
from aiogram.types.inline_keyboard import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData
from aiogram.utils.exceptions import Unauthorized
from utils.db_api.commands import del_group, search_groups
from loader import dp


apanel_cd = CallbackData('apanel', 'level', 'func',
                        'user_id', 'chat_id', 'group_id', 'file_id')


def make_callback_data(level='0', func='0', user_id='0', chat_id='0', group_id='0', file_id='0'):
    return apanel_cd.new(level=level, func=func, user_id=user_id, chat_id=chat_id, group_id=group_id, file_id=file_id)


async def keyboard_apanel(data: dict):
    LEVEL = 0
    groups = await search_groups()
    user_id = data['user_id']
    chat_id = data['chat_id']
    markup = InlineKeyboardMarkup(row_width=3)
    for group in groups:
        try:
            search = await dp.bot.get_chat(chat_id=group.get['chat_id'])
            text = search['title']
            group_id = search['id']
            callback = make_callback_data(
                level=LEVEL + 1, user_id=user_id, chat_id=chat_id, group_id=group_id, func='send_msg')
            markup.insert(InlineKeyboardButton(
                text='@'+text, callback_data=callback))
        except Unauthorized:
            logging.error(f'З группи {group.get["chat_id"]} вигнано бота, видаляємо з бази даних группу.')
            await del_group(group.get['chat_id'])

    return markup


    