from aiogram import Dispatcher
from loader import dp
from .user_filters import IsContributor
from .chat_filters import IsGroup
from .chat_filters import IsPrivate
from .has_permissions import HasPermissions
from .is_reply import IsReplyFilter


if __name__ == "filters":
	text_messages = [
	dp.message_handlers,
	dp.edited_message_handler,
	dp.channel_post_handlers,
	dp.edited_channel_post_handlers,
	]

	dp.filters_factory.bind(HasPermissions, event_handlers=text_messages)
	dp.filters_factory.bind(IsReplyFilter, event_handlers=text_messages)
	dp.filters_factory.bind(IsContributor)
	dp.filters_factory.bind(IsGroup)
	dp.filters_factory.bind(IsPrivate)
	
