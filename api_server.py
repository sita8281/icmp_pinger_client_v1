import socket
import json
import struct
import queue
import time
import zlib


class Get:
    @staticmethod
    def all_hosts():
        """
        Получить список всех хостов и их параметров
        """
        return {
            'request': 'GET',
            'object': 'HOST',
            'item': 'all'
        }

    @staticmethod
    def one_host(ip: str):
        """
        Получить информацию о хосте по IP
        """
        return {
            'request': 'GET',
            'object': 'HOST',
            'item': {
                'ip': ip
            }
        }

    @staticmethod
    def dead_hosts():
        """
        Получить список OFFLINE хостов
        """
        return {
            'request': 'GET',
            'object': 'HOST',
            'item': 'dead'
        }

    @staticmethod
    def live_hosts():
        """
        Получить список ONLINE хостов
        """
        return {
            'request': 'GET',
            'object': 'HOST',
            'item': 'live'
        }

    @staticmethod
    def pause_hosts():
        """
        Получить список хостов которые стоят на паузе
        """
        return {
            'request': 'GET',
            'object': 'HOST',
            'item': 'pause'
        }

    @staticmethod
    def folder_with_hosts(id_folder: str):
        """
        Получить список хостов в папке id_folder
        """
        return {
            'request': 'GET',
            'object': 'FOLDER',
            'item': {
                'folder_id': id_folder
            }
        }

    @staticmethod
    def all_folders():
        """
        Получить список всех существубщих папок на сервере в БД
        """
        return {
            'request': 'GET',
            'object': 'FOLDER',
            'item': 'all'
        }

    @staticmethod
    def online_users():
        """
        Получить список клиентов подключенных к серверу
        """
        return {
            'request': 'GET',
            'object': 'USER',
            'item': 'online'
        }

    @staticmethod
    def registered_users():
        """
        Получить список зарегистрированых в БД клиентов
        """
        return {
            'request': 'GET',
            'object': 'USER',
            'item': 'registered'
        }

    @staticmethod
    def numbers_phones():
        """
        Получить список номеров телефонов в БД сервера
        """
        return {
            'request': 'GET',
            'object': 'PHONE',
            'item': 'all'
        }

    @staticmethod
    def param_api_sms():
        """
        Получить параметры api sms оповещений
        """
        return {
            'request': 'GET',
            'object': 'SMS_API',
            'item': 'all'
        }

    @staticmethod
    def icmp_params():
        """
        Получить список параметров Пингера
        """
        return {
            'request': 'GET',
            'object': 'PINGER',
            'item': 'params'
        }


class Post:

    @staticmethod
    def host(ip: str, name: str, id_folder: str, info: str, sms: int):
        """
        Отправить запрос на добавление хоста в БД
        :param ip : адрес хоста
        :param name: навание (любые символы)
        :param id_folder: ID папки в которую нужно добавить хост
        :param info: дополнительная информация (любые символы)
        :param sms: 0 или 1 (отправка sms при падении хоста)
        :return:
        """
        return {
            'request': 'POST',
            'object': 'HOST',
            'item': {
                'ip': ip,
                'name': name,
                'folder_id': id_folder,
                'info': info,
                'state': 'online',
                'sms': sms
            }
        }

    @staticmethod
    def folder(name: str):
        """
        Отправить запрос на добавление новой папки
        :param name: название папки (любые символы)
        :return:
        """
        return {
            'request': 'POST',
            'object': 'FOLDER',
            'item': {
                'name': name
            }
        }

    @staticmethod
    def user(login: str, passw: str, access: str):
        """
        Создать нового пользователя в БД
        :param login: логин пользователя (уникальный в БД)
        :param passw: пароль пользователя
        :param access: уроверь доступа Admin или Guest
        :return:
        """
        return {
            'request': 'POST',
            'object': 'USER',
            'item': {
                'login': login,
                'passw': passw,
                'access': access
            }
        }

    @staticmethod
    def phone(number: int, info: str):
        """
        Добавляет в БД сервера номер телефона для SMS сообщений.
        :param number: номер телефона (без + и прочитх символов, только цифры)
        :param info: инфа о номере
        :return:
        """
        return {
            'request': 'POST',
            'object': 'PHONE',
            'item': {
                'number': number,
                'info': info,
            }
        }


