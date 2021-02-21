# -*- coding: utf-8 -*-
'''
Simple Raspberry Pi Controller
'''
import sys, os, subprocess, traceback, types
from datetime import datetime, timedelta
import threading, queue
import serial, time, codecs, sqlite3

import random
# from Crypto.Cipher import AES - 윈도우에서 설치 에러남. 걍 안쓸란다

import kivy
kivy.require('1.10.0')

from kivy.app import App
from kivy.lang import Builder
from kivy.core.text import LabelBase, DEFAULT_FONT
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.tabbedpanel import TabbedPanel
from kivy.uix.popup import Popup
from kivy.config import Config
from kivy.graphics import BorderImage
from kivy.uix.screenmanager import Screen, ScreenManager, NoTransition
# from kivy.properties import StringProperty, NumericProperty, ObjectProperty
from kivy.properties import *

# from screen_manager import ScreenHome, ScreenEther, ScreenDisp, ScreenManagement, ScreenManager, Screen
from screen_manager import *

debug_mode = False

# 윈도우버전 파이썬 버그 대응: OSError: raw write() returned invalid length
if sys.platform == 'win32':
    import win_unicode_console
    win_unicode_console.enable()
elif sys.platform.startswith('linux'):
    from bluedot.btcomm import BluetoothServer
    os.system('sudo bash -c "echo 0 > /sys/class/backlight/rpi_backlight/bl_power"')

if len(sys.argv) > 1:
    if "debug" in sys.argv[1:]:
        debug_mode = True
    if "rotate" in sys.argv[1:]:
        Config.set('graphics', 'rotation', '180')

# 화면 설정
Config.set('graphics', 'width', '800')
Config.set('graphics', 'height', '480')
Config.set('graphics','resizable',0)

# 기본 글꼴 설정: https://kivy.org/docs/_modules/kivy/core/text.html
LabelBase.register(
    DEFAULT_FONT,
    # name="default",
    fn_regular="./fonts/NanumGothicCoding-Regular.ttf",
    fn_bold="./fonts/NanumGothicCoding-Bold.ttf",
    fn_italic="./fonts/NanumGothicCoding-Regular.ttf",
    fn_bolditalic="./fonts/NanumGothicCoding-Bold.ttf"
)


# 마우스 멀티터치 비활성 - 마우스 우클릭시 주황색 원형 마크가 생성되는 것 방지 목적
Config.set('input', 'mouse', 'mouse,multitouch_on_demand')


class ThreadFlask:
    is_running = True

    def __init__(self):
        self.thread = threading.Timer(1, self.queueToServer)

    def queueToServer(self, mode = "none"):
        if (mode == "start"):
            self.thread.start()
        elif (mode == "stop"):
            self.thread.cancel()
        else:
            while self.is_running == True:
                if flask.que_from_kivy.qsize() > 0:
                    self.que_data = flask.que_from_kivy.get_nowait()
                    print("Queue from Kivy:: " + self.que_data)

                time.sleep(0.05)

            self.thread.cancel()

class ThreadKivy:
    is_running = True

    def __init__(self):
        self.datetime_thread = threading.Timer(1, self.threadDateTime)
        self.flaskqueue_thread = threading.Timer(1, self.queueToDevice)

    def threadDateTime(self, mode = "none"):
        thread = self.datetime_thread
        if (mode == "start"):
            thread.start()
        elif (mode == "stop"):
            thread.cancel()
        else:
            current_screen = app_main.scm.children[0]
            while self.is_running == True:
                now = datetime.now()
                current_screen.ids.current_date.text =\
                            '%s-%s-%s' % (\
                            '{:04d}'.format(now.year),\
                            '{:02d}'.format(now.month),\
                            '{:02d}'.format(now.day))
                current_screen.ids.current_time.text =\
                        time.strftime('%H:%M:%S')

                time.sleep(1)

            thread.cancel()

    def queueToDevice(self, mode = "none"):
        thread = self.flaskqueue_thread
        if (mode == "start"):
            thread.start()
        elif (mode == "stop"):
            thread.cancel()
        else:
            while self.is_running == True:
                if app_main.que.qsize() > 0:
                    self.que_data = app_main.que.get_nowait()
                    print("Queue from Flask:: " + self.que_data)
                    # app_main.que_to_flask.put(self.que_data)

                    data = self.que_data.split(":")
                    if data[0] == "Brightness":
                        print("^_^_^_^::" + data[1].strip())
                        

                time.sleep(0.05)

            thread.cancel()

