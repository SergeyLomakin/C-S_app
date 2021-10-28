import sys
import logging
import logs.config_server_log
import logs.config_client_log


# Инициализиция логера
# метод определения модуля, источника запуска.
if sys.argv[0].find('client') == -1:
    logger = logging.getLogger('server')
else:
    logger = logging.getLogger('client')


# Дескриптор данных для порта
class Port:
    def __set__(self, instance, value):
        # логгирование некорректного порта
        if not 1023 < value < 65535:
            logger.critical(
                f'Попытка запуска сервера с указанием неподходящего порта {value}. Допустимы адреса с 1024 до 65535.')
            exit(1)

        instance.__dict__[self.name] = value

    def __set_name__(self, owner, name):
        self.name = name
