import asyncio
import logging
from typing import Union

from aiogram import types
from aiogram.dispatcher.filters.builtin import Command, Text
from aiogram.dispatcher.storage import FSMContext
from aiogram.types.callback_query import CallbackQuery
from aiogram.types.message import Message

from filters import IsPrivate
from keyboards.inline.music_ad import music_add_panel, music_ad_cd
from keyboards.inline.music_panel import musics_keyboard, musics_cd
from loader import config
from loader import dp, bot
from states.music_add import Music, Video
from utils.db_api.commands import control_music, get_categories, search_musics, control_video, search_videos


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
		await msg.answer(f'M E N U [{name_menu}]', reply_markup=markup)
	elif isinstance(msg, CallbackQuery):
		call = msg
		await call.message.edit_reply_markup(markup)


async def music_show(call: CallbackQuery, **kwargs):
	try:
		user_id = kwargs['user_id']
		id_code = kwargs['id_code']
		musics = await search_musics(user_id=user_id, file_unique_id=id_code)
		file_id = musics.get['file_id']
		markup = await music_add_panel(user_id=user_id, id_code=id_code)
		await call.message.answer_audio(file_id, reply_markup=markup)
	except AttributeError as err:
		logging.error(err)
		await dp.bot.answer_callback_query(call.id, text='Не найдено пісню[Оновіть сторінку]')


async def video_show(call: CallbackQuery, **kwargs):
	user_id = kwargs['user_id']
	id_code = kwargs['id_code']
	video = await search_videos(user_id=user_id, file_unique_id=id_code)
	file_id = video.get['file_id']
	await call.message.answer_video(file_id)
	
	
async def all_musics(call: CallbackQuery, **kwargs):
	from_page = kwargs['from_page']
	page = from_page.split(',')
	message_id = call.message.message_id
	category = kwargs['func']
	musics = await search_musics(kwargs['user_id'], category=category)
	for music in musics[int(page[0]):int(page[1])]:
		music = music.get
		markup = await music_add_panel(user_id=music['user_id'], id_code=music['id_code'])
		await call.message.answer_audio(audio=music['file_id'], reply_markup=markup)
	markup = await musics_keyboard(kwargs["user_id"], name_menu='music', category=None)
	await bot.delete_message(chat_id=kwargs['user_id'], message_id=message_id)
	await bot.send_message(chat_id=kwargs['user_id'], text='M E N U [music]', reply_markup=markup)
	
	
async def change_category(call: CallbackQuery, **kwargs):
	user_id = kwargs['user_id']
	name_menu = kwargs['name_menu']
	markup = await musics_keyboard(user_id=user_id, name_menu='change_menu')
	await call.message.edit_reply_markup(markup)
	
	
async def change_menu(call: CallbackQuery, **kwargs):
	await music_st_panel(call, name_menu='music', category=kwargs['func'])
	

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


@dp.callback_query_handler(IsPrivate(), music_ad_cd.filter())
async def control_music_ad(call: CallbackQuery, callback_data: dict):
	action = callback_data.get('action')
	user_id = callback_data.get('user_id')
	id_code = callback_data.get('id_code')
	message_id = call.message.message_id
	if action == 'hide_music':
		await call.message.delete()
	elif action == 'delete_music':
		data = {
			'function': 'remove',
			'user_id': user_id,
			'file_unique_id': id_code,
		}
		if await control_music(data):
			await dp.bot.answer_callback_query(call.id, text='Видалено!')
			await call.message.delete()
		else:
			await dp.bot.answer_callback_query(call.id, text='Помилка!')


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
		'all_musics': all_musics,
		'change_category': change_category,
		'change_menu': change_menu,
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
	print(
		f'ACTION: {action} | FUNC: {func} | USER_ID: {user_id} | ID_CODE: {id_code} | PAGES: {pages} | PAGE: {page} | FROM_PAGE: {from_page} | NAME_MENU: {name_menu}')

