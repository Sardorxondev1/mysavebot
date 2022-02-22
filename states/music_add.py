from aiogram.dispatcher.filters.state import State, StatesGroup


class Music(StatesGroup):
    category = State()
    audio = State(state='*')
    
    
class Video(StatesGroup):
    video = State(state='*')
    name = State()
    category = State()