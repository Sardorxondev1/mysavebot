import asyncio
import logging
from typing import Union

from aiogram import types
from aiogram.dispatcher.filters.builtin import Command, Text
from aiogram.dispatcher.storage import FSMContext
from aiogram.types.callback_query import CallbackQuery
from aiogram.types.message import Message

from filters import IsPrivate
from keyboards.inline.music_panel import musics_keyboard, musics_cd
from loader import config
from loader import dp
from states.music_add import Music, Video
from utils.db_api.commands import control_music, search_musics, control_video, search_videos


@dp.message_handler(IsPrivate(), Command('add_music'))
async def add_func(msg: Message):
	await Music.category.set()
	await msg.answer('Надішліть категорію\n<code>Для одної та більше пісень</code>')
	
	
@dp.message_handler(IsPrivate(), state=Music.category)
async def name_music_state(msg: types.Message, state=FSMContext):
	async with state.proxy() as data:
		category = msg.text
		data['category'] = category
		await msg.reply('Надішліть пісню або пісні')
		await Music.next()


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
		try:
			category = data['category']
			name = f'{msg.audio.performer} - {msg.audio.title}'
			file_id = msg.audio.file_id
			name = msg.audio.title
			if not name:
				name = msg.audio.file_name
			performer = msg.audio.performer
			if not performer:
				performer = 'Невідомо'
			file_unique_id = msg.audio.file_unique_id
			if not name:
				name = msg.audio.file_name
			data['function'] = 'add'
			data['user_id'] = msg.from_user.id
			data['name_music'] = name
			data['performer'] = performer
			data['file_id'] = file_id
			data['file_unique_id'] = file_unique_id
			if await control_music(data):
				await msg.answer(f'<code>[{performer} - {name}]</code> <b>Добавлено!</b>')
			else:
				await msg.answer(f'<code>[{performer} - {name}]</code> <b>Не вийшло добавити!</b>')
			await state.finish()
		except KeyError:
			pass


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
