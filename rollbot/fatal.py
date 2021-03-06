from .models import Location, Button
from bots import db
from telebot import types
import random

from bs4 import BeautifulSoup

#from telegram.utils.helpers import escape_markdown


def create_description(callback=None):
    if callback:
        btn_id = int(callback.data.split(' ')[1])
        btn = Button.query.get(btn_id)
        loc_key = btn.act_key

        if loc_key == 'default':
            return {'text': callback_title(callback),
                    'buttons': None
                    }
    else:
        loc_key = 'default'

    loc_list = Location.query.filter_by(key=loc_key).all()
    loc = random.choice(loc_list)
    btn_list = Button.query.filter_by(loc_id=loc.id).all()

    dsc_title = callback_title(callback)
    text = dsc_title + loc.dsc
    markup = create_keyboard(btn_list)
    dsc = {'text': text, 'buttons': markup}
    return dsc


def create_keyboard(btn_list):
    markup = None
    if btn_list:
        markup = types.InlineKeyboardMarkup()
        for btn in btn_list:
            inline_button = types.InlineKeyboardButton(
                text=btn.dsc,
                callback_data="f "+ str(btn.id)
                )
            markup.add(inline_button)
    return markup


def callback_title(callback):
        if not callback:
            return ''

        author = ''
        if callback.message.chat.type != 'private':
            author = user_to_author(callback.from_user)
        btn_id = int(callback.data.split(' ')[1])
        btn = Button.query.get(btn_id)
        title = author + '*>> ' + btn.dsc + '*\n\n'
        return title


def user_to_author(usr):
    if usr.username:
        author = '@' + usr.username + ' '
    else:
        author = '$ ' + usr.first_name + ' '
    return escape_markdown(author)

def escape_markdown(str):
    return str.replace('_', '\_')

class Editor:

    @staticmethod
    def delete_all():
        if not Location.query.first():
            return
        Location.query.delete()
        Button.query.delete()
        db.session.commit()

    @staticmethod
    def import_from_file(file):
        soup = BeautifulSoup(file, 'lxml')
        locations = soup.find_all('loc')

        for loc in locations:
            Editor.add_location(loc)
        db.session.commit()

    @staticmethod
    def add_location(loc):
        dsc = str(loc.find(text=True, recursive=False)).strip()
        key = str(loc['key'])
        location = Location(key, dsc)
        db.session.add(location)
        db.session.commit()
        db.session.refresh(location)
        loc_id = location.id
        buttons = loc.find_all('btn')
        print(location)
        for btn in buttons:
            btn_dsc = btn.text
            btn_act = btn['key']
            button = Button(loc_id, btn_act, btn_dsc)
            db.session.add(button)
            db.session.commit()
            print(button)