class Put:
    @staticmethod
    def host(ip, new_ip=None, name=None, id_folder=None, state=None, info=None, sms=None):
        """
        Изменить данные хоста по текущему IP адресу

        :param ip: Текущий IP адрес
        :param new_ip: Новый IP адрес
        :param name: Название
        :param id_folder: ID папки
        :param info: Поле информации
        :param sms: SMS рассылка
        :param state: Состояние
        :return:
        """
        return {
            'request': 'PUT',
            'object': 'HOST',
            'item': {
                'ip': ip,
                'new': {
                    'name': name,
                    'folder_id': id_folder,
                    'state': state,
                    'ip': new_ip,
                    'info': info,
                    'sms': sms
                }
            }
        }

    @staticmethod
    def folder(id_folder, new_id=None, name=None):
        """
        Изменить данные папки по текущему ID

        :param id_folder: Текущий ID папки
        :param new_id: Новый ID папки
        :param name: Название
        :return:
        """
        return {
            'request': 'PUT',
            'object': 'FOLDER',
            'item': {
                'folder_id': id_folder,
                'new': {
                    'name': name,
                    'folder_id': new_id
                }
            }
        }

    @staticmethod
    def user(login, new_login=None, passw=None, access=None):
        """
        Изменить логин, пароль и уровень прав пользователя

        :param login: Логин
        :param new_login: Новый Логин
        :param passw: Новый пароль
        :param access: Уровень прав (admin/guest)
        :return:
        """
        return {
            'request': 'PUT',
            'object': 'USER',
            'item': {
                'login': login,
                'new': {
                    'login': new_login,
                    'passw': passw,
                    'access': access
                }
            }
        }

    @staticmethod
    def sms_api(gateway=None, post_req=None, icmp_count=None):
        """
        Изменить параметры SMS рассылки

        :param gateway: URL адрес ресурса рассылки
        :param post_req: POST запрос в API ресурса рассылки
        :param icmp_count: Количество ICMP запросов на хост перед отправком SMS
        :return:
        """
        return {
            'request': 'PUT',
            'object': 'SMS_API',
            'item': {
                'gateway': gateway,
                'post_req': post_req,
                'icmp_count': icmp_count
            }
        }


class Delete:
    @staticmethod
    def host(ip):
        """
        Удалить хост
        :param ip: адрес хоста
        :return:
        """
        return {
            'request': 'DELETE',
            'object': 'HOST',
            'item': ip
        }

    @staticmethod
    def folder(id_folder: int):
        """
        Удалить папку
        :param id_folder:  id папки
        :return:
        """
        return {
            'request': 'DELETE',
            'object': 'FOLDER',
            'item': id_folder
        }

    @staticmethod
    def user(login: str):
        """
        Удалить пользователя
        :param login: Логин пользователя
        :return:
        """
        return {
            'request': 'DELETE',
            'object': 'USER',
            'item': login
        }

    @staticmethod
    def phone(number: int):
        """
        Удалить номер телефона
        :param number: номер телефона
        :return:
        """
        return {
            'request': 'DELETE',
            'object': 'PHONE',
            'item': number
        }


