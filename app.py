from aiogram import executor
from loader import dp
from utils.notify_admins import on_startup_notify
import middlewares
import filters
import handlers


async def on_startup(dispatcher):
    pass

async def on_shit(dispather):
    print('+'*1000)
if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup, skip_updates=True)
