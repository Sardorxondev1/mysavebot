from handlers.users.add_function import add_func, add_video


from handlers.users.control_music import music_st_panel
from handlers.users.registration import register
from typing import Union
from keyboards.default.main import main_panel
from aiogram.dispatcher.filters import Text
from aiogram.types.message import Message
from aiogram.dispatcher.filters import Command
from aiogram.types import CallbackQuery
from loader import dp, config
from utils.db_api.commands import check
from utils.db_api.models import User
from filters import IsPrivate

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


@dp.message_handler(IsPrivate(), Text(equals='🎧 Моя музика'))
async def music_change(msg: Message):
    await music_st_panel(msg, name_menu='music', category=None)


@dp.message_handler(IsPrivate(), Text(equals='🎞 Мої відео'))
async def sms_change(msg: Message):
    await music_st_panel(msg, name_menu='video', category=None)
    
    
@dp.message_handler(IsPrivate(), Text(equals='➕ Додати музику'))
async def music_add(msg: Message):
    await add_func(msg)
    
    
@dp.message_handler(IsPrivate(), Text(equals='➕ Додати відео'))
async def video_add(msg: Message):
    await add_video(msg)


@dp.message_handler(IsPrivate(), Command('page'))
async def change_page_on(msg: Message):
    config.read('data/config.ini')
    if int(config['DEFAULT']['id_owner_bot']) == int(msg.from_user.id):
        count = msg.get_args().split(' ')[0]
        text = ''
        try:
            config.read('data/config.ini')
            count = int(count)
            old_count = config['MUSIC_SETTINGS']['counts']
            config['MUSIC_SETTINGS']['counts'] = str(count)
            text =  f'Кількість пісень на сторінці змінено на {count} з {old_count}'
            with open('data/config.ini', 'w') as fileconfig:
                config.write(fileconfig)
        except Exception as err:
            text = 'Не вийшло'
            print(err)
        await msg.answer(text)