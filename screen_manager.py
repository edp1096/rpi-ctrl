import sys, os, subprocess
from eth_control import EthControl
from blt_control import BluetoothControl
from kivy.uix.screenmanager import Screen, ScreenManager, NoTransition
# from kivy.properties import StringProperty, NumericProperty, ObjectProperty, BooleanProperty
from kivy.properties import *

from kivy.uix.label import Label
from kivy.uix.vkeyboard import VKeyboard


class ScreenKeyboard(VKeyboard):
    # Kivy 1.10.0 기준으로 윈도우는 textinput / on_key_down, 리눅스는 on_key_up & on_key_down
    # on_key_up은 안쓴다.

    # 일반 글자 처리
    def on_textinput(self, internal):
        self.current_screen = self.parent.parent

        # print("t in " + str(internal))
        if self.current_screen.name is "Ether" and sys.platform.startswith('win32'):
            if internal != None:
                self.current_screen.ids.ap_pwd.text += internal

    # 백스페이스, 엔터, 시프트, 캡스록, 이스케이프 등 처리
    def on_key_down(self, b_keycode, internal, b_modifiers):
        self.current_screen = self.parent.parent

        # print("k dn " + str(internal) + "/" + str(b_keycode))
        if self.current_screen.name is "Ether":
            if b_keycode == "backspace":
                text = self.current_screen.ids.ap_pwd.text
                self.current_screen.ids.ap_pwd.text = text[:-1]
            elif internal != None:
                self.current_screen.ids.ap_pwd.text += internal


class ScreenHome(Screen):
    pass

class ScreenEther(Screen):
    ethc = EthControl()
    selected_ap = ""
    ap_pwd = ""

    def on_enter(self, *args):
        if sys.platform.startswith('linux'):
            self.eth = "eth0"
            self.wifi = "wlan0"
        else:
            self.eth = "이더넷"
            self.wifi = "Wi-Fi"

        # 정보 취득하여 표시 - 느려서 제외. 사용자 입력에 의해 트리거하게 함.
        # self.reloadApList()
        # self.showIpList()

    def toggleKeyboard(self, mode):
        keyboard = self.ids.screen_keyboard.children[0]
        if mode is "show":
            keyboard.pos = ((self.width - keyboard.width) / 2, 0)
        else:
            keyboard.pos = (self.width, 0)

    def wifiOnOff(self, cmd):
        self.ethc.wifiOnOff(cmd)

    def showIpList(self):
        ip_eth = self.ethc.getIp(self.eth)
        ip_wifi = self.ethc.getIp(self.wifi)

        if ip_wifi is "":
            print("WIFI Null")

        if "Device not found" not in ip_eth:
            self.ids["ether_eth_ip"].text = ip_eth
        if "Device not found" not in ip_wifi:
            self.ids["ether_wifi_ip"].text = ip_wifi

    def reloadApList(self):
        self.ids["ether_ap_list"].data = []
        for ap_name in self.ethc.getAp():
            self.ids["ether_ap_list"].data.append({'ap_name': ap_name})

    def connectWifi(self):
        self.selected_ap = self.ids.selected_ap.text
        self.ap_pwd = self.ids.ap_pwd.text
        self.ethc.connectWifi(self.selected_ap, self.ap_pwd)

    def disconnectWifi(self):
        self.ethc.disconnectWifi()


class ScreenBluetooth(Screen):
    bltc = BluetoothControl()
    selected_ap = ""
    ap_pwd = ""

    def on_enter(self, *args):
        if sys.platform.startswith('linux'):
            pass
        else:
            self.ids.title.text = "블루투스 - MS Windows는 직접 연결"

    def getControllerList(self):
        self.bltc.getControllerList()

    def doDeviceScan(self):
        self.ids["blt_device_list"].data = []
        for bt_info in self.bltc.doDeviceScan():
            bt_info_arr = bt_info.split("~~SEPERATOR~~")
            bt_mac = bt_info_arr[0]
            bt_name = bt_info_arr[1]
            # print(bt_name + "/" + bt_mac)
            self.ids["blt_device_list"].data.append({'bt_name': bt_name, 'bt_mac': bt_mac})
    
    def setDiscoverable(self):
        self.bltc.setDiscoverable()

    def getPairedList(self):
        self.bltc.getPairedList()

    def rfcommStart(self):
        self.bltc.rfcommStart()

    # def rfcommStop(self):
    #     self.bltc.rfcommStop()

    def sendData(self, data):
        self.bltc.sendData(data)

    # def sendSerialData(self, data):
    #     self.bltc.sendSerialData(data)


class ScreenDisp(Screen):
    def on_enter(self, *args):
        if sys.platform.startswith('linux'):
            bl_off_int = subprocess.getoutput("cat /sys/class/backlight/rpi_backlight/bl_power")

            if "No such file" in bl_off_int:
                pass
            else:
                bl_stats = "Off"
                if int(bl_off_int) is 0:
                    bl_stats = "On"
                else:
                    bl_stats = "Off"

                self.ids["disp_off"].text = bl_stats

                bl_brightness_int = int(subprocess.getoutput("cat /sys/class/backlight/rpi_backlight/brightness"))
                self.ids.sl_brightness.value = round(bl_brightness_int / 2)

    def setBrightness(self, val):
        br_val = round(val) * 2
        if sys.platform.startswith('linux'):
            try:
                if br_val < 10:
                    br_val = 10

                cmd = "sudo bash -c \"echo " + str(br_val) + " > /sys/class/backlight/rpi_backlight/brightness\""
                os.system(cmd)
            except AttributeError as e:
                print("e:" + " " + e)
            except Exception as ec:
                print("ec:" + " " + ec, False)
            else:
                pass
        else:
            # print(br_val)
            pass

class ScreenManagement(ScreenManager):
    # Kivy 1.10.1-dev 이상은 아래 설정이 안 먹히므로 AppMain에서 설정해야 된다.
    ScreenManager.transition = NoTransition()
