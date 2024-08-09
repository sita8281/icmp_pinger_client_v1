import tkinter as tk
from tkinter import filedialog
import pickle
from tkinter import ttk
from tkinter import messagebox
from api_server import DeilEyeAPI
from datetime import datetime
import webbrowser
import os
import csv
import json


def save_temp_data(login=None, server=None, check1=None, check2=None, check3=None):
    """
    Сохранить логин и IP сервера в файл.
    """
    obj = load_temp_data()
    if obj:
        with open(file='temp_data.data', mode='wb') as file:
            if login:
                obj['login'] = login
            if server:
                obj['server'] = server
            if check1 is True or check1 is False:
                obj['check1'] = check1
            if check2 is True or check2 is False:
                obj['check2'] = check2
            if check3 is True or check3 is False:
                obj['check3'] = check3
            pickle.dump(obj, file)
            print(obj)


def load_temp_data():
    """
    Получить логин и IP сервера из файла.
    """
    try:
        with open(file='temp_data.data', mode='rb') as file:
            obj = pickle.load(file)
            return obj
    except (Exception,):
        pass


def center_window(p, width, height):
    screen_width = p.winfo_screenwidth()
    screen_height = p.winfo_screenheight()
    win_width = width
    win_height = height
    x_coordinate = int((screen_width / 2) - (win_width / 2))
    y_coordinate = int((screen_height / 2) - (win_height / 2))
    return f'{win_width}x{win_height}+{x_coordinate}+{y_coordinate}'


def center_window_adaptive(p, width, height):
    screen_width = p.winfo_screenwidth()
    screen_height = p.winfo_screenheight()
    win_width = int(width*(screen_width / 1920))
    win_height = int(height*(screen_height / 1080))
    x_coordinate = int((screen_width / 2) - (win_width / 2))
    y_coordinate = int((screen_height / 2) - (win_height / 2))
    return f'{win_width}x{win_height}+{x_coordinate}+{y_coordinate}'


def handler_status_codes(parent, status, show=None, reconnect=True, special_reconnect=None):
    """
    Обработчик статус-кодов из API.
    Выводит messagebox с информацией соответствующей статус-коду.

    :param parent: родительское окно или виджет
    :param status: код статуса ответа
    :param show: какой тип статусов отображать ('bad', 'good', 'all')
    :param reconnect: переподключаться при ошибке соединения
    :return:
    """

    if status == 100:
        if show == 'bad' or show == 'all':
            tk.messagebox.showwarning('Неправильный запрос', 'Сервер не обработал ваш запрос', parent=parent)
        return

    elif status == 200:
        if show == 'good' or show == 'all':
            tk.messagebox.showinfo('Информация', 'Запрос успешно обработан и выполнен на сервере', parent=parent)
        return 1

    elif status == 300:
        if show == 'bad' or show == 'all':
            tk.messagebox.showwarning('Информация', 'Объект к которому вы обращаетесь не существует', parent=parent)
        return

    elif status == 400:
        if show == 'bad' or show == 'all':
            tk.messagebox.showwarning('Ошибка авторизации', 'Неверный логин или пароль', parent=parent)
        return

    elif status == 500:
        if show == 'bad' or show == 'all':
            tk.messagebox.showwarning('Ошибка сервера', 'При обработке запроса на сервере произошла ошибка',
                                      parent=parent)
        return

    elif status == 600:
        if show == 'bad' or show == 'all':
            tk.messagebox.showerror('Нет прав', 'У вас не достаточно прав для выполнения этого запроса',
                                    parent=parent)
        return

    elif status == 700:
        if show == 'bad' or show == 'all':
            tk.messagebox.showwarning('Информация', 'Объект с таким ID, Логином или IP уже существует',
                                      parent=parent)
        return

    elif status == 800:
        if show == 'good' or show == 'all':
            tk.messagebox.showinfo('Информация', 'Авторизация на сервере прошла успешно', parent=parent)
        return 1

    elif status == 900:
        if show == 'bad' or show == 'all':
            tk.messagebox.showwarning('Ошибка авторизации', 'Ваш клиент не успел подключиться к серверу',
                                      parent=parent)
        return

    elif status == 10:
        if special_reconnect:
            parent = app.server_connection_lost()
            tk.messagebox.showwarning('Generic Error', 'Сбой TCP-сокета.', parent=parent)
        return

    elif status == 30 or status == 20:
        if reconnect:
            parent = app.server_connection_lost()
            tk.messagebox.showwarning('Ошибка соединения', 'Соединение с сервером потеряно', parent=parent)
            return
        elif special_reconnect:
            tk.messagebox.showwarning('Ошибка соединения', 'Сервер не отвечает или не доступен', parent=parent)
            return
    else:
        app.stop_afters = True
        tk.messagebox.showerror('Unknown Error', 'Неизвестная ошибка. Перезапустите программу.', parent=parent)
        app.destroy()
        return


