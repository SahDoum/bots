from sqlalchemy import Column, Integer, BigInteger, String, TEXT

from bots import db


class Catalog(db.Model):
    __tablename__ = 'catalogs'
    id =    Column(Integer, primary_key=True)
    name =  Column(String(64), unique=True)

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<Catalog %r>' % (self.name)


class Book(db.Model):
    __tablename__ = 'books'
    id =        Column(Integer, primary_key=True)
    name =      Column(String(64))
    catalog =   Column(String(64))
    author =    Column(String(64))
    link =      Column(String(255))
    comments =  Column(TEXT(convert_unicode=True))

    def __init__(self, name='', author='', link='', comments=''):
        self.name = name
        self.author = author
        self.link = link
        self.comments = comments

    def __repr__(self):
        return 'Book %r' % (self.name)


class ProposeBook(db.Model):
    __tablename__ = 'math_propose_books'
    id =        Column(Integer, primary_key=True)
    name =      Column(String(64))
    catalog =   Column(String(64))
    author =    Column(String(64))
    link =      Column(String(255))
    comments =  Column(TEXT(convert_unicode=True))
    usr_id =    Column(BigInteger, unique=True)
    usr_name =  Column(String(255))

    def __init__(self, book, usr_id, usr_name):
        self.name = book.name
        self.author = book.author
        self.link = book.link
        self.comments = book.comments
        self.usr_id = usr_id
        self.usr_name = usr_name

    def __repr__(self):
        return 'PropBook %r' % (self.name)


# status = 'Creator' 'Admin' 'Moder' 'Banned'
class User(db.Model):
    __tablename__ = 'math_users'
    id =     Column(Integer, primary_key=True)
    usr_id = Column(BigInteger, unique=True)
    name =   Column(String(255))
    status = Column(String(32))

    def __init__(self, usr_id=None, name=None, status='None'):
        self.usr_id = usr_id
        self.name = name
        self.status = status

    def __repr__(self):
        return 'Usr %r name %r status %r' % (self.usr_id,
                                             self.name,
                                             self.status)

    @staticmethod
    def logUser(usr_id):
        usr = User.query.filter_by(usr_id=usr_id).first()
        if usr:
            return usr
        else:
            return User(usr_id)

    @staticmethod
    def log_by_message(message):
        if message.chat.type == 'private':
            usr = User.query.filter_by(usr_id=message.from_user.id).first()
            if usr:
                return usr

        return User(message.from_user.id)

    def register_user(self):
        db.session.add(self)
        db.session.commit()

    def can_edit(self):
        return (self.status in ['Admin', 'Moder', 'Creator'])

    def can_add(self):
        return (self.status != 'Ban')

    def can_affirm_books(self):
        return (self.status in ['Admin', 'Moder', 'Creator'])

    def can_delete_catalog(self):
        return (self.status in ['Admin', 'Creator'])

    def can_assign_admin(self):
        return (self.status == 'Creator')

    def can_ban_user(self):
        return (self.status in ['Admin', 'Creator'])

    def can_browse_commands(self):
        return (self.status in ['Admin', 'Moder', 'Creator'])