class Service:
    @staticmethod
    def ping_one_host(ip: str):
        """
        Проверить один хост по IP адресу
        :param ip: адресс хоста
        :return:
        """
        return {
            'request': 'SERVICE',
            'command': 20,
            'item': ip
        }

    @staticmethod
    def ping_all():
        """
        Запусть проверку всех хостов
        """
        return {
            'request': 'SERVICE',
            'command': 10,
            'item': None
        }

    @staticmethod
    def ping_dead():
        """
        Запусть проверку мертвых хостов
        """
        return {
            'request': 'SERVICE',
            'command': 21,
            'item': None
        }

    @staticmethod
    def shutdown_server():
        return {
            'request': 'SERVICE',
            'command': 30,
            'item': None
        }

    @staticmethod
    def hosts_check_per_sec(c: int):
        """
        Задать количество проверяемых хостов в единицу времени
        :param c: Количество проверяемых хостов в секунду
        :return:
        """
        return {
            'request': 'SERVICE',
            'command': 40,
            'item': c
        }

    @staticmethod
    def icmp_count_with_host(c: int):
        """
        Задать количество ICMP на один хост при проверке
        :param c: Количество ICMP
        :return:
        """
        return {
            'request': 'SERVICE',
            'command': 50,
            'item': c
        }

    @staticmethod
    def icmp_interval(c: int):
        """
        Задержка между ICMP запросами на хост
        :param c: Интервал в секундах
        :return:
        """
        return {
            'request': 'SERVICE',
            'command': 60,
            'item': c
        }

    @staticmethod
    def auto_ping_interval(c: int):
        """
        Задать интервал авто-проверки хостов
        :param c: Интервал в секундах
        :return:
        """
        return {
            'request': 'SERVICE',
            'command': 70,
            'item': c
        }

    @staticmethod
    def icmp_timeout(c: int):
        """
        Задать таймаут ICMP запроса
        :param c: таймаут в секундах
        :return:
        """
        return {
            'request': 'SERVICE',
            'command': 80,
            'item': c
        }

    @staticmethod
    def disconnect_user(login: str):
        """
        Запросить лог с сервера
        """
        return {
            'request': 'SERVICE',
            'command': 81,
            'item': login
        }

    @staticmethod
    def server_uptime():
        """
        Запросить uptime с сервера
        """
        return {
            'request': 'SERVICE',
            'command': 82,
            'item': 'uptime'
        }

    @staticmethod
    def log():
        """
        Запросить лог с сервера
        """
        return {
            'request': 'SERVICE',
            'command': 90,
            'item': None
        }


