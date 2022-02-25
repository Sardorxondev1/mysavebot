from aiogram import types
from aiogram.dispatcher.filters import BoundFilter
import logging

from utils.db_api.commands import search_users

events = []

class IsGroup(BoundFilter):

	async def check(self, message: types.Message):
		try:
			return message.chat.type in (types.ChatType.GROUP,
									 	types.ChatType.SUPERGROUP)
		except AttributeError as err:
			if str(err) == "'CallbackQuery' object has no attribute 'chat'":
				call = message
				return call.message.chat.type in (types.ChatType.GROUP, types.ChatType.SUPERGROUP)
			else:
				logging.error(str(err))
		except Exception as err:
			logging.error(str(err))

event = 0
user_tl = False
class IsPrivate(BoundFilter):

	async def check(self, msg: types.Message):
		try:
			global event, user_tl
			user_id = msg.from_user.id
			event += 1
			if event > 9:
				event = 1
			if event == 1:
				user = await search_users(user_id=user_id)
				if not user:
					await msg.answer('Ви не зареєстровані\nЩоб зареєструватись /reg')
					user_tl = False
				else:
					user_tl = True
			if user_tl:
				return True
			else:
				pass
		except AttributeError as err:
			if str(err) == "'CallbackQuery' object has no attribute 'chat'":
				call = msg
				user_id = call.message.user_id
				await msg.answer(user_id)
				event += 1
				if event > 9:
					event = 1
				if event == 9:
					user = await search_users(user_id=user_id)
					if not user:
						await msg.answer('Ви не зареєстровані\nЩоб зареєструватись /reg')
						user_tl = False
					else:
						user_tl = True
				if user_tl:
					return True
			else:
				logging.error(str(err))
		except Exception as err:
			logging.error(str(err))