class EntryWithMenu(ttk.Entry):
    """
    Обычный Entry виджет наследованный от ttk.Entry
    Добавлено простое меню: копировать, ставить и вырезать
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bind('<Button-3>', self.open_menu)
        self.menu = tk.Menu(tearoff=0)
        self.menu.add_command(label='Копировать', command=self.copy)
        self.menu.add_command(label='Вставить', command=self.paste)
        self.menu.add_command(label='Вырезать', command=self.cut)

    def open_menu(self, e):
        self.menu.post(e.x_root, e.y_root)

    def copy(self):
        try:
            if self.selection_present():
                f_sel = self.index('sel.first')
                l_sel = self.index('sel.last')
                self.clipboard_clear()
                get = self.get()
                self.clipboard_append(get[f_sel:l_sel])
                return f_sel, l_sel
        except (tk.TclError, Exception):
            pass

    def paste(self):
        try:
            pst = self.clipboard_get()
            if pst:
                if self.selection_present():
                    f_sel = self.index('sel.first')
                    l_sel = self.index('sel.last')
                    self.delete(f_sel, l_sel)
                    self.insert(f_sel, pst)
                else:
                    indx = self.index('insert')
                    self.insert(indx, pst)
        except tk.TclError:
            pass

    def cut(self):
        sel = self.copy()
        if sel:
            self.delete(sel[0], sel[1])


class LogText(tk.Text):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.auto_scroll = tk.BooleanVar()
        self.auto_scroll.set(True)

        self.bind('<Button-3>', self.open_menu)
        self.menu = tk.Menu(tearoff=0)
        self.menu.add_command(label='Копировать', command=self.copy)
        self.menu.add_command(label='Очистить', command=self.clear)
        self.menu.add_checkbutton(label='Автопрокрутка', variable=self.auto_scroll)

    def open_menu(self, e):
        self.menu.post(e.x_root, e.y_root)

    def copy(self):
        try:
            txt = self.selection_get()
            self.clipboard_clear()
            self.clipboard_append(txt)
        except tk.TclError:
            return

    def cut(self):
        try:
            txt = self.selection_get()
            self.clipboard_clear()
            self.clipboard_append(txt)
            index1 = self.index(tk.SEL_FIRST)
            index2 = self.index(tk.SEL_LAST)
            self.delete(index1, index2)
        except tk.TclError:
            return

    def clear(self):
        self['state'] = tk.NORMAL
        self.delete('1.0', tk.END)
        self['state'] = tk.DISABLED

    def paste(self):
        try:
            self.selection_get()
            index1 = self.index(tk.SEL_FIRST)
            index2 = self.index(tk.SEL_LAST)
            self.delete(index1, index2)
            self.insert(index1, self.clipboard_get())
        except tk.TclError:
            try:
                self.insert(self.index(tk.INSERT), self.clipboard_get())
            except tk.TclError:
                return


class InfoText(LogText):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs, font=('Segoe UI', 9))

        self.menu = tk.Menu(tearoff=0)
        self.menu.add_command(label='Копировать', command=self.copy)
        self.menu.add_command(label='Очистить', command=self.clear)
        self.menu.add_command(label='Вырезать', command=self.cut)
        self.menu.add_command(label='Вставить', command=self.paste)


class AuthorizedWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self._call = parent.run_loop
        self.grab_set()
        # self.iconphoto(True, tk.PhotoImage(file='icons/key.png'))
        self.api = api
        self.default_tcp_port = 2323
        self.parent.withdraw()
        self.title('Подключение к серверу')
        self.resizable(False, False)
        self.geometry(center_window(self, 400, 260))
        self.protocol('WM_DELETE_WINDOW', self.close_parent)
        self.bind('<KeyPress-Return>', self.connect_to_server)

        self.info_label = ttk.Label(self, text='Для подключения к серверу авторизуйтесь')
        self.login_label = ttk.Label(self, text='Логин:')
        self.passw_label = ttk.Label(self, text='Пароль:')
        self.server_label = ttk.Label(self, text='Сервер:')

        self.canvas = tk.Canvas(self, height=100, width=400, bg='red', highlightthickness=0)
        self.img = tk.PhotoImage(file='icons/authorized.png')
        self.image = self.canvas.create_image(0, 0, anchor='nw', image=self.img)

        self.login = EntryWithMenu(self, width=40)
        self.passw = EntryWithMenu(self, width=40, show='*')
        self.server = EntryWithMenu(self, width=40)

        temp_data = load_temp_data()
        if temp_data:
            self.login.insert(tk.END, temp_data['login'])
            self.server.insert(tk.END, temp_data['server'])

        self.connect_button = ttk.Button(self, text='Подключиться', command=self.connect_to_server)

        self.canvas.grid(row=0, column=0, columnspan=3)
        self.info_label.grid(row=1, column=0, pady=5, padx=10, columnspan=3)
        self.login_label.grid(row=2, column=0, pady=4, padx=10)
        self.passw_label.grid(row=3, column=0, pady=4, padx=10)
        self.server_label.grid(row=4, column=0, pady=4, padx=10)
        self.login.grid(row=2, column=1, pady=4)
        self.passw.grid(row=3, column=1, pady=4)
        self.server.grid(row=4, column=1, pady=4)
        self.connect_button.grid(row=5, column=1, pady=6, sticky='e')

    def connect_to_server(self, e=None):
        login = self.login.get()
        passw = self.passw.get()
        serv = self.server.get()
        save_srv = serv

        if ':' in serv:
            serv = serv.split(':')

        else:
            serv = f'{serv}:{self.default_tcp_port}'
            serv = serv.split(':')

        self.api.set_connect_data(serv[0], int(serv[1]), login, passw)
        status = self.api.set_connection()
        if status:
            if handler_status_codes(self, status[0], 'bad', reconnect=False, special_reconnect=True):
                self.close_self_and_open_parent()
                save_temp_data(login, save_srv)
                self.parent.current_user.set(login)

    def close_parent(self):
        self.parent.destroy()

    def close_self_and_open_parent(self):
        """закрывает себя, и разворачивает главное окно"""
        self.destroy()
        self.parent.deiconify()
        self._call()
        self.parent.monitoring_frame.folder_list.select_all_hosts()


class TableHostsLite(tk.Frame):
    """Окно со списком хостов"""
    def __init__(self, parent):
        super().__init__(parent)
        self.tree = ttk.Treeview(self, columns=('name', 'ip'),
                                 height=15, selectmode='browse', style='q.Treeview', takefocus=False)
        self.perent = parent

        # стилизация Treeview и установка размера одного элемента на 19 пикс.
        s = ttk.Style()
        s.configure('q.Treeview', rowheight=19)

        # скролл-бары
        self.scroll = ttk.Scrollbar(self, orient='vertical', command=self.tree.yview)
        self.scroll_x = ttk.Scrollbar(self, orient='horizontal', command=self.tree.xview)
        self.tree.configure(yscrollcommand=self.adaptive_scroller,
                            xscrollcommand=self.adaptive_scroller_x)

        # колонки (столбцы) списка
        self.tree.column('#0', stretch=False, width=50)
        self.tree.column('name', minwidth=300, anchor='w')
        self.tree.column('ip', stretch=False, width=120, anchor='w', minwidth=120)

        # названия колонок списка
        sort_name = self.sort_name_generator(0)
        self.tree.heading('name', text='Name', command=lambda: sort_name.__next__())
        sort_ip = self.sort_name_generator(1)
        self.tree.heading('ip', text='IP address', command=lambda: sort_ip.__next__())

        # теги для присваивания иконки состояния хосту
        self.img_server = tk.PhotoImage(file='icons/server16x16.png')
        self.tree.tag_configure('server', image=self.img_server)

        # расстоновка всех виджетов (скролл_x, скролл_y, treeview)
        self.tree.grid(row=0, column=0, sticky='nsew')
        self.scroll.grid(row=0, column=1, sticky='ns')
        self.scroll_x.grid(row=1, column=0, sticky='we')

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

    def adaptive_scroller(self, a, b):
        """Scroll_Y вызвает этот метод, при любом изменении размера виджета,
        или изменении количества находящихся в нём элементов.
        Нужен для авто-скрытия scroll-баров, когда в них нет нужды"""

        self.scroll.set(a, b)
        if float(b) == 1.0 and float(a) == 0.0:
            self.scroll.grid_remove()
        else:
            self.scroll.grid(row=0, column=1, sticky='ns')

    def adaptive_scroller_x(self, a, b):
        """Scroll_X вызвает этот метод, при любом изменении размера виджета,
        или изменении количества находящихся в нём элементов.
        Нужен для авто-скрытия scroll-баров, когда в них нет нужды"""

        self.scroll_x.set(a, b)
        if float(b) == 1.0 and float(a) == 0.0:
            self.scroll_x.grid_remove()
        else:
            self.scroll_x.grid(row=1, column=0, sticky='we')

    def sort_name_generator(self, sort):
        """генератор для сортировки элементов в списке"""
        revers = False
        while True:
            sorted_iids = []
            all_iids = self.tree.get_children()

            for iid in all_iids:
                name = self.tree.item(item=iid)['values']
                sorted_iids.append([str(name[sort]).lower(), iid])

            sorted_iids = sorted(sorted_iids, key=lambda s: s[0], reverse=revers)

            for count, i in enumerate(sorted_iids):
                name, iid = i
                self.tree.move(iid, '', count)

            if revers:
                revers = False
                self._change_trianle_heading(sort, '▲')
            else:
                self._change_trianle_heading(sort, '▼')
                revers = True
            yield

    def _change_trianle_heading(self, heading, symbol_utf):
        """изменить, переместить треугольник в списке, на кнопках сортировки"""
        self._delete_triangle_heading()  # убрать треугольник со всех кнопок
        if heading == 0:
            self.tree.heading('name', text=f'Name   {symbol_utf}')
        elif heading == 1:
            self.tree.heading('ip', text=f'IP address   {symbol_utf}')

    def _delete_triangle_heading(self):
        """убрать все треугольники сортировки с кнопок сортировки"""
        self.tree.heading('name', text='Name')
        self.tree.heading('ip', text='IP address')


class TableHosts(tk.Frame):
    """Список-таблица хостов"""
    def __init__(self, parent):
        super().__init__(parent, bd=2)

        self.selected_folder = None

        # загрузка икононок состояний хостов
        self.img_pause = tk.PhotoImage(file='icons/pause1.png')
        self.img_good = tk.PhotoImage(file='icons/icmp_good.png')
        self.img_bad = tk.PhotoImage(file='icons/icmp_bad.png')
        self.img_clock = tk.PhotoImage(file='icons/clock.png')
        self.img_delete = tk.PhotoImage(file='icons/cross16x16.png')
        self.img_add = tk.PhotoImage(file='icons/add16x16.png')
        self.img_web = tk.PhotoImage(file='icons/web.png')
        self.img_ping = tk.PhotoImage(file='icons/ping.png')
        self.img_telnet = tk.PhotoImage(file='icons/telnet.png')
        self.img_copy = tk.PhotoImage(file='icons/copy.png')
        self.img_pause_menu = tk.PhotoImage(file='icons/pause_menu.png')
        self.img_play = tk.PhotoImage(file='icons/play.png')

        self.menu = tk.Menu(tearoff=0)
        self.menu.add_command(label='  Открыть в браузере', image=self.img_web, compound='left',
                              command=self.open_browser)
        self.menu.add_command(label='  Запустить пинг (32 Байт)', compound='left', image=self.img_ping,
                              command=self.open_cmd_ping)
        self.menu.add_command(label='  Запустить пинг (50000 Байт)', compound='left', image=self.img_ping,
                              command=self.open_cmd_ping_max_size)
        self.menu.add_command(label='  Запустить пинг (свои параметры)', compound='left', image=self.img_ping,
                              command=self.open_cmd_ping_advanced)
        self.menu.add_command(label='  Подключиться по Telnet', compound='left', image=self.img_telnet,
                              command=self.open_cmd_telnet)
        self.menu.add_separator()
        self.menu.add_command(label='  Создать хост', compound='left', image=self.img_add,
                              command=lambda: CreateHostWindow(app))
        self.menu.add_command(label='  Удалить хост', compound='left', image=self.img_delete,
                              command=self.delete_host_in_server)
        self.menu.add_command(label='  Поставить на паузу', compound='left', image=self.img_pause_menu,
                              command=self.set_pause_host)
        self.menu.add_command(label='  Снять с паузы', compound='left', image=self.img_play,
                              command=self.set_play_host)
        self.menu.add_separator()
        self.menu.add_command(label='  Копировать IP', compound='left', image=self.img_copy,
                              command=self.copy_ip)
        self.menu.add_command(label='  Копировать название', compound='left', image=self.img_copy,
                              command=self.copy_name)

        # таблица-список хостов
        self.tree = ttk.Treeview(self, columns=('name', 'ip', 'date', 'time', 'notify'),
                                 height=30, selectmode='browse', style='q.Treeview', takefocus=False)

        # стилизация Treeview и установка размера одного элемента на 19 пикс.
        s = ttk.Style()
        s.configure('q.Treeview', rowheight=19)

        # скролл-бары
        self.scroll = ttk.Scrollbar(self, orient='vertical', command=self.tree.yview)
        self.scroll_x = ttk.Scrollbar(self, orient='horizontal', command=self.tree.xview)
        self.tree.configure(yscrollcommand=self.adaptive_scroller,
                            xscrollcommand=self.adaptive_scroller_x)

        # вызов метода при нажатии на хост
        self.tree.bind('<<TreeviewSelect>>', self.select_item)
        self.tree.bind('<Button-3>', self.select_item_btn3)
        self.tree.tag_bind('offline', '<Double-Button-1>', self.ping_host)
        self.tree.tag_bind('online', '<Double-Button-1>', self.ping_host)
        self.tree.tag_bind('clock.offline', '<Double-Button-1>', self.ping_host)
        self.tree.tag_bind('clock.online', '<Double-Button-1>', self.ping_host)
        self.tree.tag_bind('clock', '<Double-Button-1>', self.ping_host)

        # колонки (столбцы) списка
        self.tree.column('#0', stretch=False, width=50)
        self.tree.column('name', minwidth=300, anchor='w')
        self.tree.column('ip', stretch=False, width=120, anchor='w', minwidth=120)
        self.tree.column('date', width=20, anchor='w', minwidth=120)
        self.tree.column('time', width=20, anchor='w', minwidth=130)
        self.tree.column('notify', width=20, anchor='w', minwidth=100)

        # названия колонок списка
        sort_name = self.sort_name_generator(0)
        self.tree.heading('name', text='Name', command=lambda: sort_name.__next__())
        sort_ip = self.sort_name_generator(1)
        self.tree.heading('ip', text='IP address', command=lambda: sort_ip.__next__())
        sort_date = self.sort_name_generator(2)
        self.tree.heading('date', text='Дата изменения', command=lambda: sort_date.__next__())
        sort_time = self.sort_name_generator(3)
        self.tree.heading('time', text='Время изменения', command=lambda: sort_time.__next__())
        sort_notify = self.sort_name_generator(4)
        self.tree.heading('notify', text='Оповещения', command=lambda: sort_notify.__next__())

        # теги для присваивания иконки состояния хосту
        self.tree.tag_configure('offline', image=self.img_bad)  # хост не в сети
        self.tree.tag_configure('clock.offline', image=self.img_clock)  # хост проверяется
        self.tree.tag_configure('online', image=self.img_good)  # хост в сети
        self.tree.tag_configure('clock.online', image=self.img_clock)  # хост проверяется
        self.tree.tag_configure('pause', image=self.img_pause)  # хост на паузе
        self.tree.tag_configure('clock', image=self.img_clock)  # хост проверяется

        # расстоновка всех виджетов (скролл_x, скролл_y, treeview)
        self.tree.grid(row=0, column=0, sticky='nsew')
        self.scroll.grid(row=0, column=1, sticky='ns')
        self.scroll_x.grid(row=1, column=0, sticky='we')

        # параметры расстягивания колонок и строк Treeview
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

    def copy_ip(self):
        item = self.tree.selection()
        if item:
            self.clipboard_clear()
            self.clipboard_append(item[0])

    def copy_name(self):
        item = self.tree.selection()
        if item:
            self.clipboard_clear()
            self.clipboard_append(self.tree.item(item[0])['values'][0])

    def open_cmd_ping(self):
        item = self.tree.selection()
        if item:
            os.system(f"cmd.exe /c start ping {item[0]} -t")

    def open_cmd_ping_max_size(self):
        item = self.tree.selection()
        if item:
            os.system(f"cmd.exe /c start ping {item[0]} -t -l 50000")

    def open_cmd_telnet(self):
        item = self.tree.selection()
        if item:
            os.system(f"cmd.exe /c start telnet {item[0]}")

    def open_cmd_ping_advanced(self):
        item = self.tree.selection()
        if item:
            PingAdvanced(app, item[0])

    def open_browser(self):
        item = self.tree.selection()
        if item:
            try:
                webbrowser.open(f'http://{item[0]}', new=2)
            except webbrowser.Error:
                return

    def select_item_btn3(self, e):
        """выделить элемент при нажатии на него ПКМ"""
        item = self.tree.identify_row(e.y)
        if item:
            self.tree.selection_set(item)
            self.open_menu(e)

    def open_menu(self, e):
        print(e)
        self.menu.post(e.x_root, e.y_root)

    def set_pause_host(self):
        """Поставить хост на паузу"""
        host = self.tree.selection()
        if host:
            resp = api.PutHost(*host, state='pause')  # запрос на сервер
            if handler_status_codes(app, resp[0], reconnect=False):
                app.monitoring_frame.host_info.update_data(*host)
        else:
            tk.messagebox.showwarning('Хост не выбран', 'Чтобы отключить ICMP-проверку хоста, его нужно выбрать')

    def set_play_host(self):
        """Убрать хост с паузы"""
        host = self.tree.selection()
        if host:
            resp = api.PutHost(*host, state='offline')  # запрос на сервер
            if handler_status_codes(app, resp[0], reconnect=False):
                app.monitoring_frame.host_info.update_data(*host)
                api.PingONE(*host)
        else:
            tk.messagebox.showwarning('Хост не выбран', 'Чтобы включить ICMP-проверку хоста, его нужно выбрать')

    def ping_host(self, e=None):
        """отправить запрос на сервер для пинга выбранного хоста"""
        host = self.tree.selection()
        if host:
            api.PingONE(*host)   # запрос на сервер (в этом случае без response-обработчика)

    def adaptive_scroller(self, a, b):
        """Scroll_Y вызвает этот метод, при любом изменении размера виджета,
        или изменении количества находящихся в нём элементов.
        Нужен для авто-скрытия scroll-баров, когда в них нет нужды"""

        self.scroll.set(a, b)
        if float(b) == 1.0 and float(a) == 0.0:
            self.scroll.grid_remove()
        else:
            self.scroll.grid(row=0, column=1, sticky='ns')

    def adaptive_scroller_x(self, a, b):
        """Scroll_X вызвает этот метод, при любом изменении размера виджета,
        или изменении количества находящихся в нём элементов.
        Нужен для авто-скрытия scroll-баров, когда в них нет нужды"""

        self.scroll_x.set(a, b)
        if float(b) == 1.0 and float(a) == 0.0:
            self.scroll_x.grid_remove()
        else:
            self.scroll_x.grid(row=1, column=0, sticky='we')

    def show_hosts(self, folder_id):

        if folder_id == 'all':
            items = api.GetAllHosts()
            self.selected_folder = (None, api.GetAllHosts)
        elif folder_id == 'live':
            items = api.GetLiveHosts()
            self.selected_folder = (None, api.GetLiveHosts)
        elif folder_id == 'dead':
            items = api.GetDeadHosts()
            self.selected_folder = (None, api.GetDeadHosts)
        elif folder_id == 'pause':
            items = api.GetPauseHosts()
            self.selected_folder = (None, api.GetPauseHosts)
        elif folder_id:
            items = api.GetHostsWithFolder(folder_id)
            self.selected_folder = (folder_id, api.GetHostsWithFolder)
        else:
            return

        if items:
            if handler_status_codes(app, items[0], show='bad', reconnect=False):
                self.insert_items(items[1])
                return
            self.selected_folder = None

    def delete_hosts(self):
        """очистить treeview"""
        self.tree.delete(*self.tree.get_children())
        self._delete_triangle_heading()  # удаление треугольников с сортировок

    def insert_items(self, items):
        """добавление хостов  в treeview"""
        self.delete_hosts()
        for item in items:
            ip, name, folder, state, timestamp, _, notify = item
            if notify:
                notify = 'Вкл.'
            else:
                notify = 'Выкл.'
            time_change = datetime.fromtimestamp(int(timestamp)).strftime('%H:%M:%S')
            date_change = datetime.fromtimestamp(int(timestamp)).strftime('%Y-%m-%d')
            self.tree.insert('', iid=ip, index=tk.END, values=(name, ip, date_change, time_change, notify,),
                             tags=(state, 'event_double_click'))

    def update_hosts(self):
        """Цикл обновления данных в таблице, интервал 1 сек"""
        if app.stop_afters:
            return
        if self.selected_folder:
            get_hosts_callback = self.selected_folder[1]
            id_folder = self.selected_folder[0]
        else:
            app.after_call_folders = self.after(1000, self.update_hosts)
            return

        # получение из API задержки ответов сервера
        app.delay_server.set(api.GetDelayServer())
        # получение из API кол-во принятых байт
        app.rx_bytes.set(api.GetRxBytes())
        # получение из API кол-во отправленных байт
        app.tx_bytes.set(api.GetTxBytes())
        # получение из API время работы сервера
        response = api.GetServerUptime()
        if handler_status_codes(app, response[0], reconnect=False):
            app.uptime.set(response[1])

        if id_folder:
            hosts = get_hosts_callback(id_folder)
        else:
            hosts = get_hosts_callback()

        if handler_status_codes(app, hosts[0]):
            hosts = hosts[1]
            if hosts:
                hosts_in_tree = self.tree.get_children()
                flag = False
                for host in hosts_in_tree:
                    for host1 in hosts:
                        if host == host1[0]:
                            flag = False
                            break
                        else:
                            flag = True
                    if flag:
                        self.tree.delete(host)
                for item in hosts:
                    ip, name, folder, state, timestamp, _, notify = item
                    time_change = datetime.fromtimestamp(int(timestamp)).strftime('%H:%M:%S')
                    date_change = datetime.fromtimestamp(int(timestamp)).strftime('%Y-%m-%d')

                    if notify:
                        notify = 'Вкл.'
                    else:
                        notify = 'Выкл.'

                    filter_str = app.monitoring_frame.get_filter()

                    if self.tree.exists(ip):
                        self.tree.item(ip, values=(name, ip, date_change, time_change, notify,), tags=(state,))
                    else:
                        self.tree.insert('', iid=ip, index=tk.END,
                                         values=(name, ip, date_change, time_change, notify,),
                                         tags=(state,))

                    # фильтрация хостов по вводимым значениям
                    if filter_str:
                        for i in self.tree.get_children():
                            if str(filter_str).lower() in str(self.tree.item(i)['values'][0]).lower():
                                pass
                            else:
                                self.tree.delete(i)

            else:
                self.tree.delete(*self.tree.get_children())
        app.after_call_folders = self.after(1000, self.update_hosts)

    def delete_host_in_server(self):
        """удалить выбранный хост из БД сервера"""
        host = self.tree.selection()
        if host:
            name_host = self.tree.item(host[0])['values'][0]
            ask = tk.messagebox.askyesno('Удаление хоста', f'Вы уверены что хотите удалить хост: "{name_host}"?\n')
            if ask:
                response = api.DeleteHost(*host)
                handler_status_codes(app, response[0], show='good', reconnect=False)
        else:
            tk.messagebox.showwarning('Хост не выбран', 'Выберите хост из списка, чтобы его удалить')

    def select_item(self, e):
        """вызывается при нажатии на хост"""
        host = self.tree.selection()
        if host:
            app.monitoring_frame.host_info.insert_data(*host)

    def sort_name_generator(self, sort):
        """генератор для сортировки элементов в списке"""
        revers = False
        while True:
            sorted_iids = []
            all_iids = self.tree.get_children()

            for iid in all_iids:
                name = self.tree.item(item=iid)['values']
                sorted_iids.append([str(name[sort]).lower(), iid])

            sorted_iids = sorted(sorted_iids, key=lambda s: s[0], reverse=revers)

            for count, i in enumerate(sorted_iids):
                name, iid = i
                self.tree.move(iid, '', count)

            if revers:
                revers = False
                self._change_trianle_heading(sort, '▲')
            else:
                self._change_trianle_heading(sort, '▼')
                revers = True
            yield

    def _change_trianle_heading(self, heading, symbol_utf):
        """изменить, переместить треугольник в списке, на кнопках сортировки"""
        self._delete_triangle_heading()  # убрать треугольник со всех кнопок
        if heading == 0:
            self.tree.heading('name', text=f'Name   {symbol_utf}')
        elif heading == 1:
            self.tree.heading('ip', text=f'IP address   {symbol_utf}')
        elif heading == 2:
            self.tree.heading('date', text=f'Дата изменения   {symbol_utf}')
        elif heading == 3:
            self.tree.heading('time', text=f'Время изменения   {symbol_utf}')
        elif heading == 4:
            self.tree.heading('notify', text=f'Оповещения   {symbol_utf}')

    def _delete_triangle_heading(self):
        """убрать всех треугольники сортировки с кнопок сортировки"""
        self.tree.heading('name', text='Name')
        self.tree.heading('ip', text='IP address')
        self.tree.heading('date', text='Дата изменения')
        self.tree.heading('time', text='Время изменения')
        self.tree.heading('notify', text='Оповещения')


class TableFolders(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bd=2)

        # список папок не подлежащих удалению
        self.static_folders_list = ('live', 'dead', 'all', 'pause')

        # загрузка икононок состояний хостов
        self.img_pause = tk.PhotoImage(file='icons/pause_hosts.png')
        self.img_good = tk.PhotoImage(file='icons/live_hosts.png')
        self.img_bad = tk.PhotoImage(file='icons/dead_hosts.png')
        self.img_folder = tk.PhotoImage(file='icons/folder.png')
        self.img_all = tk.PhotoImage(file='icons/all_hosts.png')
        self.img_del = tk.PhotoImage(file='icons/cross16x16.png')
        self.img_add = tk.PhotoImage(file='icons/add16x16.png')
        self.img_upd = tk.PhotoImage(file='icons/update_info16x16.png')
        self.img_ren = tk.PhotoImage(file='icons/rename16x16.png')

        self.menu = tk.Menu(tearoff=0)
        self.menu.add_command(label='  Создать', command=self.create_folder_in_server, image=self.img_add,
                              compound='left')
        self.menu.add_command(label='  Переименовать', command=self.rename_folder_in_server, compound='left',
                              image=self.img_ren)
        self.menu.add_command(label='  Удалить', command=self.delete_folder_in_server, image=self.img_del,
                              compound='left')
        self.menu.add_command(label='  Обновить список', command=self.update_folders, image=self.img_upd,
                              compound='left')

        self.menu1 = tk.Menu(tearoff=0)
        self.menu1.add_command(label='  Создать', command=self.create_folder_in_server, image=self.img_add,
                               compound='left')
        self.menu1.add_command(label='  Обновить список', command=self.update_folders, image=self.img_upd,
                               compound='left')

        # таблица-список хостов
        self.tree = ttk.Treeview(self,
                                 height=30, selectmode='browse', style='f.Treeview', takefocus=False)

        self.tree.bind('<<TreeviewSelect>>', self._identify_item)
        self.tree.bind('<Button-3>', self.select_item)

        # стилизация Treeview и установка размера одного элемента на 19 пикс.
        s = ttk.Style()
        s.configure('f.Treeview', rowheight=19)

        # скролл-бары
        self.scroll = ttk.Scrollbar(self, orient='vertical', command=self.tree.yview)
        self.scroll_x = ttk.Scrollbar(self, orient='horizontal', command=self.tree.xview)
        self.tree.configure(yscrollcommand=self._adaptive_scroller,
                            xscrollcommand=self._adaptive_scroller_x)

        # колонки (столбцы) списка
        self.tree.heading('#0', text='Список папок')
        self.tree.column('#0', width=300, minwidth=300)

        # теги для присваивания иконки
        self.tree.tag_configure('all', image=self.img_all)
        self.tree.tag_configure('live', image=self.img_good)
        self.tree.tag_configure('dead', image=self.img_bad)
        self.tree.tag_configure('pause', image=self.img_pause)
        self.tree.tag_configure('folder', image=self.img_folder)

        self.tree.insert('', iid='all', index=tk.END, text='   All monitors', tags=('all',))
        self.tree.insert('', iid='live', index=tk.END, text='   Live monitors', tags=('live',))
        self.tree.insert('', iid='dead', index=tk.END, text='   Dead monitors', tags=('dead',))
        self.tree.insert('', iid='pause', index=tk.END, text='   Pause monitors', tags=('pause',))

        # расстоновка всех виджетов (скролл_x, скролл_y, treeview)
        self.tree.grid(row=0, column=0, sticky='nsew')
        self.scroll.grid(row=0, column=1, sticky='ns')
        self.scroll_x.grid(row=1, column=0, sticky='we')

        # параметры расстягивания колонок и строк Treeview
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

    def select_item(self, e):
        """выделить элемент при нажатии на него ПКМ"""
        item = self.tree.identify_row(e.y)
        if item:
            self.tree.selection_set(item)
            self.open_menu(e)
        else:
            self.open_menu1(e)

    def open_menu(self, e):
        print(e)
        self.menu.post(e.x_root, e.y_root)

    def open_menu1(self, e):
        self.menu1.post(e.x_root, e.y_root)

    def select_all_hosts(self):
        """выбрать папку All monitors"""
        self.tree.focus('all')
        self.tree.selection_set('all')

    def _adaptive_scroller(self, a, b):
        """Scroll_Y вызвает этот метод, при любом изменении размера виджета,
        или изменении количества находящихся в нём элементов.
        Нужен для авто-скрытия scroll-баров, когда в них нет нужды"""

        self.scroll.set(a, b)
        if float(b) == 1.0 and float(a) == 0.0:
            self.scroll.grid_remove()
        else:
            self.scroll.grid(row=0, column=1, sticky='ns')

    def _adaptive_scroller_x(self, a, b):
        """Scroll_X вызвает этот метод, при любом изменении размера виджета,
        или изменении количества находящихся в нём элементов.
        Нужен для авто-скрытия scroll-баров, когда в них нет нужды"""

        self.scroll_x.set(a, b)
        if float(b) == 1.0 and float(a) == 0.0:
            self.scroll_x.grid_remove()
        else:
            self.scroll_x.grid(row=1, column=0, sticky='we')

    def _identify_item(self, e):
        """При нажатии на папку, в списке хостов происходит обновление"""

        # очистка полей информации при выборе папки
        app.monitoring_frame.host_info.delete_data()

        item = self.tree.selection()
        try:
            if item[0] in self.static_folders_list:
                app.monitoring_frame.host_list.show_hosts(item[0])
            else:
                app.monitoring_frame.host_list.show_hosts(item[0])
        except (IndexError, TypeError):
            pass

    def delete_folders(self):
        """удалить все папки, кроме статических"""
        folders = self.tree.get_children()
        for folder in folders:
            if folder in self.static_folders_list:
                continue
            self.tree.delete(folder)

    def _insert_folders(self):
        folders = api.GetAllFolders()
        if handler_status_codes(app, folders[0], 'bad', reconnect=False):
            self.delete_folders()
            if folders[1]:
                for f in folders[1]:
                    id_folder, name = f
                    self.tree.insert('', iid=str(id_folder), text=' '*3 + name, index=tk.END, tags=('folder',),
                                     values=(name,))

    def update_folders(self):
        """обновить список папок,
        метод удаляет папки из treeview и сразу же добавляет новые"""
        self._insert_folders()

    def delete_folder_in_server(self):
        """удалить папку на сервере в БД"""
        item = self.tree.selection()
        if not item:
            tk.messagebox.showwarning('Папка не выбрана', 'Выберите папку, которую хотите удалить')
            return
        elif item[0] in self.static_folders_list:
            tk.messagebox.showwarning('Недопустимое действие', 'Невозможно удалить выбранную папку')
            return
        name = self.tree.item(item[0])['text'][3:]
        ask = tk.messagebox.askyesno('Удаление папки', f'Вы действительно хотите удалить папку "{name}"')
        if ask:
            response = api.DeleteFolder(item[0])
            if handler_status_codes(app, response[0], 'bad', reconnect=False):
                self.delete_folder_in_hosts(item[0])
                self.update_folders()

    @staticmethod
    def delete_folder_in_hosts(iid):
        """удалить метку (iid) папки на хостах, которые
        пренадлежали этой папке"""
        try:
            hosts = api.GetAllHosts()[1]
            for host in hosts:
                if host[2] == iid:
                    api.PutHost(host[0], id_folder='none')
        except (Exception,):
            pass

    def create_folder_in_server(self):
        """создать новую папку на сервере в БД"""
        self.wait_window(CreateFolderWindow(self))

    def rename_folder_in_server(self):
        """переименовать папку на сервере в БД"""
        item = self.tree.selection()
        if not item:
            tk.messagebox.showwarning('Папка не выбрана', 'Выберите папку, которую хотите переименовать')
            return
        elif item[0] in self.static_folders_list:
            tk.messagebox.showwarning('Недопустимое действие', 'Невозможно переименовать выбранную папку')
            return
        self.wait_window(RenameFolderWindow(item_iid=item, parent=self))


class CreateFolderWindow(tk.Toplevel):
    """Окно создания новой папки"""
    def __init__(self, parent):
        super().__init__(parent)
        self.title('Создание папки')
        self.parent = parent
        self.geometry(center_window(self, 400, 120))
        # app.stop_loop()  # остановить все циклы обновления
        self.grab_set()
        self.protocol('WM_DELETE_WINDOW', self.close_window)
        self.resizable(True, False)
        app.open_window = self

        self.entry_name = EntryWithMenu(self)
        self.label_name = ttk.Label(self, text='Введите название:', width=20, anchor='e')

        self.frame_btns = tk.Frame(self)
        self.button_confirm = ttk.Button(self.frame_btns, text='Создать', command=self.confirm, takefocus=False,
                                         width=10)
        self.button_close = ttk.Button(self.frame_btns, text='Отмена', command=self.close_window, takefocus=False,
                                       width=10)

        self.button_close.grid(row=0, column=1, padx=20)
        self.button_confirm.grid(row=0, column=0)

        self.label_name.grid(row=0, column=0)
        self.entry_name.grid(row=0, column=1, sticky='nsew', padx=20, pady=30)
        self.frame_btns.grid(row=1, column=1, sticky='e')

        self.columnconfigure(1, weight=1)

    def close_window(self):
        """вызывается при закрытии окна"""
        # app.run_loop()  # запусть все циклы обновления
        self.destroy()

    def confirm(self):
        """отправить запрос на сервер"""
        name = self.entry_name.get()
        if name:
            response = api.CreateFolder(name)  # запрос
            if handler_status_codes(self, response[0], show='bad', reconnect=False):
                app.monitoring_frame.folder_list.update_folders()
                self.close_window()
            else:
                self.destroy()
        else:
            tk.messagebox.showwarning('Внимание', 'Поле ввода не должно быть пустым', parent=self)


class RenameFolderWindow(CreateFolderWindow):
    """Окно переименования папок, наследуется от окна создания папок"""
    def __init__(self, item_iid, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.item = item_iid
        self.title('Изменение названия папки')
        self.button_confirm.configure(text='Переименовать', width=15)

    def confirm(self):
        """отправить запрос на сервер"""
        name = self.entry_name.get()
        if name:
            response = api.PutFolder(self.item[0], new_id=None, name=name)  # запрос
            if handler_status_codes(self, response[0], show='bad', reconnect=False):
                app.monitoring_frame.folder_list.update_folders()
            self.close_window()
        else:
            tk.messagebox.showwarning('Пустое поле', 'Поле ввода не должно быть пустым', parent=self)


class CreateHostWindow(CreateFolderWindow):
    """Окно создания нового хоста в базе данных сервера"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title('Создание хоста в базе данных')
        self.geometry(center_window(self, 400, 145))

        self.label_name['anchor'] = 'center'

        self.entry_ip = EntryWithMenu(self)
        self.label_ip = ttk.Label(self, text='Введите IP:', width=20, anchor='center')

        self.combobox = ttk.Combobox(self, state='readonly', values=self.build_folders_combobox())
        self.label_combobox = ttk.Label(self, text='Выберите папку:', width=20, anchor='center')

        self.button_confirm.grid(pady=15)

        self.label_name.grid(row=0, column=0)
        self.entry_name.grid(row=0, column=1, padx=15, pady=5)
        self.label_ip.grid(row=1, column=0)
        self.entry_ip.grid(row=1, column=1, sticky='nsew', padx=15, pady=5)
        self.label_combobox.grid(row=2, column=0)
        self.combobox.grid(row=2, column=1, sticky='nsew', padx=15,pady=5)
        self.frame_btns.grid(row=3, columnspan=2, column=0, sticky='e', pady=2)

        self.rowconfigure(3, weight=1)

    def confirm(self):
        """отправить запрос на сервер"""
        name = self.entry_name.get()
        folder = self.combobox.get()
        ip = self.entry_ip.get()
        if not self._validate_ip(ip):
            tk.messagebox.showwarning('Неккоректный IP', 'Неккоректный формат IP адреса', parent=self)
            return
        try:
            folder = folder.split(')', 1)[0]
            int(folder)
        except ValueError:
            folder = None

        if not folder:
            tk.messagebox.showwarning('Внимание', 'Папка не выбрана', parent=self)
            return

        if name and ip:
            response = api.CreateHost(ip=ip, id_folder=folder, name=name)  # запрос на сервер
            if handler_status_codes(self, response[0], show='all', reconnect=False):
                self.destroy()
        else:
            tk.messagebox.showwarning('Внимание', 'Поля ввода не должны быть пустыми', parent=self)

    @staticmethod
    def _validate_ip(ip: str):
        """валидация IP адреса"""
        octets_ip = ip.split('.', 4)
        if len(octets_ip) == 4:
            for count, str_octet in enumerate(octets_ip):
                try:
                    int_octet = int(str_octet)
                    if count == 0 and int_octet < 1:
                        return
                    if int_octet > 255:
                        return
                except ValueError:
                    return
            return True

    @staticmethod
    def build_folders_combobox():
        """собрать список папок для вставки в combobox"""
        f_lst = []
        item = api.GetAllFolders()
        if handler_status_codes(app, item[0], reconnect=False):
            for iid, name in item[1]:
                f_lst.append(f'{iid}) {name}')
            return f_lst


