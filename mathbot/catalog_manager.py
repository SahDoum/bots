from .catalog import Catalog, Book, ProposeBook
from bots import db
from telebot import types
from sqlalchemy import or_


class CatalogManager:
    edit_list = {}
    catalog_list = {}

    def __repr__(self):
        return '<Catalog>'

    @staticmethod
    def get_catalog_name(cat_id):
        cat = Catalog.query.filter_by(id=cat_id).first()
        return cat.name

    @staticmethod
    def catalogs_button_keyboard(tag='catalog'):
        catalogs = Catalog.query.all()
        keyboard = types.InlineKeyboardMarkup()
        for cat in catalogs:
            callback = tag+' '+str(cat.id)
            button = types.InlineKeyboardButton(text=cat.name,
                                                callback_data=callback)
            keyboard.add(button)
        return keyboard

    @staticmethod
    def get_catalogs_keyboard():
        catalogs = Catalog.query.all()

        keyboard = types.ReplyKeyboardMarkup()
        for cat in catalogs:
            button = types.KeyboardButton(text=cat.name)
            keyboard.add(button)
        return keyboard

    # ---- ---- ---- ----
    # ---- DESCRIPTIONS ----
    # ---- ---- ---- ----

    @staticmethod
    def catalog_dsc(cat_id):
        cat = Catalog.query.get(cat_id)
        books = Book.query.filter_by(catalog=cat.name)

        if not books:
            return "``` В этом разделе пока нет книг. ```"

        dsc = "``` Список книг в разделе '%s':```\n\n" % cat.name
        i = 1
        for book in books:
            dsc += '{}. {}\n'.format(i, CatalogManager.book_dsc(book))
            i += 1
        return dsc

    @staticmethod
    def book_dsc(book):
        if book.link:
            book_name = '"[{}]({})"'.format(book.name, book.link)
        else:
            book_name = '*"{}"*'.format(book.name)
        dsc = '{} {}\n'.format(book_name, book.author)

        if book.comments:
            dsc += '_'+book.comments+'_\n'
        return dsc

    @staticmethod
    def book_dsc_no_markdown(book):
        dsc = '{} {}\n'.format(book.name, book.author)

        if book.comments:
            dsc += book.comments+'\n'
        if book.link:
            dsc += '{}'.format(book.link)
        return dsc

    # ---- ---- ----
    # ---- EDIT ----
    # ---- ---- ----

    @staticmethod
    def add_catalog(cat_name):
        if Catalog.query.filter_by(name=cat_name).first() is not None:
            return False
        cat = Catalog(cat_name)
        db.session.add(cat)
        db.session.commit()
        return True

    @staticmethod
    def is_catalog_name(cat_name):
        return Catalog.query.filter_by(name=cat_name).first() is not None

    @staticmethod
    def save_cat_id(cat_id, usr_id):
        CatalogManager.catalog_list[usr_id] = cat_id

    @staticmethod
    def get_cat_id(usr_id):
        return CatalogManager.catalog_list[usr_id]

    @staticmethod
    def rename_catalog(cat_id, new_name):
        cat = Catalog.query.filter_by(id=cat_id).first()
        books = Book.query.filter_by(catalog=cat.name).all()

        cat.name = new_name
        for book in books:
            book.catalog = new_name

        db.session.commit()

    # ---- book adding ----

    @staticmethod
    def get_edit_book(usr_id, book_id='None'):
        if usr_id not in CatalogManager.edit_list:
            if book_id != 'None':
                CatalogManager.edit_list[usr_id] = Book.query.get(book_id)
            else:
                CatalogManager.edit_list[usr_id] = Book()
        return CatalogManager.edit_list[usr_id]

    @staticmethod
    def save_edit(usr_id):
        db.session.add(CatalogManager.edit_list[usr_id])
        db.session.commit()
        CatalogManager.edit_list.pop(usr_id)

    @staticmethod
    def save_propose_edit(usr_id, usr_name):
        propose_book = ProposeBook(CatalogManager.edit_list[usr_id],
                                   usr_id, usr_name)
        db.session.add(propose_book)
        db.session.commit()
        CatalogManager.edit_list.pop(usr_id)

    # ---- catalog edit ----

    @staticmethod
    def edit_catalogs_generator():
        catalogs = Catalog.query.all()

        for cat in catalogs:
            keyboard = types.InlineKeyboardMarkup()
            open_button = types.InlineKeyboardButton(
                text=u"Открыть",
                callback_data='edit '+str(cat.id)
                )
            del_button = types.InlineKeyboardButton(
                text=u"Удалить",
                callback_data='deletecatalog '+str(cat.id)
                )
            add_button = types.InlineKeyboardButton(
                text=u"Переименовать",
                callback_data='editcatalog '+str(cat.id)
                )
            keyboard.row(open_button, del_button, add_button)

            dsc = '*{}*'.format(cat.name)

            yield {'text': dsc, 'buttons': keyboard}

    @staticmethod
    def delete_catalog(cat_id):
        cat = Catalog.query.filter_by(id=cat_id).first()
        Book.query.filter_by(catalog=cat.name).delete()
        # чот говнокод
        Catalog.query.filter_by(name=cat.name).delete()
        db.session.commit()

    # ---- book edit ----

    @staticmethod
    def edit_books_generator(cat_id):
        cat = Catalog.query.filter_by(id=cat_id).first()
        books = Book.query.filter_by(catalog=cat.name)

        if not books:
            return

        for book in books:
            keyboard = types.InlineKeyboardMarkup()
            del_button = types.InlineKeyboardButton(
                text=u"Удалить",
                callback_data='deletebook '+str(book.id)
                )
            add_button = types.InlineKeyboardButton(
                text=u"Редактировать",
                callback_data='editbook '+str(book.id)
                )
            cat_button = types.InlineKeyboardButton(
                text=u"Каталог",
                callback_data='catalogbook '+str(book.id)
                )
            keyboard.row(add_button, del_button, cat_button)

            dsc = '*{}*\n{} \n'.format(book.name, book.author)
            if book.comments:
                dsc += '_'+book.comments+'_\n'

            yield {'text': dsc, 'buttons': keyboard}

    @staticmethod
    def delete_book(book_id):
        Book.query.filter_by(id=book_id).delete()
        db.session.commit()

    # ---- ---- ---- ---- ----
    # ---- PROPOSE BOOK MENU ----
    # ---- ---- ---- ---- ----

    # надо переделать офк
    @staticmethod
    def propose_books_menu_generator():
        books = ProposeBook.query.all.order_by(ProposeBook.usr_id)

        if not books:
            return

        for book in books:
            keyboard = types.InlineKeyboardMarkup()
            del_button = types.InlineKeyboardButton(
                text=u"Удалить",
                callback_data='delprop '+str(book.id)
                )
            edit_button = types.InlineKeyboardButton(
                text=u"Редактировать",
                callback_data='editprop '+str(book.id)
                )
            add_button = types.InlineKeyboardButton(
                text=u"Добавить",
                callback_data='addprop '+str(book.id)
                )
            keyboard.row(add_button, del_button, edit_button)

            dsc = '*{}*\n{} \n'.format(book.name, book.author)
            if book.comments:
                dsc += '_'+book.comments+'_\n'

            yield {'text': dsc, 'buttons': keyboard}

    @staticmethod
    def add_propose_book(book_id):
        return

    @staticmethod
    def delete_propose_book(book_id):
        return

    # ---- ---- ---- ----
    # ---- INLINE MODE ----
    # ---- ---- ---- ----

    @staticmethod
    def get_books_by_query(query):
        offset = int(query.offset) if query.offset else 0
        books_limit = 10
        request = query.query

        catalog = Catalog.query.filter(Catalog.name.like(request+'%')).first()
        db_request = or_(Book.name.like('%'+request+'%'),
                         Book.author.like('%'+request+'%'))
        if catalog:
            db_request = or_(Book.catalog == catalog.name, db_request)
        db_query = Book.query.filter(db_request)
        db_query = db_query.limit(books_limit).offset(offset)

        books = db_query.all()
        return books

    @staticmethod
    def get_catalog_inline(query):
        books = CatalogManager.get_books_by_query(query)
        offset = int(query.offset) if query.offset else 0
        next_offset = offset+len(books)

        if books:
            answer = []
            # генерим инлайновые панельки для книг
            for book in books:
                title = '"{}" {}'.format(book.name, book.author)
                if book.link:
                    result = types.InlineQueryResultDocument(
                        id='book'+str(book.id),
                        title=title,
                        description=book.comments,
                        document_url=book.link, mime_type='application/pdf',
                        caption=CatalogManager.book_dsc_no_markdown(book)
                    )
                else:
                    book_dsc = types.InputTextMessageContent(
                        message_text=CatalogManager.book_dsc(book),
                        parse_mode='Markdown',
                        disable_web_page_preview=True
                    )
                    result = types.InlineQueryResultArticle(
                        id='book'+str(book.id),
                        title=title,
                        description=book.comments,
                        input_message_content=book_dsc
                    )
                answer.append(result)
            return (answer, str(next_offset))

        return (None, None)

    @staticmethod
    def get_catalog_list_inline(cat_name):
        catalogs = Catalog.query.all()

        if catalogs:
            answer = []
            for cat in catalogs:
                # title = '{} {}'.format(book.name, book.author)
                cat_dsc = types.InputTextMessageContent(
                    message_text=CatalogManager.catalog_dsc(cat.id),
                    parse_mode='Markdown',
                    disable_web_page_preview=True
                )
                result = types.InlineQueryResultArticle(
                    id='catalog'+str(cat.id),
                    title=cat.name,
                    # description=cat.name,
                    input_message_content=cat_dsc
                )
                answer.append(result)
            return answer

        return None

    # ---- ----
