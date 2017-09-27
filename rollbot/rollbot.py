import logging

from bots.settings import API_TOKEN1
import telebot
from .fatal import Game, Editor, KEYBOARD_REMOVE_MARKUP

import dice

logger = telebot.logger
telebot.logger.setLevel(logging.DEBUG)

bot = telebot.TeleBot(API_TOKEN1, threaded=False)

# Handle '/start'
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Bot enabled")

# ---- FATAL ----

# Handle '/fatal'
@bot.message_handler(commands=['fatal'])
def fatal(message):
    game = Game(message)
    game.update_location_id()
    dsc = game.create_description()
    bot.send_message(message.chat.id, dsc['text'], parse_mode='Markdown', reply_markup=dsc['buttons'])

# Handle '/editfatal'
@bot.message_handler(commands=['editfatal'])
def editfatal(message):
    bot.reply_to(message, 'Вкидывай файл:')
    bot.register_next_step_handler(message, fatal_file)

def fatal_file(message):
    if message.document:
        Editor.delete_all()

        file_info = bot.get_file(message.document.file_id)
        file = bot.download_file(file_info.file_path)
        with open('bots/rollbot/locations.xml','wb') as new_file:
            new_file.write(file)
        with open('bots/rollbot/locations.xml','r') as read_file:
            Editor.import_from_file(read_file)
        bot.reply_to(message, 'Добавлено!')

# ---- ----
# ---- Different rolls ----

# Handle '/roll' 'r'
@bot.message_handler(commands=['roll', 'r'])
def roll (message):
    arg = message.text.split(' ')
    if len(arg)>1:
        try:
            result = dice.roll(arg[1])
            bot.reply_to(message, "Вы выкинули:\n"+str(result))
        except:
            bot.reply_to(message, "Неправильное выражение.")
    else:
        bot.reply_to(message, u'Вжух:\n'+str(dice.roll('4d6')))

# Handle '/rf'
@bot.message_handler(commands=['rf'])
def rollFate (message):
    roll = dice.roll('4d3')
    result = 0
    text = u"Вы выкинули:\n"
    for i in roll:
        if i == 1:
            text += "[-]"
        elif i == 2:
            text += "[0]"
        else:
            text += "[+]"
        result += i-2

    arg = message.text.split(' ')
    if len(arg)>1:
        text += "+"+arg[1]
        result += int(arg[1])

    text += '=\n{0}'.format(result)
    bot.reply_to(message, text)

# Handle '/rg'
@bot.message_handler(commands=['rg'])
def rollGURPS(message):
    arg = message.text.split(' ')
    roll = dice.roll('3d6t')
    text = str(roll)
    if len(arg)>1:
        if  roll > int(arg[1]):
            text += " > "+arg[1]+u"\nПровал"
        else:
            text += " ≤ "+arg[1]+u"\nУспех"
    bot.reply_to(message, text)


# ---- GURPS ----

import random
from bs4 import BeautifulSoup

# Handle '/gurps'
@bot.message_handler(commands=['gurps', 'GURPS'])
def gurps(message):
    with open('bots/rollbot/gurps.xml','r') as gurps_file:
        soup = BeautifulSoup(gurps_file, 'lxml')
        abilities = soup.find_all('gurps')
        ab = random.choice(abilities)
        bot.reply_to(message, ab.text, parse_mode='Markdown')


# Handle '/editfatal'
@bot.message_handler(commands=['editgurps'])
def editgurps(message):
    bot.reply_to(message, 'Вкидывай файл:')
    bot.register_next_step_handler(message, gurps_file)

def gurps_file(message):
    if message.document:
        file_info = bot.get_file(message.document.file_id)
        file = bot.download_file(file_info.file_path)
        with open('bots/rollbot/gurps.xml','wb') as new_file:
            new_file.write(file)
        bot.reply_to(message, 'Добавлено!')

# ---- NOT-COMAND HANDLERS ---- #

@bot.message_handler(func=lambda m: True, content_types=['text'])
def register_fatal(message):
    game = Game(message)
    if not game.is_msg_fatal(message.text):
        return
    game.update_location_id(message.text)
    dsc = game.create_description()
    bot.reply_to(message, dsc['text'], parse_mode='Markdown', reply_markup=dsc['buttons'])

@bot.message_handler(func=lambda m: True, content_types=['new_chat_members'])
def new_chat_participant(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, 'Приветствую, путник!')
