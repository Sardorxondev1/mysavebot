from datetime import datetime


class logger:
	def info(msg):
		file = open('data/info_bot.log','a+')
		text = f'[{datetime.now()}] [{__name__}] | INFO: {msg}'
		print(text, file=file)