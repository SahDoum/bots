from .models import User, Location, Button
from bots import db
from telebot import types
import random

from bs4 import BeautifulSoup

KEYBOARD_REMOVE_MARKUP = types.ReplyKeyboardRemove()

class Game:

    def __init__(self, message):
        if message.chat.type == 'private':
            chat_name = message.from_user.username
        else:
            chat_name = message.chat.title
        self.usr = User.logUser(message.chat.id, chat_name)

    def is_msg_fatal(self, msg):
        btn = Button.query.filter_by(loc_id=self.usr.location, dsc=msg).first()
        if btn:
            return True
        else:
            return False

    def update_location_id(self, msg=''):
        loc_id = self.usr.location

        if msg == '':
            if loc_id == -1:
                loc_key = 'default'
            else:
                #loc_key = 'default'
                return
        else:
            btn = Button.query.filter_by(loc_id=loc_id, dsc=msg).first()
            if btn:
                loc_key = btn.act_key
            else:
                return

        loc_list = Location.query.filter_by(key=loc_key).all()
        loc = random.choice(loc_list)
        self.usr.location = loc.id
        db.session.commit()

    def create_description(self):
        loc_id = self.usr.location
        loc = Location.query.get(loc_id)
        btn_list = Button.query.filter_by(loc_id=loc_id).all()

        if loc == None:
            self.usr.location = -1
            db.session.commit()
            return {'text':str(loc_id), 'buttons':None}

        text = loc.dsc

        markup = None
        if btn_list:
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
            for btn in btn_list:
                markup.add(btn.dsc)
        else:
            markup = KEYBOARD_REMOVE_MARKUP
            self.usr.location = -1
            db.session.commit()

        dsc = {'text':text, 'buttons':markup}
        return dsc

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
        dsc = str(loc.find(text=True, recursive=False))
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
