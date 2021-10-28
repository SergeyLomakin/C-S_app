import datetime
from sqlalchemy import create_engine, Column, ForeignKey, MetaData, Table, Integer, String, DateTime
from sqlalchemy.orm import mapper, sessionmaker

from common.variables import SERVER_DB


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

    def __init__(self):
        # Подключение к БД
        self.engine = create_engine(SERVER_DB, echo=False, pool_recycle=7200)

        self.metadata = MetaData()

        # таблица всех пользователей
        users_table = Table('Users', self.metadata,
                            Column('id', Integer, primary_key=True),
                            Column('name', String(50), unique=True, nullable=False),
                            Column('last_login', DateTime, default=datetime.datetime.now())
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

        # внесение изменений в БД
        self.metadata.create_all(self.engine)

        # настройка отображений
        mapper(self.AllUsers, users_table)
        mapper(self.ActiveUsers, active_users_table)
        mapper(self.LoginHistory, user_login_history)

        # создание сессии
        self.session = sessionmaker(bind=self.engine)
        self.sess_obj = self.session()
        self.sess_obj.query(self.ActiveUsers).delete()
        self.sess_obj.commit()

    # запись входа пользователя в БД
    def user_login(self, username, ip_address, port):
        print(username, ip_address, port)
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


if __name__ == '__main__':
    db = ServerStorage()
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