class DeilEyeAPI:
    def __init__(self, recv_log=None):
        self.IP = self.PORT = self.LOGIN = self.PASSW = None
        self.sock = None
        self.delay = 0  # задержка ответов от сервера
        self.tx = 0  # количетво принятых байт
        self.rx = 0  # количество отправленных байт
        self._recv_log = recv_log
        self._q = queue.Queue()

        self.get = Get()  # все GET запросы
        self.post = Post()  # все POST запросы
        self.put = Put()  # все Put запросы
        self.delete = Delete()  # все Delete запросы
        self.service = Service()  # все Service запросы

    def set_connect_data(self, ip, port, login, passw):
        """
        Установить ip,port,логин и пароль для подключения к серверу

        :param ip: Адрес сервера
        :param port: Порт сервера
        :param login: Логин пользователя
        :param passw: Пароль пользователя
        :return:
        """
        self.IP = ip
        self.PORT = port
        self.LOGIN = login
        self.PASSW = passw

    def set_connection(self):
        """
        Установить соединение с сервером

        :return: возращает состояние соединения в виде кода
        """

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.sock.settimeout(3)  # установка таймаута
        try:
            self.sock.connect((self.IP, self.PORT))
            if self._auth():
                packet = self._recv_()['response']
                if packet == 800:
                    return [packet]
                elif packet == 400:
                    return [packet]
                elif packet == 900:
                    return [packet]
            self.sock.close()
            return [20]

        except OSError:
            self.sock.close()
            return [30]
        except (Exception,):
            self.sock.close()
            return [10]

    def connection_close(self):
        """закрыть соединение"""
        self._q = queue.Queue()
        try:
            self.sock.close()
            del self.sock
        except AttributeError:
            return

    def _recv_offset(self, len_packet):
        # считывать буфер сокета операционной системы до тех пор,
        # пока нужное количество байт не будет собрано в пакет
        packet = b''
        while len(packet) < len_packet:
            try:
                data = self.sock.recv(len_packet - len(packet))
                if not data:
                    return
                packet += data
            except OSError:
                return
        return packet

    def _auth(self):
        return self._send_all({'login': self.LOGIN, 'password': self.PASSW})

    def _recv_(self):
        # возращает пакет переданный по tcp socket
        # в случае ошибки вернёт None
        try:
            t = time.time()

            header = self._recv_offset(4)
            len_packet = struct.unpack('<I', header)[0]
            packet = self._recv_offset(len_packet)
            delay = round((time.time()-t)*1000, 2)
            if delay > 1:
                self.delay = delay
            else:
                self.delay = '<1.0'

            self.rx += (len(packet) + 4) / 1_000_000  # счётчик принятых байт
            return json.loads(zlib.decompress(packet))
        except struct.error:
            print('ошибка модуля Struct: def recv')
            return
        except TypeError:
            print('ошибка TypeErr: def recv')
            return
        except (Exception,):
            print('непонятная ошибка надо искать: def _recv_')
            return

    def _send_all(self, msg):
        msg = zlib.compress(json.dumps(msg).encode('utf-8'))
        try:
            header = struct.pack('<I', len(msg))
            self.sock.sendall(header + msg)
            self.tx += (len(msg) + 4) / 1_000_000  # счётчик отправленных байт
            return True
        except (OSError, TypeError, struct.error, AttributeError):
            return

    def _api_handler(self, resp):
        if resp:
            try:
                while True:
                    code = resp['response']
                    data = resp['data']
                    if code == 33:
                        self._q.put(data)
                        resp = self._recv_()
                        continue
                    return [code, data]
            except (Exception,):
                return [10]
        return [30]

    def GetLogQueue(self):
        """
        Получить логи накопленные в очереди
        """
        log = []
        while True:
            try:
                log.append(self._q.get_nowait())
            except queue.Empty:
                break
        return log

    def GetAllHosts(self):
        """
        Получить список всех хостов
        """
        self._send_all(self.get.all_hosts())
        resp = self._recv_()
        return self._api_handler(resp)

    def GetOneHost(self, ip):
        """
        Получить информацию о хосте по IP
        """
        self._send_all(self.get.one_host(ip))
        resp = self._recv_()
        return self._api_handler(resp)

    def GetDeadHosts(self):
        """
        Получить список мертвых хостов
        """
        self._send_all(self.get.dead_hosts())
        resp = self._recv_()
        return self._api_handler(resp)

    def GetLiveHosts(self):
        """
        Получить список живых хостов
        """
        self._send_all(self.get.live_hosts())
        resp = self._recv_()
        return self._api_handler(resp)

    def GetPauseHosts(self):
        """
        Получить список хостов на паузе
        """
        self._send_all(self.get.pause_hosts())
        resp = self._recv_()
        return self._api_handler(resp)

    def GetHostsWithFolder(self, id_folder):
        """
        Получить список хостов в определённой папке
        """
        self._send_all(self.get.folder_with_hosts(id_folder))
        resp = self._recv_()
        return self._api_handler(resp)

    def GetAllFolders(self):
        """
        Получить список папок
        """
        self._send_all(self.get.all_folders())
        resp = self._recv_()
        return self._api_handler(resp)

    def GetOnlineUsers(self):
        """
        Получить список пользователей подключенных к серверу
        """
        self._send_all(self.get.online_users())
        resp = self._recv_()
        return self._api_handler(resp)

    def GetRegUsers(self):
        """
        Получить список пользователей в БД
        """
        self._send_all(self.get.registered_users())
        resp = self._recv_()
        return self._api_handler(resp)

    def GetNumbersPhones(self):
        """
        Получить номера телефонов SMS рассылки
        """
        self._send_all(self.get.numbers_phones())
        resp = self._recv_()
        return self._api_handler(resp)

    def GetParamsApiSms(self):
        self._send_all(self.get.param_api_sms())
        resp = self._recv_()
        return self._api_handler(resp)

    def GetParamsICMP(self):
        self._send_all(self.get.icmp_params())
        resp = self._recv_()
        return self._api_handler(resp)

    def CreatePhone(self, number, info):
        self._send_all(self.post.phone(number, info))
        resp = self._recv_()
        return self._api_handler(resp)

    def CreateHost(self, ip, id_folder, name, info=''):
        self._send_all(self.post.host(ip, name, id_folder, info=info, sms=0))
        resp = self._recv_()
        return self._api_handler(resp)

    def CreateFolder(self, name: str):
        self._send_all(self.post.folder(name))
        resp = self._recv_()
        return self._api_handler(resp)

    def CreateUser(self, login, passw, access):
        self._send_all(self.post.user(login, passw, access))
        resp = self._recv_()
        return self._api_handler(resp)

    def PutHost(self, ip, new_ip=None, name=None, id_folder=None, state=None, info=None, sms=None):
        self._send_all(self.put.host(ip, new_ip, name, id_folder, state, info, sms))
        resp = self._recv_()
        return self._api_handler(resp)

    def PutFolder(self, id_folder, new_id=None, name=None):
        self._send_all(self.put.folder(id_folder, new_id, name))
        resp = self._recv_()
        return self._api_handler(resp)

    def PutUser(self, login, new_login=None, passw=None, access=None):
        self._send_all(self.put.user(login, new_login, passw, access))
        resp = self._recv_()
        return self._api_handler(resp)

    def PutSmsApi(self, gateway=None, post_req=None, icmp_count=None):
        self._send_all(self.put.sms_api(gateway, post_req, icmp_count))
        resp = self._recv_()
        return self._api_handler(resp)

    def DeleteHost(self, ip):
        self._send_all(self.delete.host(ip))
        resp = self._recv_()
        return self._api_handler(resp)

    def DeleteFolder(self, id_folder):
        self._send_all(self.delete.folder(id_folder))
        resp = self._recv_()
        return self._api_handler(resp)

    def DeleteUser(self, login):
        self._send_all(self.delete.user(login))
        resp = self._recv_()
        return self._api_handler(resp)

    def DeletePhone(self, number):
        self._send_all(self.delete.phone(number))
        resp = self._recv_()
        return self._api_handler(resp)

    def PingALL(self):
        self._send_all(self.service.ping_all())
        resp = self._recv_()
        return self._api_handler(resp)

    def PingONE(self, ip):
        self._send_all(self.service.ping_one_host(ip))
        resp = self._recv_()
        return self._api_handler(resp)

    def PingDEAD(self):
        self._send_all(self.service.ping_dead())
        resp = self._recv_()
        return self._api_handler(resp)

    def ShutdownServer(self):
        self._send_all(self.service.shutdown_server())
        resp = self._recv_()
        return self._api_handler(resp)

    def AutoPingInterval(self, interval):
        self._send_all(self.service.auto_ping_interval(interval))
        resp = self._recv_()
        return self._api_handler(resp)

    def ICMPInterval(self, interval):
        self._send_all(self.service.icmp_interval(interval))
        resp = self._recv_()
        return self._api_handler(resp)

    def ICMPTimeout(self, timeout):
        self._send_all(self.service.icmp_timeout(timeout))
        resp = self._recv_()
        return self._api_handler(resp)

    def CheckedHostPerSecond(self, count):
        self._send_all(self.service.hosts_check_per_sec(count))
        resp = self._recv_()
        return self._api_handler(resp)

    def ICMPWithHost(self, count):
        self._send_all(self.service.icmp_count_with_host(count))
        resp = self._recv_()
        return self._api_handler(resp)

    def GetLog(self):
        self._send_all(self.service.log())
        resp = self._recv_()
        return self._api_handler(resp)

    def DisconnectUser(self, login):
        self._send_all(self.service.disconnect_user(login))
        resp = self._recv_()
        return self._api_handler(resp)

    def GetDelayServer(self):
        """получить задержку ответов от сервера"""
        return self.delay

    def GetRxBytes(self):
        """получить кол-во принятых байт"""
        return round(self.rx, 3)

    def GetTxBytes(self):
        """получить кол-во отправленных байт"""
        return round(self.tx, 3)

    def GetServerUptime(self):
        """получить время работы сервера"""
        self._send_all(self.service.server_uptime())
        resp = self._recv_()
        return self._api_handler(resp)








