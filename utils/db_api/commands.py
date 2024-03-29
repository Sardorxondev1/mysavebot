from .models import Music, User, DataLogger, Video
import sqlalchemy
from sqlalchemy import func, text
from loader import session, base, engine, config
import logging

# base.metadata.drop_all(engine)

base.metadata.create_all(engine)

table_models = {
    'users': User,
    'log': DataLogger,
    'musics': Music,
    'videos': Video,
}

columns_dict = {
    'users': {'user_id': User.user_id,
              'chat_id': User.chat_id,
              'username': User.username,
              'fullname': User.fullname,
              'admin': User.admin,
              'status_sms': User.status_sms,
              'chat_to_msg': User.chat_to_msg,
              'register': User.register},
    'log': {'level': DataLogger.level,
            'msg': DataLogger.msg,
            'data': DataLogger.data},
    'musics': {'user_id': Music.user_id,
               'name': Music.name,
               'performer': Music.performer,
               'category': Music.category,
               'id_code': Music.id_code,
               'file_id': Music.file_id},
    'videos': {'user_id': Video.user_id,
               'name': Video.name,
               'category': Video.category,
               'id_code': Video.id_code,
               'file_id': Video.file_id}
}


def commit():
    session.commit()
    session.close()


def add(data: list):
    for ls in data:
        session.add(ls)
    commit()


def check(user_id, model):
    if session.query(model).filter_by(user_id=int(user_id)).first():
        return True
    else:
        return False


def check_group(chat_id, model):
    if session.query(model).filter_by(chat_id=int(chat_id)).first():
        return True
    else:
        return False


async def check_admin(user_id):
    if session.query(User).filter(User.user_id == int(user_id), User.admin == '1').first():
        return True
    else:
        return False


async def check_musics(user_id, file_unique_id):
    if session.query(Music).filter(Music.user_id == int(user_id), Music.id_code == file_unique_id).first():
        return True
    else:
        return False
    
    
async def check_videos(user_id, file_unique_id):
    if session.query(Video).filter(Video.user_id == int(user_id), Video.id_code == file_unique_id).first():
        return True
    else:
        return False


async def del_acc(model, user_id):
    session.query(model).filter_by(user_id=int(user_id)).delete(synchronize_session="fetch")
    commit()


async def del_group(chat_id):
    session.query(Group).filter_by(chat_id=int(chat_id)
                                   ).delete(synchronize_session="fetch")
    commit()


async def logger(level, msg):
    try:
        add([DataLogger(level, msg)])
    except Exception as err:
        logging.exception(err)
        add([DataLogger('ERROR', 'function: logger | file: commands.py')])


async def register_user(data: dict):
    try:
        username = data['username']
        user_id = data['user_id']
        if check(data['user_id'], User):
            return 'Ви вже зареєстровані'
        else:
            add([User(user_id, data['chat_id'],
                data['username'], data['fullname'])])
            await logger('INFO', 'NEW USER: @' + username + '[' + str(user_id) + ']')
            return f'<b>Вас зареєстрованно в системі!</b>\n<code>@{username}[{user_id}]</code>'
    except Exception as err:
        logging.exception(err)
        return '<b>Виникла помилка!</b>\n<code>Попробуйте ще-раз або пізніше!</code>'


async def register_group(data: dict) -> dict:
    try:
        if not check_group(data['chat_id'], Group):
            add([Group(data['chat_id'], data['name_group'])])
    except Exception as err:
        logging.exception(err)
        return 'Виникла помилка!\nПопробуйте ще-раз або пізніше'


async def control_music(data: dict):
    try:
        if data['function'] == 'add':
            user_id = data['user_id']
            name = data['name_music']
            performer = data['performer']
            category = data['category']
            file_id = data['file_id']
            id_code = data['file_unique_id']
            if not await check_musics(user_id, id_code):
                add([Music(user_id, name, performer, category, id_code, file_id)])
                commit()
                return True
        elif data['function'] == 'remove':
            user_id = data['user_id']
            id_code = data['file_unique_id']
            session.query(Music).filter(Music.user_id == int(
                user_id), Music.id_code == id_code).delete(synchronize_session="fetch")
            commit()
            return True
    except Exception as err:
        logging.exception(err)
        
        
