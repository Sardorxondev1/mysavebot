import asyncio
import logging
from utils.db_api.models import User

import aiogram
from utils.db_api.commands import del_acc, search_groups, search_users
from aiogram import Dispatcher
from loader import dp, config


async def on_startup_notify(dp: Dispatcher):
    config.read('data/config.ini')
    id_owner = int(config['DEFAULT']['ID_OWNER_BOT'])
    await dp.bot.send_message(chat_id=id_owner, text='<code>Бота запущенно</code>', disable_notification=True)
    await dp.bot.send_message(chat_id=id_owner, text='<code>Провірка аккаунтів...</code>', disable_notification=True)
    await check_accounts()
    await asyncio.sleep(2)
    await check_music()
    await dp.bot.send_message(chat_id=id_owner, text='<code>Провірка музики..</code>', disable_notification=True)
    await asyncio.sleep(2)
    await check_groups()
    await dp.bot.send_message(chat_id=id_owner, text='<code>Провірка групп...</code>', disable_notification=True)
    await dp.bot.send_message(chat_id=id_owner, text=await stats(), disable_notification=True)

stat_checks = {}


async def check_accounts():
    users = await search_users()
    count = 0
    list_count = []
    for user in users:
        try:
            msg = await dp.bot.send_message(chat_id=user.get['user_id'], text='check your account..', disable_notification=True)
            await msg.delete()
            count += 1
        except aiogram.utils.exceptions.BotBlocked:
            await del_acc(User, user.get['user_id'])
            list_count.append(user.get['user_id'])

    stat_checks['accounts'] = f'Аккаунти: {count}\nПокинули чат: {len(list_count)}'


async def check_groups():
    count = 0
    list_count = 0
    groups = await search_groups()
    stat_checks['groups'] = f'Пропущенно'


async def check_music():
    stat_checks['musics'] = f'Пропущенно'


async def stats():
    accounts = stat_checks['accounts']
    musics = stat_checks['musics']
    groups = stat_checks['groups']
    return f'<b>Статистика</b>\n\nПровірка аккаунтів:\n{accounts}\n\nПровірка музики:\n{musics}\n\nПровірка групп:\n{groups}\n\n'