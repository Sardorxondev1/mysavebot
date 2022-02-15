import asyncio
import configparser
from datetime import date, datetime
from handlers.users.add_musics import music_st_panel

from aiogram.utils.exceptions import Unauthorized
from handlers.users.registration import register
from typing import Union
from keyboards.inline.apanel_menu import keyboard_apanel, apanel_cd
from keyboards.default.main import main_panel
from aiogram.dispatcher.filters import Text
from sqlalchemy.sql.functions import user
import logging
from aiogram import types
from aiogram.types.message import Message
from aiogram.dispatcher.filters import Command
from aiogram.types import CallbackQuery
from loader import dp, bot
from utils.db_api.commands import check, del_group, search_groups, search_users, set_chat
from utils.db_api.models import User
from filters import IsPrivate
from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton

chat_id_user = 0


@dp.message_handler(IsPrivate(), Command('mm'))
async def start_music(msg: Message):
    await one_panel(msg=msg)


async def one_panel(msg: Union[CallbackQuery, Message], **kwargs):
    markup = await main_panel()
    if not check(msg.from_user.id, User):
        await register(msg)
    if isinstance(msg, Message):
        await msg.answer('Головне меню', reply_markup=markup)
    elif isinstance(msg, CallbackQuery):
        call = msg
        await call.message.edit_reply_markup(markup)


async def control_music(call, **kwargs):
    pass


async def music_list(call, **kwargs):
    pass


@dp.message_handler(IsPrivate(), Text(equals='Вимкнути'), state=['send_msg', None])
async def cancel(msg: Message):
    state = dp.current_state(
        chat=msg.chat.id, user=msg.from_user.id)
    state_now = await state.get_state()
    if state_now == 'send_msg':
        await state.set_state(None)
        await set_chat(msg.from_user.id)
    await one_panel(msg)


@dp.message_handler(IsPrivate(), Text(equals='🎧 Моя музика'))
async def music_change(msg: Message):
    await music_st_panel(msg, name_menu='music', category=None)


@dp.message_handler(IsPrivate(), Text(equals='Мої відео'))
async def sms_change(msg: Message):
    await music_st_panel(msg, name_menu='video', category=None)


async def send_message(call: CallbackQuery, **kwargs):
    state = dp.current_state(
        chat=int(kwargs['chat_id']), user=int(kwargs['user_id']))
    await state.set_state('send_msg')
    await set_chat(user_id=call.from_user.id, chat_id=kwargs['group_id'])
    markup = ReplyKeyboardMarkup(resize_keyboard=True).add('Вимкнути')
    await call.message.answer('Можна писати', reply_markup=markup)


@dp.callback_query_handler(IsPrivate(), apanel_cd.filter())
async def control_music(call: CallbackQuery, callback_data: dict, **kwargs):
    level = callback_data.get('level')
    user_id = callback_data.get('user_id')
    chat_id = callback_data.get('chat_id')
    func = callback_data.get('func')
    group_id = callback_data.get('group_id')
    file_id = callback_data.get('file_id')

    levels = {
        '0': one_panel,
        '1': send_message,
    }
    try:
        current_level = levels[level]
        await current_level(
            call,
            user_id=user_id,
            chat_id=chat_id,
            func=func,
            group_id=group_id,
            file_id=file_id,
        )
    except KeyError as err:
        await bot.answer_callback_query(call.id, text='Неможливо пройти дальше!\nМеню у розробці!')
        logging.error(err)
    print(f'{level} | {user_id} | {chat_id} |{group_id} | {file_id} | {func}')


@dp.message_handler(IsPrivate(), Command('remove'))
async def remove_keyboard(msg: Message):
    text = await msg.reply('Кнопки забрані', reply_markup=ReplyKeyboardRemove())
    await asyncio.sleep(3)
    await text.delete()
    await msg.delete()