async def control_video(data: dict):
    try:
        if data['function'] == 'add':
            user_id = data['user_id']
            name = data['name_video']
            category = data['category']
            file_id = data['file_id']
            id_code = data['file_unique_id']
            if not await check_videos(user_id, id_code):
                add([Video(user_id, name, category, id_code, file_id)])
                commit()
                return True
        elif data['function'] == 'remove':
            user_id = data['user_id']
            id_code = data['file_unique_id']
            session.query(Video).filter(Video.user_id == int(
                user_id), Video.id_code == id_code).delete(synchronize_session="fetch")
            commit()
            return True
    except Exception as err:
        logging.exception(err)


async def makeadmin(user_id=None, action='add_admin'):
    if session.query(User).filter_by(user_id=int(user_id)).exists():
        if action == 'add_admin':
            print('+')
            session.query(User).filter(User.user_id == int(user_id)). \
                update({"admin": "1"}, synchronize_session="fetch")
            commit()
            return
        elif action == 'del_admin':
            print('+')
            session.query(User).filter(User.user_id == int(user_id)). \
                update({"admin": "0"}, synchronize_session="fetch")
            commit()
            return
        else:
            return

    else:
        logging.error(f'NOT FOUND ID: {user_id}')


async def search_users(user_id=None):
    try:
        if not user_id:
            return session.query(User).distinct()
        else:
            return session.query(User).filter(User.user_id == user_id).distinct().first()
    except Exception as err:
        logging.exception(err)


async def search_groups(chat_id=None):
    try:
        if not chat_id:
            return session.query(Group).distinct()
        if chat_id:
            return session.query(Group).filter_by(chat_id=chat_id).distinct().first()
    except Exception as err:
        logging.exception(err)


async def search_musics(user_id, file_unique_id=None, category=None):
    text = ''
    if not file_unique_id:
        if not category:
            text = session.query(Music).filter_by(user_id=user_id).distinct()
        else:
            text = session.query(Music).filter_by(user_id=user_id, category=category).distinct()
    else:
        text = session.query(Music).filter_by(
            user_id=user_id, id_code=file_unique_id).first()
    return text


async def search_videos(user_id, category=None, file_unique_id=None):
    text = ''
    if not file_unique_id:
        if not category:
            text = session.query(Video).filter_by(user_id=user_id).distinct()
        else:
            text = session.query(Video).filter_by(user_id=user_id, category=category).distinct()
    else:
        text = session.query(Video).filter_by(user_id=user_id, id_code=file_unique_id).first()

    return text


async def search_max_page(user_id):
    count = session.query(func.count(Music.user_id)).filter_by(user_id=user_id).first()
    return count[0]


async def get_categories(user_id):
    categories = []
    data = session.query(Music).filter_by(user_id=user_id).distinct()
    for dt in data:
        dt = dt.get 
        category = dt['category']
        if not category in categories:
            categories.append(category)
    return categories


async def get_with_db(table_name, filter_dt=None):
    model = table_models[table_name]
    data = []
    db_request = None
    if not filter_dt:
        db_request = session.query(model).distinct()
    else:
        column = filter_dt[0]
        db_request = session.query(model).filter(columns_dict[table_name][column] == filter_dt[1]).distinct()
    for rs in db_request:
        rs = rs.get
        sr = {}
        for clm in columns_dict[table_name].keys():
            sr[clm] = rs[clm]
        data.append(sr)
    return data


async def del_with_db(table_name, filter_dt=None):
    try:
        model = table_models[table_name]
        data = []
        db_request = None
        if not filter_dt:
            db_request = session.query(model).delete(synchronize_session="evaluate")
        else:
            column = filter_dt[0]
            db_request = session.query(model).filter(columns_dict[table_name][column] == filter_dt[1]).delete(synchronize_session="evaluate")
        commit()
        if int(db_request) == 1:
            return True
        else:
            return '[ERROR] Не найдено в базі данних!'
    except IndexError:
        return '[ERROR] /del [table_name]-[column]=?'
    except KeyError as ex:
        return f'[ERROR] Не знайдено {ex}'
