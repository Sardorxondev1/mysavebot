from utils.db_api.commands import search_max_page, search_musics, search_videos
from aiogram.types.inline_keyboard import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.callback_data import CallbackData
from loader import config

musics_cd = CallbackData('musics', 'action', 'func', 'user_id', 'id_code', 'pages', 'page', 'from_page', 'name_menu')


def make_callback(action='0', func='0', user_id='0', id_code='0', pages='0', page='1', from_page='0', name_menu='0'):
    return musics_cd.new(action=action, func=func, user_id=user_id, id_code=id_code, pages=pages, page=page, from_page=from_page, name_menu=name_menu)


async def musics_keyboard(user_id, page='1', count_page_max=config['MUSIC_SETTINGS']['counts'], count_page_min='0', name_menu=None, category=None):
    markup = InlineKeyboardMarkup(row_width=1)
    datas = []
    if name_menu == 'music':
        datas = await search_musics(user_id, category=category)
    elif name_menu == 'video':
        datas = await search_videos(user_id, category=category)
    else:
        datas = ['Нічого немає']
    count = await search_max_page(user_id)
    pages = str(int(count) / int(count_page_max)).split('.')
    # pages_2 = int(count) / int(count_page_max)
    
    if int(pages[1]) > 0:
        pages = int(pages[0]) + 1
    else:
        pages = int(pages[0])
    for data in datas[int(count_page_min):int(count_page_max)]:
        data = data.get
        callback = make_callback(action=name_menu, user_id=data['user_id'], id_code=data['id_code'])
        markup.insert(InlineKeyboardButton(text=data['name'], callback_data=callback))
    markup.row(InlineKeyboardButton(text='Вперід ⏩', callback_data=make_callback(action='navigate', func='next', user_id=user_id, pages=pages, page=page, from_page=f'{count_page_min},{count_page_max}', name_menu=name_menu)),
               InlineKeyboardButton(text=f'Оновити[{page} ст.]', callback_data=make_callback(user_id=user_id, from_page=f'{count_page_min},{count_page_max}', page=page, action='update_page', name_menu=name_menu)),
               InlineKeyboardButton(text='Назад ⏪', callback_data=make_callback(action='navigate', func='back',user_id=user_id, pages=1, page=page, from_page=f'{count_page_min},{count_page_max}', name_menu=name_menu)))
    return markup