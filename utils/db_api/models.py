from sqlalchemy import *
from loader import base
from datetime import datetime

format = "%d/%m/%Y %H:%M:%S"


class User(base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, unique=True)
    chat_id = Column(Integer)
    username = Column(String)
    fullname = Column(String)
    admin = Column(Integer, default='0')
    status_sms = Column(Integer, default='0')
    chat_to_msg = Column(Integer, default='0')
    register = Column(String, default=datetime.now().strftime(format))

    def __init__(self, user_id, chat_id, username, fullname):
        self.user_id = user_id
        self.chat_id = chat_id
        self.username = username
        self.fullname = fullname

    def __repr__(self):
        return 'None'

    @property
    def get(self):
        return {
            'user_id': self.user_id,
            'chat_id': self.chat_id,
            'username': self.username,
            'fullname': self.fullname,
            'admin': self.admin,
            'status_sms': self.status_sms,
            'chat_to_msg': self.chat_to_msg,
            'register': self.register,
        }


class DataLogger(base):
    __tablename__ = 'log'
    id = Column(Integer, primary_key=True)
    level = Column(String)
    msg = Column(String)
    data = Column(String, default=datetime.now().strftime(format))

    def __init__(self, level, msg):
        self.msg = msg
        self.level = level

    def __repr__(self):
        return f'<LOGGER: {self.level} {self.msg} {self.data}'

    @property
    def get(self):
        return {
            'level': self.level,
            'msg': self.msg,
            'data': self.data,
        }


class Music(base):
    __tablename__ = 'musics'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    name = Column(String)
    performer = Column(String)
    category = Column(String)
    id_code = Column(String)
    file_id = Column(String)

    def __init__(self, user_id, name, performer, category, id_code, file_id):
        self.name = name
        self.performer = performer
        self.category = category
        self.id_code = id_code 
        self.user_id = user_id
        self.file_id = file_id

    def __repr__(self) -> str:
        return {'name': self.name, 'performer': self.performer, 'category': self.category, 'id_code': self.id_code, 'user_id': self.user_id, 'file_id': self.file_id}

    @property
    def get(self):
        return {'name': self.name, 'performer': self.performer, 'category': self.category, 'id_code': self.id_code, 'user_id': self.user_id, 'file_id': self.file_id}


class Video(base):
    __tablename__ = 'videos'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    name = Column(String)
    category = Column(String)
    id_code = Column(String)
    file_id = Column(String)

    def __init__(self, user_id, name, category, id_code, file_id):
        self.name = name
        self.category = category
        self.id_code = id_code 
        self.user_id = user_id
        self.file_id = file_id

    def __repr__(self) -> str:
        return {'name':self.name, 'category': self.category, 'id_code': self.id_code, 'user_id': self.user_id, 'file_id': self.file_id}

    @property
    def get(self):
        return {'name':self.name, 'category': self.category, 'id_code': self.id_code, 'user_id': self.user_id, 'file_id': self.file_id}