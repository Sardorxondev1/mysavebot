from utils.db_api.commands import search_max_page, search_musics, search_videos
from aiogram.types.inline_keyboard import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.callback_data import CallbackData
from loader import config

music_ad_cd = CallbackData('music_panel', 'action', 'user_id', 'id_code')


def make_callback(action='0', user_id='0', id_code='0'):
    return music_ad_cd.new(action=action, user_id=user_id, id_code=id_code)


async def music_add_panel(user_id, id_code):
    markup = InlineKeyboardMarkup(row_width=1)
    markup.insert(InlineKeyboardButton(text='🗃 Сховати', callback_data=make_callback(action='hide_music', user_id=user_id, id_code=id_code)))
    markup.insert(InlineKeyboardButton(text='🗑 Видалити', callback_data=make_callback(action='delete_music', user_id=user_id, id_code=id_code)))
    return markup