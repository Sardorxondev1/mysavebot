from aiogram.dispatcher.filters import Command
from aiogram.types import Message

from filters import IsPrivate
from utils.db_api.commands import register_user
from loader import dp


@dp.message_handler(Command('reg'))
async def register(msg: Message):
    '''
            User registration function 
    '''
    # Беремо дані користувача з телеграму
    first_name = msg.from_user.first_name
    last_name = msg.from_user.last_name
    fullname = ''
    # Формуємо повне імя і фамілію, якщо є
    if first_name:
        fullname = first_name
        if last_name:
            fullname = fullname + ' ' + last_name
    else:
        fullname = 'Not found!'
    # Збираємо усі дані в словник
    data = {
        'user_id': msg.from_user.id,
        'chat_id': msg.chat.id,
        'username': msg.from_user.username,
        'fullname': fullname,
    }
    # Реєструємо користувача, і одразу відправляємо повідомлення через return
    user_reg = await register_user(data)
    if user_reg:
        await msg.answer(user_reg)
    else:
        await msg.answer('Невідома помилка')