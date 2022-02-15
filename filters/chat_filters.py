from aiogram import types
from aiogram.dispatcher.filters import BoundFilter
import logging


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


class IsPrivate(BoundFilter):

	async def check(self, message: types.Message):
		try:
			return message.chat.type == types.ChatType.PRIVATE
		except AttributeError as err:
			if str(err) == "'CallbackQuery' object has no attribute 'chat'":
				call = message
				return call.message.chat.type == types.ChatType.PRIVATE
			else:
				logging.error(str(err))
		except Exception as err:
			logging.error(str(err))