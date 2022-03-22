import asyncio
import logging

import aiogram
from aiogram import types
from aiogram.dispatcher.filters.builtin import Command, Text
from aiogram.dispatcher.storage import FSMContext
from aiogram.types.message import Message

from filters import IsPrivate
from loader import dp
from states.music_add import Music, Video
from utils.db_api.commands import control_music, control_video


def check_text(text):
	text = text.split(' ')
	count_word = 0
	for tx in text:
		for t in tx:
			count_word += 1
	


@dp.message_handler(IsPrivate(), Command('add_music'))
async def add_func(msg: Message):
	await Music.category.set()
	await msg.answer('Напиши категорію\n Щоб скасувати /cancel')
	
	
# You can use state '*' if you need to handle all states
@dp.message_handler(state='*', commands='cancel')
@dp.message_handler(Text(equals='Скасувати', ignore_case=True), state='*')
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


@dp.message_handler(IsPrivate(), state=Music.category)
async def name_music_state(msg: types.Message, state=FSMContext):
	async with state.proxy() as data:
		category = msg.text.capitalize()
		if len(category) > 10:
			await msg.answer(f'До 10 символів!  Є {len(category)}')
			await msg.answer('Надішліть категорію\n<code>Для одної та більше пісень</code>\n Щоб відмінити /cancel')
			await Music.category.set()
			
		else:
			data['category'] = category
			await msg.reply('Давай пісні\n Щоб скасувати /cancel')
			await Music.next()
		

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
				await msg.answer(f'<b>[<code>{performer}</code> - <code>{name}</code>]</b> <b>Добавлено!</b>', disable_notification=True)
			else:
				await msg.answer(f'<b>[<code>{performer}</code> - <code>{name}</code>]</b> <b>Не вийшло добавити!</b>')
			print('+')
			await asyncio.sleep(0.5)
			await state.finish()
		except KeyError:
			pass
		except aiogram.utils.exceptions.RetryAfter as err:
			await asyncio.sleep(0.5)
		except aiogram.utils.exceptions.CantParseEntities as err:
			await asyncio.sleep(0.5)
		finally:
			print('++')


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
		
		


