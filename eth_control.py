import sys, os, subprocess
import random

class EthControl:
    # def init(self):
    #     if sys.platform.startswith('linux'):
    #         eth = "eth0"
    #         wifi = "wlan0"
    #     else:
    #         eth = "이더넷"
    #         wifi = "Wi-Fi"

    #     ap = self.getAp()

    #     eth_ip = self.getIp(eth)
    #     wifi_ip = self.getIp(wifi)

    #     self.connectWifi("kstech", "kstech0007")

    def __init__(self):
        pass

    def wifiOnOff(self, cmd):
        if cmd == "on":
            os.system("sudo ifup wlan0")
        else:
            os.system("sudo ifdown wlan0")

    def getAp(self):
        ap_list = []
        if sys.platform.startswith('linux'):
            ap_list_cmd = '''
            sudo bash -c "iwlist wlan0 scan | awk -F ':' '/ESSID:/ {print $2;}'" | sed 's/ESSID://' | tr -d '"' | tr -d ' '
            '''
            ap_list_raw = subprocess.getoutput(ap_list_cmd)
            for ap in ap_list_raw.split("\n"):
                ap_list.append(ap)
        else:
            ch_cmd = "chcp"
            ch_cmd = str(ch_cmd)
            ch_raw = subprocess.getoutput(ch_cmd)
            chcp_arr = ch_raw.split(": ")
            chcp = chcp_arr[1]

            ap_cmd = "netsh wlan show networks"
            ap_list_cmd = str(ap_cmd)
            os.system("chcp 437 > nul 2>&1")
            # os.system("chcp 437")
            response_raw = subprocess.getoutput(ap_list_cmd)
            os.system("chcp " + chcp + " > nul 2>&1")
            # os.system("chcp " + chcp)
            response_raw_arr = response_raw.split("\n")

            for i in range(0, len(response_raw_arr) - 1):
                if "SSID" in response_raw_arr[i]:
                    ap_arr = response_raw_arr[i].split(":")
                    ap = ap_arr[1].strip()

                    if len(ap) > 0:
                        # ap_list += "\n" + ap
                        ap_list.append(ap)

        return ap_list

    def getIp(self, target):
        if sys.platform.startswith('linux'):
            # ip_cmd = "ifconfig eth0 | grep 'inet\b' | cut -d: -f2 | awk '{print $1}'"
            os_info = subprocess.getoutput("cat /etc/os-release")
            for line in os_info.split("\n"):
                if "VERSION=" in line:
                    if "jessie" in line or "wheezy" in line:
                        ip_cmd = "ifconfig " + target + " | grep 'inet ' | cut -d: -f2 | awk '{print $1}'"
                    else:
                        ip_cmd = "ifconfig " + target + " | grep 'inet ' | cut -d: -f2 | awk '{print $2}'"

            ip = subprocess.getoutput(ip_cmd)
        else:
            ether_raw_arr = (subprocess.getoutput("netsh interface show interface")).split("\n")

            # 빈 내용, 헤더, 구분선 제거
            for _ in range(3): ether_raw_arr.pop(0)
            ether_raw_arr.pop()

            ether_arr = []
            for raw in ether_raw_arr:
                raw_arr = raw.split(" ")
                ether_arr.append(raw_arr[-1])

            ip_cmd = "netsh interface ip show config name=\"" + target + "\""
            ip_cmd = str(ip_cmd)
            response_raw = subprocess.getoutput(ip_cmd)

            if "IP" in response_raw:
                response_raw_arr = response_raw.split("\n")
                ip_raw_arr = (response_raw_arr[3]).split(" ")
                ip = ip_raw_arr[len(ip_raw_arr)-1]
            else:
                ip = ""

        return ip

    def connectWifi(self, ap, pwd):
        if ap is "" or pwd is "":
            print("AP or Password is null")
            return

        if sys.platform.startswith('linux'):
            os.system("sudo rm -rf /etc/wpa_supplicant/wpa_supplicant.conf")

            os_info = subprocess.getoutput("cat /etc/os-release")
            for line in os_info.split("\n"):
                if "VERSION=" in line:
                    if "jessie" not in line and "wheezy" not in line:
                        wpa_default_country = "country=GB"
                        wpa_default_ctrl_interface = "ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev"
                        wpa_default_update_config = "update_config=1"
                        os.system("sudo bash -c \"echo " + wpa_default_country + " > /etc/wpa_supplicant/wpa_supplicant.conf\"")
                        os.system("sudo bash -c \"echo " + wpa_default_ctrl_interface + " >> /etc/wpa_supplicant/wpa_supplicant.conf\"")
                        os.system("sudo bash -c \"echo " + wpa_default_update_config + " >> /etc/wpa_supplicant/wpa_supplicant.conf\"")

            wpa_cmd = "sudo bash -c \"wpa_passphrase '" + ap + "' " + pwd + " >> /etc/wpa_supplicant/wpa_supplicant.conf\""
            os.system(wpa_cmd)

            ifdown_cmd = "sudo ifdown wlan0"
            ifup_cmd = "sudo ifup wlan0"
            os.system(ifdown_cmd)
            os.system(ifup_cmd)
        else:
            profile_fi = open("template/wifi_profile_skel.xml", "r")
            profile_ti = profile_fi.read()
            profile_fi.close()

            profile_to = profile_ti.replace('{SSID}', ap)
            profile_to = profile_to.replace('{password}', pwd)

            fo_name = random.randrange(1, 10)
            profile_fo = open("wifi_profile_" + str(fo_name) + ".xml", "w")
            profile_fo.write(profile_to)
            profile_fo.close()

            profile_del_cmd = "netsh wlan delete profile n=\"" + ap  + "\" > nul 2>&1"
            os.system(str(profile_del_cmd + " > nul 2>&1"))

            profile_add_cmd = "netsh wlan add profile f=\"" + profile_fo.name + "\""
            os.system(str(profile_add_cmd + " > nul 2>&1"))

            os.remove(profile_fo.name)

            connect_cmd = "netsh wlan connect n=\"" + ap + "\""
            os.system(str(connect_cmd + " > nul 2>&1"))

    def disconnectWifi(self):
        if sys.platform.startswith('linux'):
            disconnect_cmd = "sudo ifdown wlan0"
            os.system(str(disconnect_cmd))
        else:
            disconnect_cmd = "netsh wlan disconnect"
            os.system(str(disconnect_cmd + " > nul 2>&1"))

        # os.system(str(disconnect_cmd))