class AppMain(App):
    th_obj = ""

    def build(self):
        # 빈창 띄우는 범인: flask - 어케 해결하지?
        # self.que = Manager().Queue()
        # self.que_to_flask = Manager().Queue()

        # self.flask_proc = Process(target=flaskRun, args=(self.que, self.que_to_flask))
        # self.flask_proc.start()

        f = []
        f.append(open("layout/main.kv", encoding='utf8'))
        f.append(open("layout/aprow.kv", encoding='utf8'))
        f.append(open("layout/btrow.kv", encoding='utf8'))
        f.append(open("layout/home.kv", encoding='utf8'))
        f.append(open("layout/menu.kv", encoding='utf8'))
        f.append(open("layout/ether.kv", encoding='utf8'))
        f.append(open("layout/bluetooth.kv", encoding='utf8'))
        f.append(open("layout/disp.kv", encoding='utf8'))

        content = ''
        for i in f:
            content += i.read() + "\r\n"
            i.close()

        Builder.load_string(content)
        self.scm = ScreenManagement()
        self.scm.transition = NoTransition()

        self.triggerThreads()

        if sys.platform == 'win32':
            pass
        elif sys.platform.startswith('linux'):
            self.s = BluetoothServer(self.data_received)

        return self.scm

    def on_stop(self):
        # 종료시 쓰레드 종료
        self.th_obj.is_running = False

        # 종료시 플라스크 종료
        # self.flask_proc.terminate()
        # self.flask_proc.join()

    def triggerThreads(self, mode="none"):
        if self.th_obj != "":
            self.th_obj.threadDateTime("stop")
            self.th_obj.queueToDevice("stop")

        self.th_obj = ThreadKivy()
        self.th_obj.is_running = True

        self.th_obj.threadDateTime("start")
        self.th_obj.queueToDevice("start")

    def openMenu(self):
        # 메뉴
        current_screen = self.scm.children[0]

        menu_cavity = current_screen.ids.menu
        menu = menu_cavity.children[0]

        menu.pos = (0,0)
        menu.ids.menu_btn.pos = [-1000,-1000]

    def closeMenu(self):
        # 메뉴
        current_screen = self.scm.children[0]

        menu_cavity = current_screen.ids.menu
        menu = menu_cavity.children[0]

        menu.pos = (800,0)
    
    def data_received(self, data):
        if (data != "\n"):
            # print(data.strip())
            self.que.put(data.strip())
            self.s.send(data.strip() + " hahahaha" + "\n")
            # self.s.send(bytes("hahahaha\n", 'utf-8'))


from flask import Flask, request
flask = Flask(__name__)

@flask.route('/')
def frontPage():
    result = 'Hello World!!'
    flask.que.put(result)

    return result

@flask.route('/brightness/<int:num>')
def setBrightness(num=None):
    result = 'Brightness: ' + str(num)
    if num is not None:
        flask.que.put(result)

    return result

def flaskRun(que, que_from_kivy):
    th_obj = ""

    flask.que = que
    flask.que_from_kivy = que_from_kivy
    flask.que.put('Flask begin')

    th_obj = ThreadFlask()
    th_obj.is_running = True

    th_obj.queueToServer("start")

    flask.run(host='0.0.0.0')

from multiprocessing import Process, Manager, Queue
if __name__ == '__main__':
    app_main = AppMain()
    app_main.run()
