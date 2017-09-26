from bots.settings import SQLALCHEMY_DATABASE_URI
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, BigInteger, String
from sqlalchemy import TEXT

from bots import db

#engine = create_engine(SQLALCHEMY_DATABASE_URI, pool_recycle=200)
#Session = sessionmaker(bind=engine)
#session = Session()
#Base = declarative_base()
#md = Base.metadata

class User(db.Model):
    __tablename__ = 'rollclub_users'
    id =        Column(Integer, primary_key=True)
    chat_id =   Column(BigInteger, unique=True)
    chat_name = Column(String(80))
    location =  Column(Integer)

    def __init__(self, chat_id, chat_name, loc_id):
        self.chat_id = chat_id
        self.chat_name = chat_name
        self.location  = loc_id

    def __repr__(self):
        return '<User %r Id %r>' % (self.chat_name, self.chat_id)

    @classmethod
    def logUser(cls, chat_id, name):
        usr = User.query.filter_by(chat_id=chat_id).first()
        if usr:
            return usr
        else:
            new_usr = User(chat_id, name, -1)
            db.session.add(new_usr)
            db.session.commit()
            return new_usr

class Location(db.Model):
    __tablename__ = 'rollclub_locations'
    id =    Column(Integer, primary_key=True)
    key =   Column(String(64))
    dsc =   Column(TEXT(convert_unicode=True))

    def __init__(self, key, dsc):
        self.key = key
        self.dsc = dsc

    def __repr__(self):
        return '<Location %r dsc %r>' % (self.key, self.dsc)

class Button(db.Model):
    __tablename__ = 'rollclub_buttons'
    id =        Column(Integer, primary_key=True)
    loc_id =    Column(Integer)
    act_key =   Column(String(64))
    dsc =       Column(TEXT(convert_unicode=True))

    def __init__(self, loc_id, act_key, dsc):
        self.loc_id = loc_id
        self.act_key = act_key
        self.dsc = dsc

    def __repr__(self):
        return '<Button %r act %r dsc %r>' % (self.loc_id, self.act_key, self.dsc)