class BitmapButton(tk.Frame):
    def __init__(self, parent, img, command=None, text=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.parent = parent
        self.img = img
        self.text = text
        self.command = command
        self._non_active_color = self.cget('background')
        self._width = self.cget('width')
        self._height = self.cget('height')

        self.button = tk.Button(self, relief='flat', bd=0, background=self._non_active_color, image=self.img,
                                command=self.command, text=self.text, compound='left')
        self.button.bind('<Enter>', lambda e: self.clr_focus())
        self.button.bind('<Leave>', lambda e: self.clr_unfocus())
        self.button.place(x=1, y=1, width=self._width-2, height=self._height-2)

    def clr_focus(self):
        self.button.configure(background='#b2d6f3')
        self.configure(background='#0078d7')

    def clr_unfocus(self):
        self.button.configure(background=self._non_active_color)
        self.configure(background=self._non_active_color)


class HostInfo(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bd=2)

        # данные хоста, нужно для сравнения после изменения
        self.first_data = []

        self.check_var_sms = tk.BooleanVar()
        self.check_var_pause = tk.BooleanVar()
        self.check_var_sms.set(False)
        self.check_var_pause.set(False)

        self.img_notify = tk.PhotoImage(file='icons/notify.png')
        self.img_pause = tk.PhotoImage(file='icons/pause1.png')
        self.img_confirm = tk.PhotoImage(file='icons/confirm.png')
        self.img_update = tk.PhotoImage(file='icons/update_info.png')

        self.frame1 = tk.Frame(self)
        self.frame1.columnconfigure(1, weight=1)
        self.ip_label = ttk.Label(self.frame1, text='IP:')
        self.ip_entry = EntryWithMenu(self.frame1, width=40)
        self.name_label = ttk.Label(self.frame1, text='Название:')
        self.name_entry = EntryWithMenu(self.frame1)
        self.folder_label = ttk.Label(self.frame1, text='Папка:')
        self.folder_combobox = ttk.Combobox(self.frame1, state='readonly', takefocus=False)

        self.frame_checkbox = tk.Frame(self.frame1)
        # self.sms_checkbox = ttk.Checkbutton(self.frame_checkbox, text='Оповещения', takefocus=False,
        #                                     image=self.img_notify, compound='left', variable=self.check_var_sms,
        #                                     state=tk.DISABLED)
        self.sms_button = ttk.Button(self.frame_checkbox, text='Оповещения', image=self.img_notify, compound='left',
                                     command=lambda: Notify(app, self.get_notify_data(), self.get_ip_data()))
        self.pause_checkbox = ttk.Checkbutton(self.frame_checkbox, text='Пауза ICMP', takefocus=False,
                                              image=self.img_pause, compound='left', variable=self.check_var_pause)
        # self.sms_checkbox.grid(row=0, column=0, padx=10)
        self.sms_button.grid(row=0, column=0, padx=10, pady=2)
        self.pause_checkbox.grid(row=0, column=1, padx=10)

        self.frame_bitmaps = tk.Frame(self.frame1)
        self.update_bitmap = ttk.Button(self.frame_bitmaps, image=self.img_update, width=30, takefocus=False,
                                        command=self.update_data)
        self.confirm_bitmap = ttk.Button(self.frame_bitmaps, image=self.img_confirm, width=30, takefocus=False,
                                         command=self.confirm_data)
        self.update_bitmap.grid(row=0, column=0, pady=5)
        self.confirm_bitmap.grid(row=1, column=0, pady=5)

        self.ip_label.grid(row=0, column=0, padx=5, sticky='w')
        self.ip_entry.grid(row=0, column=1, pady=2, sticky='we')
        self.name_label.grid(row=1, column=0, padx=5, sticky='w')
        self.name_entry.grid(row=1, column=1, pady=2, sticky='we')
        self.folder_label.grid(row=2, column=0, padx=5, sticky='w')
        self.folder_combobox.grid(row=2, column=1, pady=2, sticky='we')
        self.frame_checkbox.grid(row=3, column=1, sticky='w')
        self.frame_bitmaps.grid(row=0, rowspan=3, column=2, padx=10)

        self.frame2 = tk.Frame(self)
        self.info_text = InfoText(self.frame2, height=10, width=20, highlightthickness=1, bd=0,
                                  highlightbackground='#828790', yscrollcommand=self._adaptive_scroller)
        self.info_text.grid(row=0, column=0, sticky='nsew')
        self.scroll = ttk.Scrollbar(self.frame2, orient='vertical', command=self.info_text.yview)

        self.frame2.columnconfigure(0, weight=1)
        self.frame2.rowconfigure(0, weight=1)

        self.frame1.grid(row=0, column=0, sticky='we')
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.frame2.grid(row=1, column=0, sticky='nsew')

        self.pass_frame = tk.Frame(self.frame2, width=17)
        self.pass_frame.grid(row=0, column=1, sticky='ns')

    def _adaptive_scroller(self, a, b):
        self.scroll.set(a, b)
        if float(b) == 1.0 and float(a) == 0.0:
            self.scroll.grid_remove()
            self.pass_frame.grid(row=0, column=1, sticky='ns')
        else:
            self.pass_frame.grid_remove()
            self.scroll.grid(row=0, column=1, sticky='ns')

    def get_notify_data(self):
        """получить данные"""
        return self.first_data[-1]

    def get_ip_data(self):
        """получить ip текущего хоста"""
        return self.first_data[0]

    def insert_data(self, host):
        """вставка информации о хосте"""

        self.delete_data()  # очистка полей перед вставкой
        item = api.GetOneHost(host)  # запрос на сервер

        # обработка запроса
        if handler_status_codes(app, item[0], reconnect=False):
            ip, name, folder, state, _, info, notify = item[1]

            self.sms_button['state'] = tk.NORMAL  # перевод кнопки в активное состояние

            if state == 'pause':
                state = True
            else:
                state = False

            self.first_data = [ip, name, folder, state, info, notify]

            self.ip_entry.insert(tk.END, ip)  # вставка IP
            self.name_entry.insert(tk.END, name)  # вставка Названия
            self.info_text.insert(tk.END, info)  # вставка Информации

            f_lst = self.build_folders_combobox(folder)  # список папок и их iid
            if f_lst:
                # если список не пустой, тогда добавить
                self.folder_combobox.configure(values=f_lst)
                # проверка существует ли папка с её iid, которая присвоена хосту
                for i in f_lst:
                    if folder == i.split(')', 1)[0]:
                        self.folder_combobox.set(i)
                        break
                    else:
                        # если iid присвоен, но папки не существует в базе,
                        # вывести "папки не существует"
                        self.first_data[2] = '(папки не существует)'
                        self.folder_combobox.set('(папки не существует)')

            # установка галочек, если режимы активны
            if state:
                self.check_var_pause.set(True)
            if notify:
                self.check_var_sms.set(True)

    @staticmethod
    def build_folders_combobox(id_folder):
        """собрать список папок для вставки в combobox"""
        host_folder = ''
        f_lst = []
        item = api.GetAllFolders()
        if handler_status_codes(app, item[0], reconnect=False):
            for iid, name in item[1]:
                if iid == id_folder:
                    host_folder = f'{iid}) {name}'
                else:
                    f_lst.append(f'{iid}) {name}')
            f_lst.insert(0, host_folder)
            return f_lst

    def delete_data(self):
        """очистка всех всех полей и снятие галочек"""

        self.first_data = None  # очистка объекта
        self.check_var_sms.set(False)  # убрать галочку с оповещений
        self.check_var_pause.set(False)  # убрать галочку с паузы
        self.ip_entry.delete(0, tk.END)  # очистить поле IP
        self.name_entry.delete(0, tk.END)  # очистить поле Название
        self.info_text.delete('1.0', tk.END)  # очистить поле Информация
        self.folder_combobox.configure(values=[])
        self.folder_combobox.configure(state='normal')
        self.folder_combobox.delete(0, tk.END)
        self.folder_combobox.configure(state='readonly')
        self.sms_button['state'] = tk.DISABLED  # отключение кнопки

    def update_data(self, ip_host=None):
        """обновить данные в полях"""
        if ip_host:
            self.insert_data(ip_host)
        elif self.first_data:
            ip = self.first_data[0]
            self.insert_data(ip)

    @staticmethod
    def _validate_ip(ip: str):
        """валидация IP адреса"""
        octets_ip = ip.split('.', 4)
        if len(octets_ip) == 4:
            for count, str_octet in enumerate(octets_ip):
                try:
                    int_octet = int(str_octet)
                    if count == 0 and int_octet < 1:
                        return
                    if int_octet > 255:
                        return
                except ValueError:
                    return
            return True

    def confirm_data(self):
        """отправить заполненную форму на сервер"""
        if not self._validate_ip(self.ip_entry.get()):
            tk.messagebox.showwarning('Неверный IP', 'Недопустимый формат IP адреса')
            return
        if not self.name_entry.get():
            tk.messagebox.showwarning('Пустое поле', 'Поле ввода названия хоста не должно быть пустым')
            return
        data = self._compare_data()
        if data:
            ip, name, folder, state, info, notify = data
            response = api.PutHost(self.first_data[0], ip, name, folder, state, info, notify)
            if handler_status_codes(app, response[0], 'all', reconnect=False):
                self.update_data(ip)

    def _compare_data(self):
        """сравнить введённые новые данные и текущие данные хоста,\n
        если данные совпадют (пользователь ничего не удалил и не ввёл),\n
        тогда вернёт False, иначе вернёт значения, которые изменились,\n
        P.S написал очень коряво, лучше не смотреть на это, потом поправлю
        """

        if self.first_data:
            _ip, _name, _folder, _state, _info, _notify = self.first_data

            notify = None

            state = self.check_var_pause.get()
            if state == _state:
                state = None
            else:
                if state:
                    state = 'pause'
                else:
                    state = 'offline'
            ip = self.ip_entry.get()
            if ip == _ip:
                ip = None
            name = self.name_entry.get()
            if name == _name:
                name = None
            info = self.info_text.get('1.0', 'end-1c')
            if info:
                if info == _info:
                    info = None
                else:
                    pass
            else:
                info = '\n'
            folder = self.folder_combobox.get()
            if folder:
                if folder.split(')', 1)[0] == _folder:
                    folder = None
                else:
                    try:
                        folder = folder.split(')', 1)[0]
                        int(folder)
                    except ValueError:
                        folder = None

            for i in (ip, name, folder, state, info, notify):
                if i:
                    return ip, name, folder, state, info, notify
            return None


class MainMenu(tk.Menu):
    """Главное меню основного окна"""
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.parent = parent

        self.img_save = tk.PhotoImage(file='icons/save_icon.png')
        self.img_out = tk.PhotoImage(file='icons/exit.png')
        self.img_disconn = tk.PhotoImage(file='icons/disconnect.png')
        self.img_shut = tk.PhotoImage(file='icons/shutdown_server.png')
        self.img_all = tk.PhotoImage(file='icons/check_all16x16.png')
        self.img_dead = tk.PhotoImage(file='icons/check_dead16x16.png')
        self.img_info = tk.PhotoImage(file='icons/info16x16.png')

        #  разделы подменю
        self.FileMenu = tk.Menu(self, tearoff=0)
        self.ActionMenu = tk.Menu(self, tearoff=0)
        self.InfoMenu = tk.Menu(self, tearoff=0)
        self.SaveHosts = tk.Menu(self, tearoff=0)

        self.SaveHosts.add_command(label='в формате CSV', command=lambda: app.save_file_hosts('csv'),)
        self.SaveHosts.add_command(label='в формате TXT', command=lambda: app.save_file_hosts('txt'),)

        #  раздел "Файл"
        self.add_cascade(menu=self.FileMenu, label='Файл')
        self.FileMenu.add_cascade(menu=self.SaveHosts, label='  Сохранить список хостов',
                                  image=self.img_save, compound='left')
        self.FileMenu.add_command(label='  Отключиться от сервера', command=self.parent.server_connection_lost,
                                  image=self.img_disconn, compound='left')
        self.FileMenu.add_separator()
        self.FileMenu.add_command(label='  Выйти', command=self.parent.destroy, image=self.img_out, compound='left')

        #  раздел "Действия"
        self.add_cascade(menu=self.ActionMenu, label='Действия')
        self.ActionMenu.add_command(label='  Перезагруить сервер', command=lambda: api.ShutdownServer(),
                                    image=self.img_shut, compound='left')
        self.ActionMenu.add_command(label='  Check ALL', command=lambda: api.PingALL(),
                                    image=self.img_all, compound='left')
        self.ActionMenu.add_command(label='  Check DEAD', command=lambda: api.PingDEAD(),
                                    image=self.img_dead, compound='left')

        #  раздел "Справка"
        self.add_cascade(menu=self.InfoMenu, label='Справка')
        self.InfoMenu.add_command(label='  О программе', image=self.img_info, compound='left',
                                  command=lambda: AuthorWindow(app))


class NoteBook(ttk.Notebook):
    """Notebook виджет с убранными линиями фокуса"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        s = ttk.Style()
        s.configure('Ch.TNotebook', sticky='w')
        s.layout("Tab", [('Notebook.tab', {'sticky': 'nswe', 'children': [
            ('Notebook.padding', {'side': 'top', 'sticky': 'nswe', 'children': [
                ('Notebook.label', {'side': 'top', 'sticky': ''})], })], })])
        self.config(style='Ch.TNotebook')


class NoteBookLog(NoteBook):
    def __init__(self, parent):
        super().__init__(parent)
        self.log = LogFrame(self)
        self.users = UsersFrame(self)
        self.add(self.log, text='  Лог сервера  ')
        self.add(self.users, text='  Пользователи  ', padding=2)
        self.bind('<<NotebookTabChanged>>', self._tab_change)
        self.temp_flag = False

    def _tab_change(self, e=None):
        if self.temp_flag:
            self.users.tab_event_notebook()
        self.temp_flag = True


class LogFrame(tk.Frame):
    """Отображание лога сервера"""
    def __init__(self, parent):
        super().__init__(parent)

        self.strings_counter = 0  # счётчик кол-во строк в поле логов
        self.tag_list = []  # список тегов навешанных на строки и символы
        self.str_list = []

        # глобальные переменные импортированные из самого tkinter
        temp_data = load_temp_data()  # подгрузка параметров из файла

        self.icmp = tk.BooleanVar()
        self.icmp.set(temp_data['check1'])
        self.users = tk.BooleanVar()
        self.users.set(temp_data['check2'])
        self.alarm = tk.BooleanVar()
        self.alarm.set(temp_data['check3'])

        self.group_frame = tk.Frame(self)  # групирующий фрейм
        self.label_text = ttk.Label(self.group_frame, text='Отображать события:')
        self.checkbox_icmp_events = ttk.Checkbutton(self.group_frame, text='Мониторинга', variable=self.icmp)
        self.checkbox_users_events = ttk.Checkbutton(self.group_frame, text='Пользователей', variable=self.users)
        self.checkbox_alarm_events = ttk.Checkbutton(self.group_frame, text='Предупреждений сервера',
                                                     variable=self.alarm)

        self.label_text.grid(row=0, column=0, padx=5)
        self.checkbox_icmp_events.grid(row=0, column=1, padx=5)
        self.checkbox_users_events.grid(row=0, column=2, padx=5)
        self.checkbox_alarm_events.grid(row=0, column=3, padx=5)

        self.text = LogText(self, height=5, yscrollcommand=self._adaptive_scroller, highlightthickness=1, bd=0,
                            highlightbackground='#828790', font=('Segoe UI', 9))
        self.text_scroll = ttk.Scrollbar(self, orient='vertical', command=self.text.yview)

        self.text.tag_configure(f'icmp_bad', foreground='#FF0000')  # красный текст
        self.text.tag_configure(f'icmp_good', foreground='#006400')  # зеленый текст

        # теги для раскраски оповещений сервера (warning)
        self.text.tag_configure(f'alarm_bracket', foreground='#CC5500', font=('Segoe UI', 9, 'bold'))  # квадратные скобки
        self.text.tag_configure(f'alarm_warning', foreground='grey30', font=('Segoe UI', 9, 'bold'))  # надпись warning
        self.text.tag_configure(f'alarm_message', foreground='#CC5500', font=('Segoe UI', 9, 'bold'))  # текст оповещения

        # теги для раскраски событий обычных пользователей
        self.text.tag_configure(f'user_bracket', foreground='#0000CD', font=('Segoe UI', 9, 'bold'))  # квадратные скобки
        self.text.tag_configure(f'user_user', foreground='grey30', font=('Segoe UI', 9, 'bold'))  # надпись "пользователь"
        self.text.tag_configure(f'user_login', foreground='#0000CD', font=('Segoe UI', 9, 'bold'))  # логин пользователя
        self.text.tag_configure(f'user_message', foreground='#4169E1', font=('Segoe UI', 9, 'bold'))  # текст оповещения

        # теги для раскраски событий админов
        self.text.tag_configure(f'admin_bracket', foreground='red', font=('Segoe UI', 9, 'bold'))  # квадратные скобки
        self.text.tag_configure(f'admin_user', foreground='grey30', font=('Segoe UI', 9, 'bold'))  # надпись "админ"
        self.text.tag_configure(f'admin_login', foreground='red', font=('Segoe UI', 9, 'bold'))  # логин пользователя
        self.text.tag_configure(f'admin_message', foreground='#CD5C5C', font=('Segoe UI', 9, 'bold'))  # текст оповещения

        self.alarm_prefix = '[Server]'
        self.user_prefix = '[Пользователь]'
        self.admin_prefix = '[Администратор]'

        self.text.grid(row=1, column=0, sticky='nsew')
        self.group_frame.grid(row=0, column=0, sticky='w')
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

    def _adaptive_scroller(self, a, b):
        """адапртивный скролл-бар, исчезает когда нечего скролить"""
        self.text_scroll.set(a, b)
        if float(b) == 1.0 and float(a) == 0.0:
            self.text_scroll.grid_remove()
        else:
            self.text_scroll.grid(row=1, column=1, sticky='ns')

    def log_update_loop(self):
        """добавление событий в лог (итерация каждую секунду)"""
        if app.stop_afters:
            return
        log = api.GetLogQueue()

        for i in log:
            self.handler(i)

        self.after(1000, self.log_update_loop)

    def handler(self, log):
        """обработчик типов логов"""

        type_log = log['type']
        if type_log == 'icmp' and self.icmp.get():
            # icmp события (хост в сети, не в сети)
            self.print_icmp_evnt(log)
        elif type_log == 'alarm' and self.alarm.get():
            # предупреждения сервера
            self.insert_text(log['message'], 'alarm')
        elif type_log == 'user' and self.users.get():
            # события пользователей (зашёл, вышел, создал, удалил и т.д)
            self.insert_text('', 'user', log)

    def print_icmp_evnt(self, log):
        """вывести icmp событие"""

        ip = log['ip']
        name = log['name']
        state = log['state']
        if state:
            # хост в сети
            string = f'Хост <{ip}> {name}  успешно проверен'
            self.insert_text(string, 'good')
        else:
            # хост не в сети
            string = f'Хост <{ip}> {name}  не доступен'
            self.insert_text(string, 'bad')

    def print_user_evnt(self, log):
        """вывести событие пользователя"""
        pass

    def insert_text(self, text, log_type, user_data=None):
        """добавить строку в text виджет"""
        time = datetime.now().strftime('%Y/%m/%d  %H:%M:%S')
        self.text['state'] = tk.NORMAL  # включение редактирования поля логов
        num_str = int(self.text.index('end-1c').split('.')[0])

        if log_type == 'good':
            in_text = f'   {time}  {text}\n'
            self.text.insert(float(num_str), in_text)
            self.text.tag_add(f'icmp_good',
                              f'{num_str}.{len(in_text)-len(text)-1}',
                              f'{num_str}.{len(in_text)}')
        elif log_type == 'bad':
            in_text = f'   {time}  {text}\n'
            self.text.insert(float(num_str), in_text)
            self.text.tag_add(f'icmp_bad',
                              f'{num_str}.{len(in_text)-len(text)-1}',
                              f'{num_str}.{len(in_text)}')
        elif log_type == 'alarm':
            in_text = f'   {time}  {self.alarm_prefix}  {text}\n'
            self.text.insert(float(num_str), in_text)

            first_bracket = in_text.find(self.alarm_prefix)  # индекс первой скобки
            second_bracket = first_bracket + len(self.alarm_prefix) - 1  # индекс второй скобки
            start_symb = first_bracket + 1  # индекс начала префикса
            end_symb = second_bracket - 1  # индекс конца префикса
            start_msg = in_text.find(text)  # индекс начала сообщения
            end_msg = start_msg + len(text)  # индекс конца префикса
            self.text.tag_add(f'alarm_bracket',
                              f'{num_str}.{first_bracket}',
                              f'{num_str}.{first_bracket+1}')

            self.text.tag_add(f'alarm_bracket',
                              f'{num_str}.{second_bracket}',
                              f'{num_str}.{second_bracket+1}')

            self.text.tag_add(f'alarm_warning',
                              f'{num_str}.{start_symb}',
                              f'{num_str}.{end_symb+1}')

            self.text.tag_add(f'alarm_message',
                              f'{num_str}.{start_msg}',
                              f'{num_str}.{end_msg}')

        elif log_type == 'user':

            ip = user_data['ip']
            login = user_data['login']
            message = user_data['message']
            access = user_data['access']

            if access == 'guest':
                in_text = f'   {time}  {self.user_prefix}  {login}  {message}\n'
                self.text.insert(float(num_str), in_text)

                first_bracket = in_text.find(self.user_prefix)  # индекс первой скобки
                second_bracket = first_bracket + len(self.user_prefix) - 1  # индекс второй скобки
                start_symb = first_bracket + 1  # индекс начала префикса
                end_symb = second_bracket  # индекс конца префикса
                start_login = in_text.find(login)  # индекс начала логина
                end_login = start_login + len(login)  # индекс конца логина
                start_msg = in_text.find(message)  # индекс начала сообщения
                end_msg = start_msg + len(message)  # индекс конца префикса
                self.text.tag_add(f'user_bracket',
                                  f'{num_str}.{first_bracket}',
                                  f'{num_str}.{first_bracket + 1}')

                self.text.tag_add(f'user_bracket',
                                  f'{num_str}.{second_bracket}',
                                  f'{num_str}.{second_bracket + 1}')

                self.text.tag_add(f'user_user',
                                  f'{num_str}.{start_symb}',
                                  f'{num_str}.{end_symb}')

                self.text.tag_add(f'user_login',
                                  f'{num_str}.{start_login}',
                                  f'{num_str}.{end_login}')

                self.text.tag_add(f'user_message',
                                  f'{num_str}.{start_msg}',
                                  f'{num_str}.{end_msg}')

            elif access == 'admin':
                in_text = f'   {time}  {self.admin_prefix}  {login}  {message}\n'
                self.text.insert(float(num_str), in_text)

                first_bracket = in_text.find(self.admin_prefix)  # индекс первой скобки
                second_bracket = first_bracket + len(self.admin_prefix) - 1  # индекс второй скобки
                start_symb = first_bracket + 1  # индекс начала префикса
                end_symb = second_bracket  # индекс конца префикса
                start_login = in_text.find(login)  # индекс начала логина
                end_login = start_login + len(login)  # индекс конца логина
                start_msg = in_text.find(message)  # индекс начала сообщения
                end_msg = start_msg + len(message)  # индекс конца префикса
                self.text.tag_add(f'admin_bracket',
                                  f'{num_str}.{first_bracket}',
                                  f'{num_str}.{first_bracket + 1}')

                self.text.tag_add(f'admin_bracket',
                                  f'{num_str}.{second_bracket}',
                                  f'{num_str}.{second_bracket + 1}')

                self.text.tag_add(f'admin_user',
                                  f'{num_str}.{start_symb}',
                                  f'{num_str}.{end_symb}')

                self.text.tag_add(f'admin_login',
                                  f'{num_str}.{start_login}',
                                  f'{num_str}.{end_login}')

                self.text.tag_add(f'admin_message',
                                  f'{num_str}.{start_msg}',
                                  f'{num_str}.{end_msg}')

        if self.text.auto_scroll.get():
            self.text.see(tk.END)
        if int(self.text.index('end-1c').split('.')[0]) > 10000:
            self.text.delete(1.0, 1000.0)
        self.text['state'] = tk.DISABLED  # отключение редактирования поля логов


class PingAdvanced(tk.Toplevel):
    def __init__(self, parent, ip):
        super().__init__(parent)
        self.ip = ip
        self.parent = parent
        self.geometry(center_window(self, 320, 120))
        self.grab_set()
        self.title('Укажите параметры пинга')
        self.focus()
        self.resizable(False, False)

        values = ['1', '3', '5', '10', '20', '30', '50']
        values2 = ['32', '512', '1024', '5000', '10000', '25000', '50000']
        self.combobox = ttk.Combobox(self, values=values, state='readonly', width=5)
        self.combobox_2 = ttk.Combobox(self, values=values2, state='readonly', width=5)
        self.combobox.set('1')
        self.combobox_2.set('32')
        self.combobox.place(x=140, y=20)
        self.combobox_2.place(x=140, y=45)

        label = ttk.Label(self, text='Кол-во окон пинга:')
        label_2 = ttk.Label(self, text='Размер пакета:')
        label_3 = ttk.Label(self, text='шт.')
        label_4 = ttk.Label(self, text='байт')
        label.place(x=10, y=20)
        label_2.place(x=10, y=45)
        label_3.place(x=200, y=20)
        label_4.place(x=200, y=45)

        self.button = ttk.Button(self, text='Открыть', command=self.open_cmd_ping)
        self.button.place(x=120, y=90)

    def open_cmd_ping(self):
        bytes_packet = self.combobox_2.get()
        for i in range(int(self.combobox.get())):
            os.system(f"cmd.exe /c start ping {self.ip} -t -l {bytes_packet}")
        self.destroy()


class UsersFrame(tk.Frame):
    """Список пользователей зарегистрированных в БД,
    и обозначаение онлайн пользователей"""
    def __init__(self, parent):
        super().__init__(parent, background='white')
        self.tree = ttk.Treeview(self, columns=('username', 'ip', 'last_online'),
                                 height=3, selectmode='browse', style='qu.Treeview', takefocus=False)
        self.tree.bind('<<TreeviewSelect>>', self._select_user)

        self.button_frame = tk.Frame(self, background='white')
        self.update_button = ttk.Button(self.button_frame, text='Обновить список', takefocus=False,
                                        command=self._update)
        self.disconnect_button = ttk.Button(self.button_frame, text='Отключить пользователя', takefocus=False,
                                            command=self.disconnect)
        # self.administrate_users_button = ttk.Button(self.button_frame, text='Администрирование', takefocus=False,
        #                                             command=self.open_adm)
        self.update_button.grid(row=0, column=0, padx=10, pady=2)
        self.disconnect_button.grid(row=0, column=1)
        # self.administrate_users_button.grid(row=0, column=2, padx=10)

        # стилизация Treeview и установка размера одного элемента на 25 пикс.
        s = ttk.Style()
        s.configure('qu.Treeview', rowheight=25)

        # скролл-бары
        self.scroll = ttk.Scrollbar(self, orient='vertical', command=self.tree.yview)
        self.scroll_x = ttk.Scrollbar(self, orient='horizontal', command=self.tree.xview)
        self.tree.configure(yscrollcommand=self.adaptive_scroller,
                            xscrollcommand=self.adaptive_scroller_x)

        self.img_offline = tk.PhotoImage(file='icons/offline_user.png')
        self.img_online = tk.PhotoImage(file='icons/online_user.png')

        # колонки (столбцы) списка
        self.tree.column('#0', stretch=False, width=60)
        self.tree.column('username', anchor='w')
        self.tree.column('ip', anchor='w')
        self.tree.column('last_online', stretch=False, anchor='w', minwidth=300)

        # названия колонок списка
        self.tree.heading('#0', text='Online')
        sort_name = self.sort_name_generator(0)
        self.tree.heading('username', text='Username', command=lambda: sort_name.__next__())
        sort_ip = self.sort_name_generator(1)
        self.tree.heading('last_online', text='Последнее посещение', command=lambda: sort_ip.__next__())
        self.tree.heading('ip', text='Адрес')

        # теги для присваивания иконки онлайна пользователю
        self.tree.tag_configure('offline', image=self.img_offline)  # хост не в сети
        self.tree.tag_configure('online', image=self.img_online)  # хост в сети

        # расстоновка всех виджетов (скролл_x, скролл_y, treeview)
        self.tree.grid(row=1, column=0, sticky='nsew')
        self.scroll.grid(row=1, column=1, sticky='ns')
        self.scroll_x.grid(row=2, column=0, sticky='we')
        self.button_frame.grid(row=0, column=0, sticky='w')

        # параметры расстягивания колонок и строк Treeview
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

    def adaptive_scroller(self, a, b):
        """Scroll_Y вызвает этот метод, при любом изменении размера виджета,
        или изменении количества находящихся в нём элементов.
        Нужен для авто-скрытия scroll-баров, когда в них нет нужды"""

        self.scroll.set(a, b)
        if float(b) == 1.0 and float(a) == 0.0:
            self.scroll.grid_remove()
        else:
            self.scroll.grid(row=1, column=1, sticky='ns')

    def adaptive_scroller_x(self, a, b):
        """Scroll_X вызвает этот метод, при любом изменении размера виджета,
        или изменении количества находящихся в нём элементов.
        Нужен для авто-скрытия scroll-баров, когда в них нет нужды"""

        self.scroll_x.set(a, b)
        if float(b) == 1.0 and float(a) == 0.0:
            self.scroll_x.grid_remove()
        else:
            self.scroll_x.grid(row=2, column=0, sticky='we')

    def sort_name_generator(self, sort):
        """генератор для сортировки элементов в списке"""
        revers = True
        while True:
            sorted_iids = []
            all_iids = self.tree.get_children()

            for iid in all_iids:
                name = self.tree.item(item=iid)['values']
                sorted_iids.append([name[sort], iid])

            sorted_iids = sorted(sorted_iids, key=lambda s: s[0], reverse=revers)

            for count, i in enumerate(sorted_iids):
                name, iid = i
                self.tree.move(iid, '', count)

            if revers:
                revers = False
            else:
                revers = True
            yield

    @staticmethod
    def open_adm():
        app.open_administrate()

    def _active_button(self):
        self.disconnect_button.configure(state=tk.NORMAL)

    def _disactive_button(self):
        self.disconnect_button.configure(state=tk.DISABLED)

    def _select_user(self, e=None):
        """при выборе пользователя кнопка активируется"""
        user = self.tree.selection()
        if user:
            self._active_button()

    def disconnect(self):
        """отключить пользователя от сервера"""
        user = self.tree.selection()
        val = self.tree.item(*user)['values'][1]
        if val:
            ip, port = val.split(' : ')
            r = api.DisconnectUser((ip, int(port)))
            handler_status_codes(app, r[0], reconnect=True)
            self._update()
        else:
            tk.messagebox.showwarning('Предупреждение', 'Не удалось отключить пользователя')

    def _update(self):
        """обновление списка пользователей"""
        self._disactive_button()  # откл.кнопку
        for i in self.tree.get_children():
            self.tree.delete(i)

        # запрос на сервер
        resp1 = api.GetRegUsers()
        if handler_status_codes(app, resp1[0], reconnect=False):
            # запрос на сервер
            resp2 = api.GetOnlineUsers()
            client_addr = resp2[1][0][0]
            print(resp2)
            if handler_status_codes(app, resp2[0], reconnect=False):
                users = resp1[1]
                online = [[i[0], i[2]] for i in resp2[1]]

                for user in online:
                    ip, port = user[0]
                    login = user[1]
                    print(ip, port, login)
                    usr = user[1]
                    while self.tree.exists(usr):
                        usr = usr + '!'

                    self.tree.insert('', iid=usr, index=tk.END,
                                     values=(login, f'{ip} : {port}', 'в сети'),
                                     tags=('online',))

                for user in users:
                    try:
                        time_change = datetime.fromtimestamp(user[2]).strftime('%H:%M:%S')
                        date_change = datetime.fromtimestamp(user[2]).strftime('%Y/%m/%d')
                    except TypeError:
                        time_change = ''
                        date_change = ''
                    if not self.tree.exists(user[0]):
                        self.tree.insert('', iid=user[0], index=tk.END,
                                         values=(f'{user[0]}', '', f'{date_change}  {time_change}'),
                                         tags=('offline',))

    def tab_event_notebook(self):
        """вызывается при перключении вкладок в родительском Notebook"""
        self._update()


class AdministrateUsers(tk.Frame):
    """Окно администрирования пользователей"""
    def __init__(self, parent):
        super().__init__(parent)

        self.temp_flag = True

        self.label_title = tk.Label(self, foreground='white', background='#4682B4',
                                    font=('Segoe UI', 15, 'bold'), text='Администрирование аккаунтов',
                                    width=50)

        self.button_frame = tk.Frame(self, height=30, background='white')

        self.add_img = tk.PhotoImage(file='icons/plus.png')
        self.remove_img = tk.PhotoImage(file='icons/cross.png')
        self.put_img = tk.PhotoImage(file='icons/pencil.png')
        self.update_img = tk.PhotoImage(file='icons/update_info.png')
        self.user_img = tk.PhotoImage(file='icons/user.png')

        self.add_button = BitmapButton(self.button_frame, self.add_img, width=30, height=30, background='white',
                                       command=lambda: CreateUserWindow(app))
        self.remove_button = BitmapButton(self.button_frame, self.remove_img, width=30, height=30, background='white',
                                          command=self.delete)
        self.update_button = BitmapButton(self.button_frame, self.update_img, width=30, height=30, background='white',
                                          command=self._update)

        self.add_button.grid(row=0, column=0, pady=2, padx=10)
        self.remove_button.grid(row=0, column=1,)
        self.update_button.grid(row=0, column=2, padx=10)

        self.tree = ttk.Treeview(self, columns=('username', 'access'),
                                 height=12, selectmode='browse', style='qi.Treeview', takefocus=False)

        self.tree.tag_configure('user', image=self.user_img)

        # обновить и заполнить список пользователями

        # стилизация Treeview и установка размера одного элемента на 25 пикс.
        s = ttk.Style()
        s.configure('qi.Treeview', rowheight=35)

        # скролл-бары
        self.scroll = ttk.Scrollbar(self, orient='vertical', command=self.tree.yview)
        self.scroll_x = ttk.Scrollbar(self, orient='horizontal', command=self.tree.xview)
        self.tree.configure(yscrollcommand=self.adaptive_scroller,
                            xscrollcommand=self.adaptive_scroller_x)

        # колонки (столбцы) списка
        self.tree.column('#0', width=60, stretch=False)
        self.tree.column('username', anchor='w', width=150)
        self.tree.column('access', anchor='w', width=150)

        # названия колонок списка
        sort_name = self.sort_name_generator(0)
        self.tree.heading('username', text='Username', command=lambda: sort_name.__next__())
        sort_ip = self.sort_name_generator(1)
        self.tree.heading('access', text='Уровень прав', command=lambda: sort_ip.__next__())

        # расстановка всех виджетов (скролл_x, скролл_y, treeview)
        self.label_title.grid(row=0, column=0, columnspan=2, sticky='we')
        self.button_frame.grid(row=1, column=0, columnspan=2, sticky='we')
        self.tree.grid(row=2, column=0, sticky='nsew')
        self.scroll.grid(row=2, column=1, sticky='ns')
        self.scroll_x.grid(row=3, column=0, sticky='we')

        # параметры расстягивания колонок и строк Treeview
        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)

    def update_frame(self):
        self._update()

    def adaptive_scroller(self, a, b):
        """Scroll_Y вызвает этот метод, при любом изменении размера виджета,
        или изменении количества находящихся в нём элементов.
        Нужен для авто-скрытия scroll-баров, когда в них нет нужды"""

        self.scroll.set(a, b)
        if float(b) == 1.0 and float(a) == 0.0:
            self.scroll.grid_remove()
        else:
            self.scroll.grid(row=2, column=1, sticky='ns')

    def adaptive_scroller_x(self, a, b):
        """Scroll_X вызвает этот метод, при любом изменении размера виджета,
        или изменении количества находящихся в нём элементов.
        Нужен для авто-скрытия scroll-баров, когда в них нет нужды"""

        self.scroll_x.set(a, b)
        if float(b) == 1.0 and float(a) == 0.0:
            self.scroll_x.grid_remove()
        else:
            self.scroll_x.grid(row=3, column=0, sticky='we')

    def sort_name_generator(self, sort):
        """генератор для сортировки элементов в списке"""
        revers = True
        while True:
            sorted_iids = []
            all_iids = self.tree.get_children()

            for iid in all_iids:
                name = self.tree.item(item=iid)['values']
                sorted_iids.append([name[sort], iid])

            sorted_iids = sorted(sorted_iids, key=lambda s: s[0], reverse=revers)

            for count, i in enumerate(sorted_iids):
                name, iid = i
                self.tree.move(iid, '', count)

            if revers:
                revers = False
            else:
                revers = True
            yield

    def _update(self):
        """обновить список пользователей"""
        self.tree.delete(*self.tree.get_children())  # удаление элементов из treeview
        response = api.GetRegUsers()
        if handler_status_codes(app, response[0], show='bad', reconnect=False):
            for user in response[1]:
                if user[1] == 'admin':
                    access = 'Администратор'
                else:
                    access = 'Пользователь'
                self.tree.insert('', tk.END, values=(user[0], access,), tags=('user',), iid=user[0])

    def delete(self):
        """удалить пользователя из БД сервера"""
        user = self.tree.selection()
        if user:
            ask = tk.messagebox.askyesno('Удаление пользователя',
                                         f'Вы действительно хотите удалть пользователя: "{user[0]}"', parent=self)
            if ask:
                response = api.DeleteUser(*user)
                if handler_status_codes(self, response[0], 'bad', reconnect=False):
                    self._update()
        else:
            tk.messagebox.showwarning('Пользователь не выбран', 'Для удаления пользователя выберите его из списка',
                                      parent=self)


class IcmpServerSettings(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, background='white')
        self.label_title = tk.Label(self, foreground='white', background='#4682B4',
                                    font=('Segoe UI', 15, 'bold'), text='Параметры ICMP',
                                    width=50)

        self.button_frame = tk.Frame(self, height=30, background='white')

        self.img_update = tk.PhotoImage(file='icons/update_info.png')
        self.img_confirm = tk.PhotoImage(file='icons/confirm.png')
        self.button_update = BitmapButton(self.button_frame, width=30, height=30, img=self.img_update,
                                          background='white', command=self.update_settings)
        self.button_confirm = BitmapButton(self.button_frame, width=30, height=30, img=self.img_confirm,
                                           background='white', command=self.confirm_settings)
        self.button_update.grid(row=0, column=1, padx=5)
        self.button_confirm.grid(row=0, column=0, padx=5)

        self.style = ttk.Style()
        self.style.configure('Horizontal.TScale', background='white')
        self.style.configure('A.TLabel', background='white')
        self.style.configure('A.TLabel', background='white')
        self.style.configure('S.TLabel', background='white', font=('Segoe UI', 9, 'bold'))

        self.label_title.grid(row=0, column=0, sticky='we', columnspan=2)
        self.button_frame.grid(row=1, column=0, pady=2, sticky='w', columnspan=2)

        self.columnconfigure(0, weight=1)

        self.group_frame1 = tk.Frame(self, background='white')
        self.label_auto_ping = ttk.Label(self.group_frame1, text='Авто проверка всех хостов каждые:', style='A.TLabel')
        self._label_auto_ping = ttk.Label(self.group_frame1, text='0', style='S.TLabel')
        self.scale_auto_ping = ttk.Scale(self, from_=60, to=600, command=self._update_auto_ping)

        self.group_frame2 = tk.Frame(self, background='white')
        self.label_speed_ping = ttk.Label(self.group_frame2, text='Скорость проверки:', style='A.TLabel')
        self._label_speed_ping = ttk.Label(self.group_frame2, text='0', style='S.TLabel')
        self.scale_speed_ping = ttk.Scale(self, from_=1, to=100, command=self._update_speed_ping)

        self.group_frame3 = tk.Frame(self, background='white')
        self.label_count_icmp = ttk.Label(self.group_frame3, text='Количество ICMP пакетов на хост:', style='A.TLabel')
        self._label_count_icmp = ttk.Label(self.group_frame3, text='0', style='S.TLabel')
        self.scale_count_icmp = ttk.Scale(self, from_=1, to=10, command=self._update_count_ping)

        self.group_frame4 = tk.Frame(self, background='white')
        self.label_delay_icmp = ttk.Label(self.group_frame4, text='Временной интервал между ICMP пакетами:',
                                          style='A.TLabel')
        self._label_delay_icmp = ttk.Label(self.group_frame4, text='0', style='S.TLabel')
        self.scale_delay_icmp = ttk.Scale(self, from_=1, to=10, command=self._update_delay_ping)

        self.group_frame5 = tk.Frame(self, background='white')
        self.label_timeout_icmp = ttk.Label(self.group_frame5, text='Timeout ICMP ответа:', style='A.TLabel')
        self._label_timeout_icmp = ttk.Label(self.group_frame5, text='0', style='S.TLabel')
        self.scale_timeout_icmp = ttk.Scale(self, from_=1, to=10, command=self._update_timeout_ping)

        self.label_auto_ping.grid(row=0, column=0, sticky='w')
        self._label_auto_ping.grid(row=0, column=1, sticky='w')

        self.label_speed_ping.grid(row=0, column=0, sticky='w')
        self._label_speed_ping.grid(row=0, column=1, sticky='w')

        self.label_count_icmp.grid(row=0, column=0, sticky='w')
        self._label_count_icmp.grid(row=0, column=1, sticky='w')

        self.label_delay_icmp.grid(row=0, column=0, sticky='w')
        self._label_delay_icmp.grid(row=0, column=1, sticky='w')

        self.label_timeout_icmp.grid(row=0, column=0, sticky='w')
        self._label_timeout_icmp.grid(row=0, column=1, sticky='w')

        self.group_frame1.grid(row=3, column=0, sticky='we')
        self.scale_auto_ping.grid(row=4, column=0, sticky='we', pady=5)
        self.group_frame2.grid(row=5, column=0, sticky='we')
        self.scale_speed_ping.grid(row=6, column=0, sticky='we', pady=5)
        self.group_frame3.grid(row=7, column=0, sticky='we')
        self.scale_count_icmp.grid(row=8, column=0, sticky='we', pady=5)
        self.group_frame4.grid(row=9, column=0, sticky='we')
        self.scale_delay_icmp.grid(row=10, column=0, sticky='we', pady=5)
        self.group_frame5.grid(row=11, column=0, sticky='we')
        self.scale_timeout_icmp.grid(row=12, column=0, sticky='we', pady=5)

    def _update_auto_ping(self, x):
        self._label_auto_ping['text'] = f'{int(float(x))} секунд'

    def _update_speed_ping(self, x):
        self._label_speed_ping['text'] = f'{int(float(x))} хостов/сек'

    def _update_count_ping(self, x):
        self._label_count_icmp['text'] = f'{int(float(x))} шт.'

    def _update_delay_ping(self, x):
        self._label_delay_icmp['text'] = f'{int(float(x))} секунд'

    def _update_timeout_ping(self, x):
        self._label_timeout_icmp['text'] = f'{int(float(x))} секунд'

    def update_settings(self):
        """получить параметры icmp с сервера и отобразить"""
        response = api.GetParamsICMP()
        if handler_status_codes(app, response[0], 'bad', reconnect=False):
            params = response[1]

            self.scale_auto_ping.set(params[0])
            self.scale_count_icmp.set(params[1])
            self.scale_delay_icmp.set(params[2])
            self.scale_speed_ping.set(params[3])
            self.scale_timeout_icmp.set(params[4])

    def confirm_settings(self):
        """отправить изменённые icmp параметры на сервер"""

        responses = [api.AutoPingInterval(int(float(self.scale_auto_ping.get()))),
                     api.ICMPWithHost(int(float(self.scale_count_icmp.get()))),
                     api.ICMPInterval(int(float(self.scale_delay_icmp.get()))),
                     api.CheckedHostPerSecond(int(float(self.scale_speed_ping.get()))),
                     api.ICMPTimeout(int(float(self.scale_timeout_icmp.get())))]

        for response in responses:
            if handler_status_codes(app, response[0], show='bad', reconnect=False):
                continue
            else:
                return
        tk.messagebox.showinfo('Запрос обработан', 'Параметры успешно сохранены на сервере', parent=app)


class Notify(tk.Toplevel):
    def __init__(self, parent, data, ip, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.geometry(center_window(self, 600, 240))
        self.parent = parent
        self.parent.open_window = self
        self.grab_set()
        self.online_sms = tk.BooleanVar()
        self.offline_sms = tk.BooleanVar()
        self.double_check = tk.BooleanVar()
        self.online_sms.set(False)
        self.offline_sms.set(False)
        self.double_check.set(False)
        self.data = data
        self.ip = ip

        self.group_frame = tk.Frame(self)

        self.label_off_host = tk.Label(self, font=('Segoe UI', 10, 'bold'), foreground='white', background='grey50',
                                       text='Действия при отключении хоста')
        self.label_on_host = tk.Label(self, font=('Segoe UI', 10, 'bold'), foreground='white', background='grey50',
                                      text='Действия при включении хоста')

        self.check_enable = ttk.Checkbutton(self, text='Включено', variable=self.offline_sms)
        self.check_double_ping = ttk.Checkbutton(self,
                                                 text='Дополнительная проверка перед отправкой SMS\n'
                                                      '(5 пинг-запросов через 30 секунд после отключения хоста)',
                                                 variable=self.double_check)

        self.group_frame_1 = tk.Frame(self)
        self.entry_url = EntryWithMenu(self.group_frame_1)
        self.label_url = tk.Label(self.group_frame_1, text='URL API:')
        self.label_url.grid(row=0, column=0)
        self.entry_url.grid(row=0, column=1, sticky='we')
        self.group_frame_1.columnconfigure(1, weight=1)

        self.test_button = ttk.Button(self, text='Пробная отправка SMS')

        self.check_enable_1 = ttk.Checkbutton(self, text='Включено', variable=self.online_sms)
        self.group_frame_2 = tk.Frame(self)
        self.entry_url_on = EntryWithMenu(self.group_frame_2)
        self.label_url_on = tk.Label(self.group_frame_2, text='URL API:')
        self.label_url_on.grid(row=0, column=0)
        self.entry_url_on.grid(row=0, column=1, sticky='we')
        self.group_frame_2.columnconfigure(1, weight=1)

        self.test_button_1 = ttk.Button(self, text='Пробная отправка SMS')

        self.group_frame_3 = tk.Frame(self)
        self.confirm_button = ttk.Button(self.group_frame_3, text='Сохранить', command=self.confirm)
        self.close_button = ttk.Button(self.group_frame_3, text='Отмена', command=self.destroy)
        self.reset_button = ttk.Button(self.group_frame_3, text='Сброс', command=self.reset)
        self.confirm_button.grid(row=0, column=1, pady=10, padx=5)
        self.close_button.grid(row=0, column=2, pady=5, padx=5)
        self.reset_button.grid(row=0, column=0, pady=5, padx=5)

        self.label_off_host.grid(row=0, column=0, sticky='we')
        self.check_enable.grid(row=1, column=0, sticky='w', padx=10)
        self.check_double_ping.grid(row=2, column=0, sticky='w', padx=10)
        self.group_frame_1.grid(row=3, column=0, sticky='we', pady=5, padx=5)
        self.label_on_host.grid(row=5, column=0, sticky='we')
        self.check_enable_1.grid(row=6, column=0, sticky='we', padx=10)
        self.group_frame_2.grid(row=7, column=0, sticky='we', pady=5, padx=5)
        self.group_frame_3.grid(row=9, column=0, sticky='e')

        self.columnconfigure(0, weight=1)

        self.update_data()

    def update_data(self):
        try:
            self.data = json.loads(self.data)
        except (json.JSONDecodeError, TypeError):
            pass
        if type(self.data) is dict:
            self.offline_sms.set(self.data['offline'])
            self.online_sms.set(self.data['online'])
            self.double_check.set(self.data['double_check'])
            self.entry_url.insert(tk.END, self.data['offline_url'])
            self.entry_url_on.insert(tk.END, self.data['online_url'])

        elif self.data is None:
            pass
        else:
            tk.messagebox.showwarning('Ошибка', 'Не удалось загрузить данные SMS оповещений', parent=self)
            self.destroy()

    def confirm(self):
        if not self.offline_sms.get() and not self.online_sms.get():
            if not self.entry_url.get() and not self.entry_url_on.get():
                response = api.PutHost(self.ip, sms='')
                if handler_status_codes(self, status=response[0], show='bad', reconnect=False):
                    app.monitoring_frame.host_info.update_data(self.ip)
                    self.destroy()
                    return
                else:
                    tk.messagebox.showerror('Ошибка Server.API', 'Попробуйте повторить позже.', parent=self)
                    self.destroy()

        if self.offline_sms.get() and not self.entry_url.get():
            tk.messagebox.showwarning('Неккоректные данные', 'Поле URL не должно быть пустым', parent=self)
            return
        if self.online_sms.get() and not self.entry_url_on.get():
            tk.messagebox.showwarning('Неккоректные данные', 'Поле URL не должно быть пустым', parent=self)
            return

        sms_params = {
            'offline': self.offline_sms.get(),
            'online': self.online_sms.get(),
            'double_check': self.double_check.get(),
            'offline_url': self.entry_url.get(),
            'online_url': self.entry_url_on.get()
        }
        sms_params = json.dumps(sms_params)

        response = api.PutHost(self.ip, sms=sms_params)
        if handler_status_codes(self, status=response[0], show='all', reconnect=False):
            app.monitoring_frame.host_info.update_data(self.ip)
            self.destroy()
        else:
            tk.messagebox.showerror('Ошибка Server.API', 'Попробуйте повторить позже.', parent=self)
            self.destroy()

    def reset(self):
        """сброс всех флажков и полей"""
        self.offline_sms.set(False)
        self.online_sms.set(False)
        self.double_check.set(False)
        self.entry_url.delete(0, tk.END)
        self.entry_url_on.delete(0, tk.END)


class CreateUserWindow(tk.Toplevel):
    """Окно создания нового пользователя"""
    def __init__(self, parent):
        super().__init__(parent)
        self.grab_set()
        self.parent = parent
        self.geometry(center_window(parent, 400, 170))
        self.var_access = tk.StringVar()
        self.var_access.set('guest')
        self.protocol('WM_DELETE_WINDOW', self.close_window)

        self.entry_login = EntryWithMenu(self)
        self.label_login = ttk.Label(self, text='Логин:', width=15, anchor='e')
        self.entry_passw = EntryWithMenu(self)
        self.label_passw = ttk.Label(self, text='Пароль:', width=15, anchor='e')
        self.label_access = ttk.Label(self, text='Уровень прав:', width=15, anchor='e')
        self.radiobtn_admin = ttk.Radiobutton(self, text='Администратор', variable=self.var_access, value='admin',
                                              takefocus=False)
        self.radiobtn_user = ttk.Radiobutton(self, text='Пользователь', variable=self.var_access, value='guest',
                                             takefocus=False)

        self.frame_btns = tk.Frame(self)
        self.button_confirm = ttk.Button(self.frame_btns, text='Создать', command=self.confirm, takefocus=False,
                                         width=10)
        self.button_close = ttk.Button(self.frame_btns, text='Отмена', command=self.close_window, takefocus=False,
                                       width=10)

        self.button_close.grid(row=0, column=1, padx=20)
        self.button_confirm.grid(row=0, column=0)

        self.label_login.grid(row=0, column=0)
        self.entry_login.grid(row=0, column=1, sticky='nsew', padx=20, pady=10)
        self.label_passw.grid(row=1, column=0)
        self.entry_passw.grid(row=1, column=1, sticky='nsew', padx=20)
        self.label_access.grid(row=2, column=0, pady=10)
        self.radiobtn_admin.grid(row=2, column=1, sticky='w', padx=20)
        self.radiobtn_user.grid(row=3, column=1, sticky='w', padx=20)
        self.frame_btns.grid(row=4, column=1, sticky='e', pady=10)

        self.columnconfigure(1, weight=1)

    def confirm(self):
        login = self.entry_login.get()
        passw = self.entry_passw.get()

        if len(login) < 3:
            tk.messagebox.showwarning('Короткий логин', 'Логин должен состоять минимум из 3 символов', parent=self)
            return
        if len(passw) < 5:
            tk.messagebox.showwarning('Короткий пароль', 'Пароль должен состоять минимум из 5 символов', parent=self)
            return

        access = self.var_access.get()

        response = api.CreateUser(login, passw, access)
        if handler_status_codes(self, response[0], show='all', reconnect=False):
            self.close_window()

    def close_window(self):
        app.users.update_frame()
        self.destroy()


class Monitoring(tk.Frame):
    """Фрейм мониторинга

    Основные элементы:
    - список хостов
    - список папок
    - лог сервера
    - информационное поле"""

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.parent = parent

        self.frame_button_adm = tk.Frame(self, background='white')
        self.frame_button_adm.pack(side='top', anchor='nw', pady=1)

        #  фрейм для группировки кнопок bitmaps
        self.frame_buttons = tk.Frame(self)
        self.frame_buttons.pack(side='top', pady=3, fill='x')

        # основная динамическая панель
        self.mainPanedWindow = tk.PanedWindow(self, orient='vertical', bd=0, sashwidth=3, sashrelief='flat',)
        self.mainPanedWindow.pack(side='top', fill='both', expand=1)  # упаковка во фрейм

        # дочерние верхняя и нижняя панели
        self.upPanedWindow = tk.PanedWindow(self, orient='horizontal', bd=0, sashwidth=3, sashrelief='flat')
        self.downPanedWindow = tk.PanedWindow(self, orient='horizontal', bd=0, sashwidth=3, sashrelief='flat')
        # размещение дочерних панелей в родительскую
        self.mainPanedWindow.add(self.upPanedWindow, stretch='always')
        self.mainPanedWindow.add(self.downPanedWindow, stretch='never')

        self.log = NoteBookLog(self.downPanedWindow)
        self.host_list = TableHosts(self.upPanedWindow)
        self.folder_list = TableFolders(self.upPanedWindow)
        self.host_info = HostInfo(self.downPanedWindow)

        self.upPanedWindow.add(self.folder_list)
        self.upPanedWindow.add(self.host_list)
        self.downPanedWindow.add(self.log, stretch='always')
        self.downPanedWindow.add(self.host_info, stretch='never')

        #  список кнопок и список иконок к ним
        self.bitmaps = []
        self.img_paths = (
            'icons/create_folder.png',
            'icons/delete_folder.png',
            'icons/put_folder.png',
            'icons/update_folder.png',
            '--separator',
            '--separator',
            'icons/create_host.png',
            'icons/delete_host.png',
            'icons/pause_host.png',
            'icons/play_host.png',
            '--separator',
            '--separator',
            'icons/check_all.png',
            'icons/check_dead.png',
            '--separator',
            '--separator',
            'icons/info.png'
        )

        self.command_lst = (
            self.folder_list.create_folder_in_server,
            self.folder_list.delete_folder_in_server,
            self.folder_list.rename_folder_in_server,
            self.folder_list.update_folders,
            lambda: CreateHostWindow(app),
            self.host_list.delete_host_in_server,
            self.host_list.set_pause_host,
            self.host_list.set_play_host,
            api.PingALL,
            api.PingDEAD,
            lambda: AuthorWindow(app)
        )

        cmds = self._get_command()

        # создание кнопок
        for i in self.img_paths:
            if i == '--separator':
                bitmap = i
            else:
                bitmap = BitmapButton(self.frame_buttons, img=tk.PhotoImage(file=i), width=30, height=30,
                                      command=cmds.__next__())
            self.bitmaps.append(bitmap)

        # размещение кнопок
        for column, bitmap in enumerate(self.bitmaps):
            if bitmap == '--separator':
                bitmap = ttk.Separator(self.frame_buttons, orient='vertical')
            bitmap.grid(row=1, column=column, padx=2, sticky='ns')

        self.empty_frame = ttk.Frame(self.frame_buttons)
        self.empty_frame.grid(row=1, column=len(self.bitmaps), sticky='we')
        self.frame_buttons.columnconfigure(len(self.bitmaps), weight=1)

        self.label_filter = ttk.Label(self.frame_buttons, text='Поиск:')
        self.label_filter.grid(row=1, column=len(self.bitmaps)+1, sticky='we')
        self.entry_filter = ttk.Entry(self.frame_buttons)
        self.entry_filter.grid(row=1, column=len(self.bitmaps)+2, sticky='we', padx=5)

        self.img_user = tk.PhotoImage(file='icons/user_adm.png')
        self.img_icmp = tk.PhotoImage(file='icons/icmp_adm.png')
        self.img_sms = tk.PhotoImage(file='icons/sms_adm.png')

    def _get_command(self):
        """Получить комманду (callback) из генератора
        для кнопки"""
        for i in self.command_lst:
            yield i

    def get_filter(self):
        """получить данные из строки фильтра хостов"""
        return self.entry_filter.get()


class Status(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.parent = parent

        self.label_delay = ttk.Label(self, text='Задержка сервера, мс:')
        self.entry_delay = tk.Label(self, width=10, bd=1, relief='sunken', textvariable=self.parent.delay_server)

        self.label_rx = ttk.Label(self, text='Принято, Мб:')
        self.entry_rx = tk.Label(self, width=10, bd=1, relief='sunken', textvariable=self.parent.rx_bytes)

        self.label_tx = ttk.Label(self, text='Отправлено, Мб:')
        self.entry_tx = tk.Label(self, width=10, bd=1, relief='sunken', textvariable=self.parent.tx_bytes)

        self.label_user = ttk.Label(self, text='Текущий пользователь:')
        self.entry_user = tk.Label(self, width=20, bd=1, relief='sunken', textvariable=self.parent.current_user)

        self.label_uptime = ttk.Label(self, text='Uptime сервера:')
        self.entry_uptime = tk.Label(self, width=20, bd=1, relief='sunken', textvariable=self.parent.uptime)

        self.label_user.grid(row=0, column=0, padx=2)
        self.entry_user.grid(row=0, column=1)
        self.label_tx.grid(row=0, column=2, padx=2)
        self.entry_tx.grid(row=0, column=3)
        self.label_rx.grid(row=0, column=4, padx=2)
        self.entry_rx.grid(row=0, column=5)
        self.label_delay.grid(row=0, column=6, padx=2)
        self.entry_delay.grid(row=0, column=7)
        self.label_uptime.grid(row=0, column=8, padx=2)
        self.entry_uptime.grid(row=0, column=9)


class AuthorWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.geometry(center_window(self, 400, 250))
        # self.iconphoto(True, tk.PhotoImage(file='icons/info16x16.png'))
        # self.iconbitmap('icons/info16x16.ico')
        self.title('Информация')
        self.grab_set()
        self.resizable(False, False)
        self.config(background='white')
        app.open_window = self

        self.columnconfigure(0, weight=1)

        self.label = tk.Label(self, text='DEIL EYE (система ICMP мониторинга)',
                              background='#006400', foreground='white', font=('Segoe UI', 10, 'bold'))
        self.label.grid(row=0, column=0, sticky='we')

        self.text = tk.Text(self, font=('Segoe UI', 9), height=5, bd=2)
        self.text.insert('1.0', 'Данное ПО создано для мониторинга состояния сети\n')
        self.text.insert('2.0', 'и основывается на клиент-серверной архитектуре.\n')
        self.text.insert('3.0', 'В неё включены: система авторизации, база данных (SQLite),\n')
        self.text.insert('4.0', 'разделение прав пользователей, свой API/протокол повехр TCP/IP,\n')
        self.text.insert('5.0', 'система SMS оповещений через URL запросы')
        self.text['state'] = tk.DISABLED

        self.frame1 = tk.Frame(self, background='white')
        self.label_author = tk.Label(self.frame1, text='Создатель системы:', background='white', width=20)
        self.entry_author1 = tk.Text(self.frame1, bd=2, width=30, height=1, font=('Segoe UI', 9))
        self.entry_author1.insert('1.0', 'Ситников Артём')
        self.label_author.grid(row=0, column=0)
        self.entry_author1.grid(row=0, column=1)

        self.frame2 = tk.Frame(self, background='white')
        self.label_author2 = tk.Label(self.frame2, text='Профиль VK:', background='white', width=20)
        self.entry_author3 = tk.Text(self.frame2, bd=2, width=30, height=1, font=('Segoe UI', 9))
        self.entry_author3.insert('1.0', 'vk.com/mrsitt')
        self.label_author2.grid(row=0, column=0)
        self.entry_author3.grid(row=0, column=1)

        self.frame3 = tk.Frame(self, background='white')
        self.label_author3 = tk.Label(self.frame3, text='Эл.Почта:', background='white', width=20)
        self.entry_author4 = tk.Text(self.frame3, bd=2, width=30, height=1, font=('Segoe UI', 9))
        self.entry_author4.insert('1.0', 'mrsit8281@yandex.ru')
        self.label_author3.grid(row=0, column=0)
        self.entry_author4.grid(row=0, column=1)

        self.entry_author1['state'] = tk.DISABLED
        self.entry_author3['state'] = tk.DISABLED
        self.entry_author4['state'] = tk.DISABLED

        self.img = tk.PhotoImage(file='icons/server_erch.png')
        self.label_provider = tk.Label(self, text='Разработанно специально для\nоператора связи ООО «Дейл-телеком»',
                                       font=('Sogoe UI', 9, 'italic'), relief='raised', image=self.img,
                                       compound='left')

        self.text.grid(row=1, column=0, padx=10, pady=10)
        self.frame1.grid(row=2, column=0, pady=2, sticky='w')
        self.frame2.grid(row=3, column=0, pady=2, sticky='w')
        self.frame3.grid(row=4, column=0, pady=2, sticky='w')
        self.label_provider.grid(row=5, column=0, pady=10)


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.geometry(center_window_adaptive(self, 1200, 800))  # центровка окна и адаптация под разрешение экрана
        self.config(menu=MainMenu(self))  # основное верхнее меню
        self.title('Deil Eye (программа мониторинга сети)')
        self.iconphoto(True, tk.PhotoImage(file='icons/server16x16.png'))
        self.open_window = None  # если соществует открытый Toplevel то его объект помещается сюда
        self.protocol('WM_DELETE_WINDOW', self.close_window)

        # self.style = ttk.Style()
        # self.style.theme_use('winnative')

        self.delay_server = tk.StringVar()
        self.rx_bytes = tk.StringVar()
        self.tx_bytes = tk.StringVar()
        self.current_user = tk.StringVar()
        self.uptime = tk.StringVar()

        self.stop_afters = False
        self.notebook = NoteBook(self)
        self.notebook.bind('<<NotebookTabChanged>>', self.update_notebook)
        self.status_frame = Status(self)

        # фрейм мониторинга (папки, хосты, лог и т.д)
        self.monitoring_frame = Monitoring(self.notebook)

        self.settings_frame = tk.Frame(self.notebook, background='white')
        self.users = AdministrateUsers(self.settings_frame)
        self.users.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)
        self.icmp = IcmpServerSettings(self.settings_frame)
        self.icmp.grid(row=0, column=1, sticky='nsew', padx=5, pady=5)
        # self.notify = Notify(self.settings_frame)
        # self.notify.grid(row=1, column=0, columnspan=2, sticky='nsew')

        self.settings_frame.columnconfigure(0, weight=1)
        self.settings_frame.columnconfigure(1, weight=1)
        #
        self.settings_frame.rowconfigure(0, weight=1)
        # self.settings_frame.rowconfigure(1, weight=1)

        # фрейм настройки SMS оповещений

        # вкладки: Мониторинг, Администрирование, SMS оповещения
        self.img_monitoring = tk.PhotoImage(file='icons/monitoring.png')
        self.img_params = tk.PhotoImage(file='icons/server_settings.png')
        self.img_sms = tk.PhotoImage(file='icons/sms_adm.png')
        self.notebook.add(self.monitoring_frame, text='  Мониторинг  ', image=self.img_monitoring, compound='left')
        self.notebook.add(self.settings_frame, text='  Параметры ICMP/  \n  Администрирование  ', image=self.img_params,
                          compound='left')

        self.notebook.grid(row=0, column=0, sticky='nsew')
        self.status_frame.grid(row=1, column=0, sticky='we')

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        AuthorizedWindow(self)  # окно авторизации (скрывает родительское)

    def close_window(self):
        """обработка закрытия окна"""
        alrm = self.monitoring_frame.log.log.alarm.get()
        usr = self.monitoring_frame.log.log.users.get()
        icmp = self.monitoring_frame.log.log.icmp.get()
        print(alrm, usr, icmp)
        save_temp_data(check1=icmp, check2=usr, check3=alrm)
        self.destroy()

    def update_notebook(self, e=None):
        """обновить выбранный фрейм в виджете ноутбук"""
        frame = self.notebook.index(self.notebook.select())
        if frame == 1:
            self.icmp.update_settings()
            self.users.update_frame()

    def open_administrate(self):
        """открыть окно администрироваия аккаунтов"""
        AdministrateUsers(self)

    def run_loop(self):
        """Вызывается при подключении к серверу или
        переподключении, запускает необходииые циклы обновления,
        снимает блокировку с обновляющих циклов
        """
        self.stop_afters = False
        self.monitoring_frame.folder_list.update_folders()
        self.monitoring_frame.host_list.update_hosts()
        self.monitoring_frame.log.log.log_update_loop()

    def stop_loop(self):
        """Вызывается если нужно запустить циклы обновления данных"""
        self.stop_afters = True

    def server_connection_lost(self):
        """При потере соединения вызвается этот метод или
        при плановом отключении от сервера
        """
        try:
            self.open_window.destroy()
        except (tk.TclError, AttributeError):
            pass
        self.stop_loop()  # остановить циклы обновления
        self.monitoring_frame.folder_list.delete_folders()
        self.monitoring_frame.host_list.delete_hosts()
        api.connection_close()
        auth_win = AuthorizedWindow(self)  # окно авторизации (скрывает родительское)
        return auth_win

    def save_file_hosts(self, file: str):
        """Сохранить CSV-файл или TXT-файл со списком всех хостов из базы данных сервера"""
        response = api.GetAllHosts()
        if handler_status_codes(self, reconnect=False, status=response[0]):
            if file == 'csv':
                name_path = filedialog.asksaveasfilename(defaultextension='.csv', filetypes=(('CSV файлы', '*.csv'),),
                                                         initialfile='host_list')
                if not name_path:
                    return
                with open(name_path, mode='w', encoding='utf-16') as file:
                    file_w = csv.writer(file, lineterminator="\r")
                    for i in response[1]:
                        file_w.writerow([i[0], i[1], i[3]])
            elif file == 'txt':
                big_len_name = 0
                big_len_ip = 18
                big_len_state = 8
                for i in response[1]:
                    current_len = len(i[1])
                    if current_len > big_len_name:
                        big_len_name = current_len
                name_path = filedialog.asksaveasfilename(defaultextension='.txt', filetypes=(('TXT файлы', '*.txt'),),
                                                         initialfile='host_list')
                if not name_path:
                    return
                with open(name_path, mode='w', encoding='utf-8') as file:
                    for i in response[1]:
                        ip_offset = big_len_ip - len(i[0])
                        name_offset = big_len_name + 3 - len(i[1])
                        state_offset = big_len_state - len(i[3])
                        file.write(f'''{i[0]+' '*ip_offset}{i[1]+' '*name_offset}{i[3]+' '*state_offset}\n''')


if __name__ == '__main__':
    api = DeilEyeAPI()  # API для взаимодействия с сервером
    app = App()
    app.mainloop()
