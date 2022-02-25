from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.session import sessionmaker
import configparser
import os

online_db = "postgresql://scjmytdnbachvn:f13b47c4a417d436a691117290c7e07112681f7782c45e8511b6d4982267876c@ec2-52-209-246-87.eu-west-1.compute.amazonaws.com:5432/dpjikqddkqs7f"
offline_db = 'sqlite:///main.db'
config = configparser.ConfigParser()
config.read(r'data/config.ini')

bot = Bot(token=config['DEFAULT']['bot_token'],
          parse_mode=types.ParseMode.HTML)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
engine = create_engine(online_db, echo=False)
base = declarative_base()
session = sessionmaker(bind=engine)()
