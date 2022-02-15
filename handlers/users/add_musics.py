import asyncio
from typing import Union
from aiogram.types.callback_query import CallbackQuery
from keyboards.inline.music_panel import musics_keyboard, musics_cd
import logging
from utils.db_api.commands import add, control_music, search_musics, control_video, search_videos
from aiogram import types
from aiogram.dispatcher.filters.builtin import Command, Text
from aiogram.dispatcher.storage import FSMContext
from aiogram.types.reply_keyboard import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from loader import dp
from aiogram.types.message import Message
from filters import IsPrivate
from states.music_add import Music, Video
from loader import config


@dp.message_handler(IsPrivate(), Command('get'))
async def get_musics(msg: Message):
    args = msg.get_args().split(' ')
    name_menu = args[0]
    category = None
    if len(args) == 2:
        category = args[1]
    await music_st_panel(msg, name_menu=name_menu, category=category)


async def music_st_panel(msg: Union[Message, CallbackQuery], **kwargs):
    name_menu = kwargs['name_menu']
    category = kwargs['category']
    markup = await musics_keyboard(msg.from_user.id, name_menu=name_menu, category=category)
    if isinstance(msg, Message):
        await msg.answer('M E N U', reply_markup=markup)
    elif isinstance(msg, CallbackQuery):
        call = msg
        await call.message.edit_reply_markup(markup)


async def music_show(call: CallbackQuery, **kwargs):
    user_id = kwargs['user_id']
    id_code = kwargs['id_code']
    musics = await search_musics(user_id=user_id, file_unique_id=id_code)
    file_id = musics.get['file_id']
    await call.message.answer_audio(file_id)
    
    
async def video_show(call: CallbackQuery, **kwargs):
    user_id = kwargs['user_id']
    id_code = kwargs['id_code']
    video = await search_videos(user_id=user_id, file_unique_id=id_code)
    file_id = video.get['file_id']
    await call.message.answer_video(file_id)


async def navigate_button(call: CallbackQuery, **kwargs):
    config.read('data/config.ini')
    counts = int(config['MUSIC_SETTINGS']['counts'])
    action = kwargs['func']
    from_page = kwargs['from_page']
    pages = int(kwargs['pages'])
    page = int(kwargs['page'])
    p_min = int(from_page.split(',')[0])
    p_max = int(from_page.split(',')[1])
    name_menu = kwargs['name_menu']
    if action == 'next':
        if not page >= pages:
            await dp.bot.answer_callback_query(call.id, text='Загружаємо..')
            await asyncio.sleep(0.3)
            p_min += counts
            p_max += counts
            page += 1
            markup = await musics_keyboard(call.from_user.id, page, p_max, p_min, name_menu=name_menu)
            await call.message.edit_reply_markup(markup)
        else:
            await dp.bot.answer_callback_query(call.id, text='Це остання сторінка!')
    elif action == 'back':
        if not page == pages:
            await dp.bot.answer_callback_query(call.id, text='Загружаємо..')
            await asyncio.sleep(0.3)
            p_min -= counts
            p_max -= counts
            page -= 1
            markup = await musics_keyboard(call.from_user.id, page, p_max, p_min, name_menu=name_menu)
            await call.message.edit_reply_markup(markup)
        else:
            await dp.bot.answer_callback_query(call.id, text='Це перша сторінка!')


async def update_page(call: CallbackQuery, **kwargs):
    user_id = kwargs['user_id']
    page = kwargs['page']
    from_page = kwargs['from_page'].split(',')
    from_page_min = from_page[0]
    from_page_max = from_page[1]
    name_menu = kwargs['name_menu']
    markup = await musics_keyboard(call.from_user.id, page, from_page_max, from_page_min, name_menu)
    await dp.bot.answer_callback_query(call.id, 'Сторінку оновленно!')
    await call.message.edit_reply_markup(markup)

async def func_pass(call: CallbackQuery, **kwargs):
    pass


@dp.callback_query_handler(IsPrivate(), musics_cd.filter())
async def control_all_musics(call: CallbackQuery, callback_data: dict):
    action = callback_data.get('action')
    func = callback_data.get('func')
    user_id = callback_data.get('user_id')
    id_code = callback_data.get('id_code')
    pages = callback_data.get('pages')
    page = callback_data.get('page')
    from_page = callback_data.get('from_page')
    name_menu = callback_data.get('name_menu')

    actions = {
        '0': func_pass,
        'music': music_show,
        'video': video_show,
        'update_page': update_page,
        'navigate': navigate_button,
    }
    await asyncio.sleep(0.3)
    current_action = actions[action]
    await current_action(
        call,
        action=action,
        func=func,
        user_id=user_id,
        id_code=id_code,
        pages=pages,
        page=page,
        from_page=from_page,
        name_menu=name_menu,
    )
    print(f'ACTION: {action} | FUNC: {func} | USER_ID: {user_id} | ID_CODE: {id_code} | PAGES: {pages} | PAGE: {page} | FROM_PAGE: {from_page} | NAME_MENU: {name_menu}')


