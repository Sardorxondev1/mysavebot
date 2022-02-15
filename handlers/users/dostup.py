from aiogram.types.callback_query import CallbackQuery
from keyboards.inline.users import all_users, user_cd
from loader import dp
from filters import IsPrivate
from aiogram.types import Message
from aiogram.dispatcher.filters import Command


@dp.message_handler(IsPrivate(), Command('makeadmin'))
async def admin_panel(msg: Message):
    func = 0
    if msg.get_args == '1':
        markup = await all_users(action=1)
        btn = await msg.reply('Виберіть користувача', reply_markup=markup)
    elif msg.get_args == '0':
        markup = await all_users(action=0)
        btn = await msg.reply('Виберіть користувача', reply_markup=markup)
    else:
        pass
    
    
    
async def change_user(call: CallbackQuery, **kwargs):
    user_id = kwargs['user_id']
    
    
    
@dp.callback_query_handler(IsPrivate(), user_cd.filter())
async def control_user(call: CallbackQuery, callback_data: dict):
    user_id = callback_data.get('user_id')
    