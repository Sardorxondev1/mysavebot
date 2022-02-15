from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.session import sessionmaker
import configparser

config = configparser.ConfigParser()
config.read(r'data/config.ini')

bot = Bot(token=config['DEFAULT']['bot_token'],
          parse_mode=types.ParseMode.HTML)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
engine = create_engine(f"sqlite:///data/main.db", echo=False)
base = declarative_base()
session = sessionmaker(bind=engine)()
