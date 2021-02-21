import sys, os, subprocess
import random

import pexpect

if sys.platform == 'win32':
    import pexpect.popen_spawn

class BluetoothControl:

    def __init__(self):
        if sys.platform == 'win32':
            self.child = pexpect.popen_spawn.PopenSpawn("python")
        elif sys.platform.startswith('linux'):
            self.child = pexpect.spawn("bluetoothctl")
            self.child.sendline("power on")
            self.child.expect(["bluetooth", pexpect.EOF])
            self.child.sendline("agent on")
            self.child.expect(["bluetooth", pexpect.EOF])
            self.child.sendline("pairable on")
            self.child.expect(["bluetooth", pexpect.EOF])
            self.child.sendline("discoverable on")
            self.child.expect(["bluetooth", pexpect.EOF])

    def setDiscoverable(self):
        self.child = pexpect.spawn("bluetoothctl")
        self.child.sendline("power on")
        self.child.expect(["bluetooth", pexpect.EOF])
        self.child.sendline("agent on")
        self.child.expect(["bluetooth", pexpect.EOF])
        self.child.sendline("pairable on")
        self.child.expect(["bluetooth", pexpect.EOF])
        self.child.sendline("discoverable on")
        self.child.expect(["bluetooth", pexpect.EOF])

    def getControllerList(self):
        controller_list_response = subprocess.getoutput("hcitool dev")
        controller_list = controller_list_response.split("\n")
        if len(controller_list) > 1:
            for controller in controller_list:
                if "Devices:" not in controller:
                    controller_str = controller.split("\t")
                    # print(controller_str[0])
                    print(controller_str[1])
                    print(controller_str[2])
                    # print(controller)
        else:
            print("No Controller")

    def doDeviceScan(self):
        bt_list = []

        device_list_response = subprocess.getoutput("hcitool scan")
        device_list = device_list_response.split("\n")
        if len(device_list) > 1:
            for device in device_list:
                if "Scanning ..." not in device:
                    # print(device)
                    device_str = device.split("\t")
                    # print(device_str[0])
                    # print(device_str[1])
                    # print(device_str[2])
                    if (device_str[2] != "n/a"):
                        bt_list.append(str(device_str[1]) + "~~SEPERATOR~~" + str(device_str[2]))
                    # print(device)
        else:
            # print("No device.")
            bt_list.append("No device.")
        # print(device_list)

        return bt_list

    def getPairedList(self):
        print("GET Paired List")

    def rfcommStart(self):
        # self.proc = subprocess.Popen(['sudo bash', '-c', "'rfcomm watch hci0'"], shell=True)
        self.proc = subprocess.Popen(['sudo', 'bash', "-c", "rfcomm watch all"], shell=False)
        # self.proc = subprocess.getoutput("sudo bash -c 'rfcomm watch all&'")
        # self.proc = subprocess.Popen(["sudo", "rfcomm watch all"], shell=False)
        # self.proc = subprocess.Popen(["sudo", "rfcomm", "watch hci0"],
        #                             shell=False,
        #                             stdin=subprocess.PIPE,
        #                             stdout=subprocess.PIPE,
        #                             stderr=subprocess.PIPE)
        # self.pid = self.proc.pid
        # print(self.proc)
        print(self.proc.pid)

    def getData(self):
        data = subprocess.getoutput("sudo cat /dev/rfcomm0")
        print(data)

    # pid = ""
    # def rfcommStop(self):
    #     if (self.pid != ""):
    #         print(str(self.pid))
    #         os.system("sudo kill " + str(self.pid))
    #         # self.proc.terminate()

    def sendData(self, data):
        # print(data)
        os.system("sudo bash -c 'echo \"" + data + "\" > /dev/rfcomm0'")

    # import serial
    # from time import sleep
    # def sendSerialData(self, data):
    #     print(data)
    #     os.system("sudo bash -c \"echo '" + data + "' > /dev/rfcomm0\"")

