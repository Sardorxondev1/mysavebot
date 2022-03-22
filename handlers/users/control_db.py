import asyncio

from aiogram.dispatcher.filters.builtin import Command, Text
from aiogram.types.message import Message

from loader import dp, config, id_owner
from utils.db_api.commands import makeadmin, search_users, get_with_db, del_with_db


@dp.message_handler(Command('id'))
async def give_id(msg: Message):
    await msg.answer(f'Твій ID: <code>{msg.from_user.id}</code>')


@dp.message_handler(Command('admin'))
async def add_admin(msg: Message):
    pass


@dp.message_handler(Command('get'))
async def db_request(msg: Message):
    try:
        if int(msg.from_user.id) == int(id_owner):
            text = msg.get_args().split('-')
            where = None
            try:
                text[1].split('=')[0]
                text[1].split('=')[1]
                where = text[1].split('=')
            except:
                pass
            index = None
            try:
                index = text[2]
            except:
                try:
                    index = text[1]
                except:
                    pass
            text = await get_with_db(table_name=text[0], filter_dt=where)
            for tx in text:
                if index:
                    await msg.answer(tx[index])
                else:
                    await msg.answer(tx)
                
            if len(text) > 5:
                await asyncio.sleep(0.3)
            elif len(text) > 10:
                await asyncio.sleep(0.5)
    except IndexError:
        await msg.answer(f'[ERROR] Не найдено в базі данних!')
        
        
@dp.message_handler(Command('del'))
async def delete_item(msg: Message):
    if int(msg.from_user.id) == int(id_owner):
        text = msg.get_args().split('-')
        where = None
        try:
            where = text[1].split('=')
        except:
            pass
        result = await del_with_db(table_name=text[0], filter_dt=where)
        if result == True:
            await msg.answer('Успішно видалено!')
        else:
            await msg.answer(result)
    
            
        