@dp.message_handler(IsPrivate(), Command('add_music'))
async def add_func(msg: Message):
    await Music.audio.set()
    await msg.answer('Надішліть пісню')


# You can use state '*' if you need to handle all states
@dp.message_handler(state='*', commands='cancel')
@dp.message_handler(Text(equals='cancel', ignore_case=True), state='*')
async def cancel_handler(message: types.Message, state: FSMContext):
    """
    Allow user to cancel any action
    """
    current_state = await state.get_state()
    if current_state is None:
        return

    logging.info('Cancelling state %r', current_state)
    # Cancel state and inform user about it
    await state.finish()
    # And remove keyboard (just in case)
    await message.reply('Скасовано.', reply_markup=types.ReplyKeyboardRemove())


@dp.message_handler(IsPrivate(), state=Music.audio, content_types=types.ContentTypes.AUDIO)
async def music_in_data(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        name = f'{msg.audio.performer} - {msg.audio.title}'
        file_id = msg.audio.file_id
        file_unique_id = msg.audio.file_unique_id
        data['function'] = 'add'
        data['user_id'] = msg.from_user.id
        data['name_music'] = name
        data['file_id'] = file_id
        data['file_unique_id'] = file_unique_id
        await msg.reply('Напишіть назву')
        await Music.next()


@dp.message_handler(IsPrivate(), state=Music.name)
async def name_music_state(msg: types.Message, state=FSMContext):
    async with state.proxy() as data:
        data['name_music'] = msg.text
        await msg.reply('Напишіть категорію')
        await Music.next()


@dp.message_handler(IsPrivate(), state=Music.category)
async def process_name_music(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        category = msg.text
        data['category'] = category
        print(data)
        if await control_music(data):
            await msg.answer(f'Успішно добавленно пісню')
        await state.finish()


@dp.message_handler(IsPrivate(), Command('add_video'))
async def add_video(msg: Message):
    await Video.video.set()
    await msg.answer('Надішліть відео')


# You can use state '*' if you need to handle all states
@dp.message_handler(state='*', commands='cancel')
@dp.message_handler(Text(equals='cancel', ignore_case=True), state='*')
async def cancel_handler(message: types.Message, state: FSMContext):
    """
    Allow user to cancel any action
    """
    current_state = await state.get_state()
    if current_state is None:
        return

    logging.info('Cancelling state %r', current_state)
    # Cancel state and inform user about it
    await state.finish()
    # And remove keyboard (just in case)
    await message.reply('Скасовано.', reply_markup=types.ReplyKeyboardRemove())


@dp.message_handler(IsPrivate(), state=Video.video, content_types=types.ContentTypes.VIDEO)
async def music_in_data(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        file_id = msg.video.file_id
        file_unique_id = msg.video.file_unique_id
        data['function'] = 'add'
        data['user_id'] = msg.from_user.id
        data['file_id'] = file_id
        data['file_unique_id'] = file_unique_id
        await msg.reply('Напишіть назву')
        await Video.next()


@dp.message_handler(IsPrivate(), state=Video.name)
async def name_video_state(msg: types.Message, state=FSMContext):
    async with state.proxy() as data:
        data['name_video'] = msg.text
        await msg.reply('Напишіть категорію')
        await Video.next()


@dp.message_handler(IsPrivate(), state=Video.category)
async def process_name_music(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        category = msg.text
        data['category'] = category
        if await control_video(data):
            await msg.answer(f'Успішно добавленно відео')
        else:
            await msg.answer(f'Не вийшло добавити ')
        await state.finish()


@dp.message_handler(IsPrivate(), Command('get_categories'))
async def get_categories(msg: types.Message):
    musics = await search_musics(msg.from_user.id)
    videos = await search_videos(msg.from_user.id)
    ms = []
    vd = []
    data = []
    for music, video in zip(musics, videos):
        music = music.get
        video = video.get
        category_music = f'[MUSIC] {music["category"]}'
        category_video = f'[VIDEO] {video["category"]}'
        if category_music in data:
            pass
        else:
            data.append(category_music)
        if category_video in data:
            pass
        else:
            data.append(category_video)
    categories = '\n'.join(data)
    await msg.answer(categories)
        