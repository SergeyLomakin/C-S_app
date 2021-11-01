import datetime
from sqlalchemy import create_engine, Column, ForeignKey, MetaData, Table, Integer, String, DateTime
from sqlalchemy.orm import mapper, sessionmaker

from common.variables import *


class ServerStorage:
    # класс для таблицы всех пользователей
    class AllUsers:
        def __init__(self, username):
            self.id = None
            self.name = username
            self.last_login = datetime.datetime.now()

        def __repr__(self):
            return f"<f'User {self.name} {self.last_login}'>"

    # класс для таблицы пользователей онлайн
    class ActiveUsers:
        def __init__(self, user_id, ip_address, port, login_time):
            self.id = None
            self.user = user_id
            self.ip_address = ip_address
            self.port = port
            self.login_time = login_time

        def __repr__(self):
            return f"<f'User {self.user} {self.ip_address} {self.port} {self.login_time}'>"

    # класс для таблицы истории входов пользователей
    class LoginHistory:
        def __init__(self, name, date_time, ip_address, port):
            self.id = None
            self.name = name
            self.date_time = date_time
            self.ip_address = ip_address
            self.port = port

        def __repr__(self):
            return f"<f'User {self.name} {self.date_time} {self.ip_address} {self.port}'>"

    # класс для таблицы контактов пользователей
    class UsersContacts:
        def __init__(self, user, contact):
            self.id = None
            self.user = user
            self.contact = contact

    # класс для таблицы истории действий
    class UsersHistory:
        def __init__(self, user):
            self.id = None
            self.user = user
            self.sent = 0
            self.accepted = 0

    def __init__(self, path):
        # Подключение к БД
        self.engine = create_engine(f'sqlite:///{path}', echo=False, pool_recycle=7200,
                                    connect_args={'check_same_thread': False})

        self.metadata = MetaData()

        # таблица всех пользователей
        users_table = Table('Users', self.metadata,
                            Column('id', Integer, primary_key=True),
                            Column('name', String(50), unique=True, nullable=False),
                            Column('last_login', DateTime)
                            )

        # таблица пользователей онлайн
        active_users_table = Table('Active_users', self.metadata,
                                   Column('id', Integer, primary_key=True),
                                   Column('user', ForeignKey('Users.id'), unique=True),
                                   Column('ip_address', String(50), nullable=False),
                                   Column('port', Integer, nullable=False),
                                   Column('login_time', DateTime)
                                   )

        # таблица истории входов пользователей
        user_login_history = Table('Login_history', self.metadata,
                                   Column('id', Integer, primary_key=True),
                                   Column('user', ForeignKey('Users.id')),
                                   Column('date_time', DateTime),
                                   Column('ip_address', String(50), nullable=False),
                                   Column('port', Integer, nullable=False)
                                   )

        # таблица контактов пользователей
        contacts = Table('Contacts', self.metadata,
                         Column('id', Integer, primary_key=True),
                         Column('user', ForeignKey('Users.id')),
                         Column('contact', ForeignKey('Users.id'))
                         )

        # таблица истории пользователей
        users_history_table = Table('History', self.metadata,
                                    Column('id', Integer, primary_key=True),
                                    Column('user', ForeignKey('Users.id')),
                                    Column('sent', Integer),
                                    Column('accepted', Integer)
                                    )

        # внесение изменений в БД
        self.metadata.create_all(self.engine)

        # настройка отображений
        mapper(self.AllUsers, users_table)
        mapper(self.ActiveUsers, active_users_table)
        mapper(self.LoginHistory, user_login_history)
        mapper(self.UsersContacts, contacts)
        mapper(self.UsersHistory, users_history_table)

        # создание сессии
        session = sessionmaker(bind=self.engine)
        self.sess_obj = session()
        self.sess_obj.query(self.ActiveUsers).delete()
        self.sess_obj.commit()

    # запись входа пользователя в БД
    def user_login(self, username, ip_address, port):
        # print(username, ip_address, port)
        # проверка на существование пользователя
        rez = self.sess_obj.query(self.AllUsers).filter_by(name=username)
        # пользователь существует - обновить время последнего входа
        if rez.count():
            user = rez.first()
            user.last_login = datetime.datetime.now()
        # пользователя не существует - создать нового пользователя
        else:
            user = self.AllUsers(username)
            self.sess_obj.add(user)
            user_in_history = self.UsersHistory(user.id)
            self.sess_obj.add(user_in_history)
            self.sess_obj.commit()

        # создать запись в таблицу активных пользователей
        new_active_user = self.ActiveUsers(user.id, ip_address, port, datetime.datetime.now())
        self.sess_obj.add(new_active_user)

        # сохранить время входа в историю
        new_login = self.LoginHistory(user.id, datetime.datetime.now(), ip_address, port)
        self.sess_obj.add(new_login)

        self.sess_obj.commit()

    # запись выхода пользователя в БД
    def user_logout(self, username):
        # находим нужного пользователя
        user = self.sess_obj.query(self.AllUsers).filter_by(name=username).first()
        # удаляем его из таблицы пользователей онлайн
        self.sess_obj.query(self.ActiveUsers).filter_by(user=user.id).delete()
        self.sess_obj.commit()

    # фиксация передачи сообщения с записью в БД
    def process_message(self, sender, recipient):
        # получить id отправителя и получателя
        sender = self.sess_obj.query(self.AllUsers).filter_by(name=sender).first().id
        recipient = self.sess_obj.query(self.AllUsers).filter_by(name=recipient).first().id

        # увеличение счётчика сообщений
        sender_row = self.sess_obj.query(self.UsersHistory).filter_by(user=sender).first()
        sender_row.sent += 1
        recipient_row = self.sess_obj.query(self.UsersHistory).filter_by(user=recipient).first()
        recipient_row.accepted += 1

        self.sess_obj.commit()

    # добавить контакт для пользователя
    def add_contact(self, user, contact):
        # id пользователей
        user = self.sess_obj.query(self.AllUsers).filter_by(name=user).first()
        contact = self.sess_obj.query(self.AllUsers).filter_by(name=contact).first()

        # проверяем что не дубль и что контакт может существовать
        if not contact or self.sess_obj.query(self.UsersContacts).filter_by(user=user.id, contact=contact.id).count():
            return

        # занести контакт в БД
        new_contact = self.UsersContacts(user.id, contact.id)
        self.sess_obj.add(new_contact)
        self.sess_obj.commit()

    # удалить контакт для пользователя
    def remove_contact(self, user, contact):
        # id пользователей
        user = self.sess_obj.query(self.AllUsers).filter_by(name=user).first()
        contact = self.sess_obj.query(self.AllUsers).filter_by(name=contact).first()

        # проверяем что контакт может существовать
        if not contact:
            return

        # удалить
        self.sess_obj.query(self.UsersContacts).filter(
            self.UsersContacts.user == user.id,
            self.UsersContacts.contact == contact.id
        ).delete()
        self.sess_obj.commit()

    # список всех пользователей со временем последнего входа
    def users_list(self):
        query = self.sess_obj.query(self.AllUsers.name, self.AllUsers.last_login)
        return query.all()

    # список активных пользователей
    def active_users_list(self):
        query = self.sess_obj.query(
            self.AllUsers.name,
            self.ActiveUsers.ip_address,
            self.ActiveUsers.port,
            self.ActiveUsers.login_time
        ).join(self.AllUsers)
        return query.all()

    # список истории входов
    def login_history(self, username=None):
        query = self.sess_obj.query(
            self.AllUsers.name,
            self.LoginHistory.date_time,
            self.LoginHistory.ip_address,
            self.LoginHistory.port
        ).join(self.AllUsers)
        # фильтрация, ксли задано имя
        if username:
            query = query.filter(self.AllUsers.name == username)
        return query.all()

    # список контактов пользователя
    def get_contact(self, username):
        # получить пользователя
        user = self.sess_obj.query(self.AllUsers).filter_by(name=username).one()

        # список контактов пользователя
        query = self.sess_obj.query(self.UsersContacts, self.AllUsers.name).filter_by(user=user.id). \
            join(self.AllUsers, self.UsersContacts.contact == self.AllUsers.id)

        # выбираем только имена пользователей и возвращаем их.
        return [contact[1] for contact in query.all()]

    # количество сообщений
    def message_history(self):
        query = self.sess_obj.query(
            self.AllUsers.name,
            self.AllUsers.last_login,
            self.UsersHistory.sent,
            self.UsersHistory.accepted
        ).join(self.AllUsers)
        return query.all()


if __name__ == '__main__':
    db = ServerStorage('')
    # подключаем пользователей
    db.user_login('user1', '192.168.0.1', 4321)
    db.user_login('user2', '192.168.0.2', 4322)
    # выводим список активных пользователей
    print(db.active_users_list())
    # отключаем одного пользователя
    db.user_logout('user1')
    # выводим список активных пользователей
    print(db.active_users_list())
    # смотрим историю входов пользователя
    db.login_history('user1')
    # выводим список всех пользователей
    print(db.users_list())

    db.add_contact('test2', 'test1')
    db.add_contact('test1', 'test3')
    db.add_contact('test1', 'test6')
    db.remove_contact('test1', 'test3')
    db.process_message('McG2', '1111')
    print(db.message_history())
