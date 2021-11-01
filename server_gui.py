import sys

from PyQt5.QtWidgets import QMainWindow, QDialog, QApplication, QAction, qApp, QLabel, QTableView, QPushButton, \
    QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QStandardItemModel, QStandardItem


# GUI - создание таблицы QModel, для отображения в окне программы.
def gui_create_model(db):
    list_user = db.active_user_list()
    list = QStandardItemModel()
    list.setHorizontalHeaderLabels(['Имя Клиента', 'IP Адрес', 'Порт', 'Время подключения'])
    for row in list_user:
        user, ip, port, time = row
        user = QStandardItem(user)
        user.setEditable(False)
        ip = QStandardItem(ip)
        ip.setEditable(False)
        port = QStandardItem(port)
        port.setEditable(False)
        # убрать милисекунды
        time = QStandardItem(str(time.replace(microsecond=0)))
        time.setEditable(False)
        list.appendRow([user, ip, port, time])
    return list


# GUI - Функция реализующая заполнение таблицы историей сообщений.
def create_stat_model(db):
    history_list = db.message_history()
    list = QStandardItemModel()
    list.setHorizontalHeaderLabels(
        ['Имя Клиента', 'Последний раз входил', 'Сообщений отправлено', 'Сообщений получено'])
    for row in history_list:
        user, last_seen, sent, received = row
        user = QStandardItem(user)
        user.setEditable(False)
        last_seen = QStandardItem(last_seen)
        last_seen.setEditable(False)
        sent = QStandardItem(sent)
        sent.setEditable(False)
        received = QStandardItem(received)
        received.setEditable(False)
        list.appendRow([user, last_seen, sent, received])
    return list


# основное окно
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # кнопка выхода
        exitAction = QAction('Выход', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.triggered.connect(qApp.quit)

        # кнопка обновления списка клиентов
        self.refresh_button = QAction('Обновить список', self)

        # кнопка вывода истории клиентов
        self.show_history_button = QAction('История клиентов', self)

        # кнопка настройки сервера
        self.config_button = QAction('Настройки сервера', self)

        # создать статусбар
        self.statusBar()

        # тулбар
        self.toolbar = self.addToolBar('MainBar')
        self.toolbar.addAction(exitAction)
        self.toolbar.addAction(self.refresh_button)
        self.toolbar.addAction(self.show_history_button)
        self.toolbar.addAction(self.config_button)

        # определение размеров главного окна
        self.resize(800, 600)
        self.setWindowTitle('Messaging Server alpha release')

        # список подключённых клиентов
        self.lable = QLabel('Список подключённых клиентов: ', self)
        self.lable.setFixedSize(240, 15)
        self.lable.move(10, 25)

        # окно со списком подключённых клиентов
        self.active_clients_table = QTableView(self)
        self.active_clients_table.move(10, 45)
        self.active_clients_table.setFixedSize(780, 400)

        # показать окно
        self.show()


# окно истории пользователей
class HistoryWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # настройки окна
        self.setWindowTitle('Статистика клиентов')
        self.setFixedSize(600, 700)
        self.setAttribute(Qt.WA_DeleteOnClose)

        # кнопка закрытия окна
        self.close_button = QPushButton('Закрыть', self)
        self.close_button.move(250, 650)
        self.close_button.clicked.connect(self.close)

        # лист с собственной историей
        self.history_table = QTableView(self)
        self.history_table.move(10, 10)
        self.history_table.setFixedSize(580, 620)

        # показать окно
        self.show()


# окно настроек
class ConfigWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # настройки окна
        # надпись о файле БД
        # строка с путём БД
        # кнопка выбора пути
        # функция обработчик открытия окна выбора папки
        # метка с именем поля файла БД
        # поле ввода имени файла
        # метка с номером порта
        # воле ввода порта
        # метка с адресом для соединения
        # метка с напоминанием о пустом поле
        # поле ввода ip
        # кнопка сохранения настроек
        # кнопка закрытия окна
        # показать окно
        self.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    message = QMessageBox
    dial = ConfigWindow
    sys.exit(app.exec_())
