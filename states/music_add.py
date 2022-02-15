from aiogram.dispatcher.filters.state import State, StatesGroup


class Music(StatesGroup):
    audio = State(state='*')
    name = State()
    category = State()
    
    
class Video(StatesGroup):
    video = State(state='*')
    name = State()
    category = State()