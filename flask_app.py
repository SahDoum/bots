from settings import WEBHOOK_URL_BASE
from settings import WEBHOOK_URL_PATH1, WEBHOOK_URL_PATH2
from flask import Flask, request, abort
from bots.rollbot.rollbot import bot
from bots.mathbot.mathbot import bot as bot2
import telebot

from bots import db
from bots.settings import SQLALCHEMY_DATABASE_URI, SQLALCHEMY_DATABASE_URI2

bot.set_webhook(url=WEBHOOK_URL_BASE+WEBHOOK_URL_PATH1) # Should be set only once - then you can cut this line
bot2.set_webhook(url=WEBHOOK_URL_BASE+WEBHOOK_URL_PATH2)  # Should be set only once - then you can cut this line

app = Flask(__name__)


app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI2
app.config["SQLALCHEMY_POOL_RECYCLE"] = 299
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

#from bots.mathbot.catalog import ProposeBook
#@app.before_first_request
#def create_database():
#    ProposeBook.__table__.drop(app)
#    db.create_all()

@app.route('/')
def hello_world():

    with open('/var/log/sahdoum.pythonanywhere.com.error.log', 'r') as error_log_file:
        return '<pre>' + ''.join(error_log_file.readlines()[-1000:-1]) + '</pre>'

@app.route(WEBHOOK_URL_PATH1, methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        print(json_string)
        bot.process_new_updates([update])
        return ''
    else:
        abort(403)

@app.route(WEBHOOK_URL_PATH2, methods=['POST'])
def webhook2():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot2.process_new_updates([update])
        return ''
    else:
        abort(403)
