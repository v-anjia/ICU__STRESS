'''
deposit public class or function
data:2019-3-28
@author antony weijiang
'''
#coding=utf-8
import subprocess
import re
import os
import time
import sys
import uiautomator2 as u2
import requests
from bs4 import BeautifulSoup
from log import logger as loger
import json
import zipfile
import serial
import random


# from Common import LogCatFile as lcf
# from Common import ScreenCap as scp
from Common import Signal_Common as SC
from Common import Signal_List as SL

logger = loger.Current_Module()
busybox = "/oem/bin/busybox"
json_name = "/update/data.json"
log_path = "/update/log/FOTA_HU_*.log"

data_size = "200"
package_path = "/update/package/hu/mpu"
# libHufota = "/update/libHUfota/libHUfota.log"
libHufota = "/update/log/libHUfota.log"
lvlog = "/sdcard/lvlog/com.living.ota/normal/*.log"
lvlog_path = "/sdcard/lvlog/com.living.ota/normal/"
settinglog = "/sdcard/lvlog/com.android.settings/normal/*.log"
network_device = "tbox0"
tbox_version = "/update/version.txt"
logcat_object = None

'''
define class for hu devices
'''
class ADB_SN(object):
    '''
    get sn number
    '''
    def __init__(self):
        self.sn = "unknown"

    def set_sn(self,sn):
        self.sn = sn

    def get_sn(self):
        return self.sn

    def get_sn_from_adb_command(self):
        '''
        function:get sn serial number
        :return:
        '''
        cmd = 'adb devices'
        rtn = subprocess.check_output(cmd,shell=True)
        p = re.compile("\n([\w]*)\t")
        return re.findall(p, rtn.decode())

    # def check_adb_status(self):
    #     '''
    #     function:check adb device status
    #     :return:
    #     '''
    #     output = subprocess.Popen('adb devices', stdout=subprocess.PIPE, shell=True).\
    #                             stdout.read()
    #     if b'not running' in output or b'error' in output \
    #             or output == b'List of devices attached\r\n\r\n':
    #         logger.log_error('adb connect error,exit',\
    #                          sys._getframe().f_code.co_filename,sys._getframe().f_code.co_name,sys._getframe().f_lineno)
    #         sys.exit(-1)
    #     else:
    #         return True

    def check_adb_status(self):
        '''
        function:check adb device status
        :return:
        '''
        output = subprocess.Popen('adb devices', stdout=subprocess.PIPE, shell=True).\
                                stdout.read()
        if b'not running' in output or b'error' in output \
                or output == b'List of devices attached\r\n\r\n':
            logger.log_error('adb connect error,exit',\
                             sys._getframe().f_code.co_filename,sys._getframe().f_code.co_name,sys._getframe().f_lineno)
            return False
        else:
            return True

    @property
    def isConnecting(self):
        if str.encode(self.sn) in subprocess.check_output\
                            ('adb -s %s devices' % self.sn, shell=True):
            return True
        return False

    # def wait_adb(self,sn):
    #     os.system('adb -s %s wait-for-device' % sn)
    #     while True:
    #         time.sleep(10)
    #         retryRet = subprocess.Popen('adb -s %s shell "getprop | grep boot_completed"' % sn, stdout=subprocess.PIPE,
    #                                     shell=True).stdout.read()
    #         if str.encode('sys.boot_completed') not in retryRet and str.encode(self.sn) not in subprocess.check_output\
    #                     ('adb -s %s devices' % self.sn, shell=True):
    #             log_warn('%s waitting for device boot up' % sn)
    #             log_warn('%s waitting for adb connected')
    #         else:
    #             logger.info('=====>%s: boot into system success' % sn)
    #             logger.info('=====>%s: adb has connected' % sn)
    #             return True

    def wait_adb(self,delay_time):
        '''
        function wait adb devices
        :param delay_time:
        :return:
        '''
        os.system('adb -s %s wait-for-device' % self.sn)
        for i in range(delay_time):

            if str.encode(self.sn) in subprocess.check_output\
                        ('adb -s %s devices' % self.sn, shell=True):
                logger.log_info('adb has connected',\
                                sys._getframe().f_code.co_filename,sys._getframe().f_code.co_name,sys._getframe().f_lineno)
                return True
            elif i == delay_time:
                logger.log_error('device: %s boot to adb FAIL' % self.sn,\
                                sys._getframe().f_code.co_filename,sys._getframe().f_code.co_name,sys._getframe().f_lineno)
                return False
            else:
                logger.log_info('wait adb 10s: %d' % i, \
                                sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name,
                                sys._getframe().f_lineno)
                time.sleep(10)

    def wait_ui(self):
        '''
        function wait hu device wake up
        :return:
        '''
        for i in range(2):
            logger.log_info('wait UI 60s: %d' % i,\
                            sys._getframe().f_code.co_filename,sys._getframe().f_code.co_name,sys._getframe().f_lineno)
            if 'sys.boot_completed' in str(subprocess.check_output\
                        ('adb -s %s shell "getprop|grep boot_completed"' % self.sn,shell=True)):
                return True
            elif i == 4:
                logger.log_error('device: %s boot to ui FAIL' % self.sn,\
                                 sys._getframe().f_code.co_filename,sys._getframe().f_code.co_name,sys._getframe().f_lineno)
                return False
            else:
                time.sleep(10)

class Serial(object):
    def __init__(self):
        self.serial_port = None
        self.serial_baudrate = 115200
        self.serial_bytesize = None
        self.serial_parity = 'N'
        self.serial_stopbits = 1
        self.package = Install_Package()

    def set_serialport(self):
        self.serial_port = self.package.update_fota_package()[4]

    def get_serialport(self):
        return self.serial_port

    def set_serial_baudrate(self, serial_baudrate):
        self.serial_baudrate = serial_baudrate

    def get_serial_baudrate(self):
        return self.serial_baudrate

    def set_serial_bytesize(self,serial_bytesize):
        self.serial_bytesize = serial_bytesize

    def get_serial_bytesize(self):
        return self.serial_bytesize

    def set_serial_parity(self,serial_stopbits):
        self.serial_stopbits = serial_stopbits

    def get_serial_parity(self):
        return self.serial_stopbits

    def open_adb_through_serial(self,count):
        '''
        function:open adb port
        :return:
        '''
        self.set_serialport()
        ser = serial.Serial(self.get_serialport(),self.get_serial_baudrate())
        ser.write("su\r\n".encode('utf-8'))
        time.sleep(5)
        ser.write(("ps -ef|grep activate|grep -v grep| %s  awk '{print $2}'|xargs kill -9 \r\n" %(busybox)).encode('utf-8'))
        time.sleep(5)
        ser.write("content insert --uri content://settings/system --bind name:s:user_rotation --bind value:i:3\r\n".encode('utf-8'))
        time.sleep(5)
        ser.write("input keyevent 3\r\n".encode('utf-8'))
        time.sleep(5)
        # ser.write("am start -n com.android.settings/com.android.settings.livingui.LVSettingsActivity\r\n".encode('utf-8'))
        ser.write("am start -n com.android.settings/com.android.settings.livingui.LVSettingHomePageActivity\r\n".encode('utf-8'))
        time.sleep(5)
        ser.write("input swipe 300 1452 500 1452 1000\r\n".encode('utf-8'))
        time.sleep(5)
        ser.write("input swipe 379 1700 379 0 500\r\n".encode('utf-8'))
        time.sleep(5)
        for i in range(count):
            ser.write("input tap 969 878\r\n".encode('utf-8'))
            time.sleep(5)
        ser.close()

    def wait_ui_through_serial(self):
        self.set_serialport()
        ser = serial.Serial(self.get_serialport(), self.get_serial_baudrate())
        ser.write("su\r\n".encode('utf-8'))
        time.sleep(5)
        while True:
            for i in range(200):
                ser.write("getprop|grep boot_completed\r\n".encode('utf-8'))
                if 'sys.boot_completed' in ser.read_all().decode('utf-8'):
                    return  True
                else:
                    time.sleep(9)
            return False

    def enter_fastboot_mode(self):
        self.set_serialport()
        ser = serial.Serial(self.get_serialport(), self.get_serial_baudrate())
        ser.write("su\r\n".encode('utf-8'))
        ser.write("reboot fastboot\r\n".encode('utf-8'))
        ser.write("reboot fastboot\r\n".encode('utf-8'))
        time.sleep(10)

    def enter_softupgrade_page(self):
        self.set_serialport()
        ser = serial.Serial(self.get_serialport(), self.get_serial_baudrate())
        ser.write("su\r\n".encode('utf-8'))
        time.sleep(5)
        ser.write(("ps -ef|grep activate|grep -v grep| %s  awk '{print $2}'|xargs kill -9 \r\n" %(busybox)).encode('utf-8'))
        time.sleep(5)
        ser.write("content insert --uri content://settings/system --bind name:s:user_rotation --bind value:i:3\r\n".encode('utf-8'))
        time.sleep(5)
        ser.write("input keyevent 3\r\n".encode('utf-8'))
        time.sleep(5)
        ser.write("am start -n com.android.settings/com.android.settings.livingui.LVSettingHomePageActivity\r\n".encode('utf-8'))
        # ser.write("am start -n com.android.settings/com.android.settings.livingui.LVSettingsActivity\r\n".encode('utf-8'))
        time.sleep(5)
        ser.write("am start -n com.living.ota/com.living.ota.MainActivity\r\n".encode('utf-8'))
        time.sleep(5)

    def cancle_activeupgrade_through_settings(self):
        self.set_serialport()
        ser = serial.Serial(self.get_serialport(), self.get_serial_baudrate())
        ser.write("su\r\n".encode('utf-8'))
        time.sleep(5)
        #setting-->soft upgrade
        ser.write("input swipe 400 1570 600 1570 1000\r\n".encode('utf-8'))
        time.sleep(20)
        #放弃升级
        ser.write("input swipe 260 1300 360 1300 1000\r\n".encode('utf-8'))
        time.sleep(5)
        #返回
        ser.write("input swipe 50 190 80 190 1000\r\n".encode('utf-8'))
        time.sleep(5)
        # #跳过
        # ser.write("input swipe 700 1400 800 1400 1000\r\n".encode('utf-8'))
        # time.sleep(5)
        # #退出安装
        # ser.write("input swipe 650 1100 750 1100 1000\r\n".encode('utf-8'))
        # time.sleep(5)

    def activeupgrade_through_settings(self):
        self.set_serialport()
        ser = serial.Serial(self.get_serialport(), self.get_serial_baudrate())
        ser.write("su\r\n".encode('utf-8'))
        time.sleep(5)
        #设置-->软件升级 立即安装
        ser.write("input swipe 400 1570 600 1570 1000\r\n".encode('utf-8'))
        time.sleep(20)
        # 立即安装1
        ser.write("input swipe 260 1200 360 1200 1000\r\n".encode('utf-8'))
        time.sleep(5)
        #放弃升级
        # ser.write("input swipe 260 1400 360 1400 1000\r\n".encode('utf-8'))
        # time.sleep(5)
        # #跳过
        # ser.write("input swipe 700 1400 800 1400 1000\r\n".encode('utf-8'))
        # time.sleep(5)
        #确认安装
        # ser.write("input swipe 250 1100 250 1100 1000\r\n".encode('utf-8'))
        # time.sleep(5)
        #退出安装
        # ser.write("input swipe 650 1100 750 1100 1000\r\n".encode('utf-8'))
        # time.sleep(5)

    def active_upgrade(self):
        self.set_serialport()
        ser = serial.Serial(self.get_serialport(), self.get_serial_baudrate())
        ser.write("su\r\n".encode('utf-8'))
        time.sleep(5)
        #立即安装
        ser.write("input swipe 400 1750 600 1750 1000\r\n".encode('utf-8'))
        # ser.write("input swipe 400 1690 600 1690 1000\r\n".encode('utf-8'))
        time.sleep(20)
        # 立即安装1
        ser.write("input swipe 260 1300 360 1300 1000\r\n".encode('utf-8'))
        time.sleep(5)
        #取消
        #ser.write("input swipe 900 120 950 120 1000\r\n".encode('uft-8'))
        #设置-->软件升级 立即安装
        # ser.write("input swipe 400 1570 600 1570 1000\r\n".encode('utf-8'))
        # time.sleep(20)
        #放弃升级
        # ser.write("input swipe 260 1300 360 1300 1000\r\n".encode('utf-8'))
        # time.sleep(5)

        #跳过
        # ser.write("input swipe 700 1400 800 1400 1000\r\n".encode('utf-8'))
        # time.sleep(5)
        #确认安装
        # ser.write("input swipe 250 1100 250 1100 1000\r\n".encode('utf-8'))
        # time.sleep(5)
        #退出安装
        # ser.write("input swipe 650 1100 750 1100 1000\r\n".encode('utf-8'))
        # time.sleep(5)

    def cancel_activeupgrade(self):
        self.set_serialport()
        ser = serial.Serial(self.get_serialport(), self.get_serial_baudrate())
        ser.write("su\r\n".encode('utf-8'))
        time.sleep(5)
        #取消
        ser.write("input swipe 900 120 950 120 1000\r\n".encode('utf-8'))
        time.sleep(5)



'''
this class for install package
'''
class Install_Package(object):
    def __init__(self):
        pass

    def curDate(self):
        '''
        function:get current date
        :return:
        '''
        curDate = time.strftime('%Y%m%d', time.localtime())
        return curDate

    def oldDate(self):
        '''
        function:get old date from date_for_fota
        :return:
        '''
        logger.log_info("%s" %(self.update_fota_package()[1]),\
                        sys._getframe().f_code.co_filename,sys._getframe().f_code.co_name,sys._getframe().f_lineno)
        return self.update_fota_package()[1]

    def down_fastboot_package_to_local(self,url_link,date):
        '''
        function:download 'mcuupgrade.bin' and 'update.zip' to local
        :param url_link:
        :param date:
        :return:
        '''
        if not os.path.exists("Common/update"):
            os.makedirs("Common/update")
        urls =r'%s%s' %(url_link[0],date)
        logger.log_info("%s" %(urls),\
                        sys._getframe().f_code.co_filename,sys._getframe().f_code.co_name,sys._getframe().f_lineno)
        site = requests.get(urls)
        text = site.text
        site.close()
        soup = BeautifulSoup((text), "html5lib")
        alist = soup.find_all('a')

        try:
            ver = alist[6]
        except:
            logger.log_critical('has no update for daily test',\
                                 sys._getframe().f_code.co_filename,sys._getframe().f_code.co_name,sys._getframe().f_lineno)
            sys.exit(-1)
        HDver=ver.text
        print ("%s" %(HDver))
        urlfastboot = '%s/%s' % (urls, HDver)
        print ("%s" %(urlfastboot))
        logger.log_info('starting download fastboot(fastboot.zip) to local , pls wait ...',\
                        sys._getframe().f_code.co_filename,sys._getframe().f_code.co_name,sys._getframe().f_lineno)
        site2 = requests.get(urlfastboot, stream=True)
        with open("Common/update/fastboot.zip",'wb') as ofp:
            for chunk in site2.iter_content(chunk_size=1024):
                ofp.write(chunk)
        logger.log_info('fastboot.zip download finished !',\
                        sys._getframe().f_code.co_filename,sys._getframe().f_code.co_name,sys._getframe().f_lineno)

    def unzip_fastboot_package(self):
        '''
        function:unzip fastboot.zip
        :return:
        '''
        fast_boot = "Common/update/fastboot.zip"
        try:
            if os.path.exists("%s" %(fast_boot)):
                zf = zipfile.ZipFile("%s" %(fast_boot), 'r')
                logger.log_info("start unzip fastboot.zip package",\
                                sys._getframe().f_code.co_filename,sys._getframe().f_code.co_name,sys._getframe().f_lineno)
                zf.extractall("Common/update/")
            else:
                logger.log_error("has no fastboot.zip package",\
                                 sys._getframe().f_code.co_filename,sys._getframe().f_code.co_name,sys._getframe().f_lineno)
                sys.exit(-1)
        except Exception as e:
            logger.log_error("%s" %(e),\
                             sys._getframe().f_code.co_filename,sys._getframe().f_code.co_name,sys._getframe().f_lineno)
            sys.exit(-1)

    '''
    function for ase-1 test
    '''
    def down_package_to_local(self,url_link,date):
        '''
        function:download 'mcuupgrade.bin' and 'update.zip' to local
        :param url_link:
        :param date:
        :return:
        '''
        if not os.path.exists("Common/update"):
            os.makedirs("Common/update")
        urls =r'%s%s' %(url_link[0],date)
        logger.log_info("%s" %(urls),\
                        sys._getframe().f_code.co_filename,sys._getframe().f_code.co_name,sys._getframe().f_lineno)
        site = requests.get(urls)
        text = site.text
        site.close()
        soup = BeautifulSoup((text), "html5lib")
        alist = soup.find_all('a')
        try:
            ver = alist[5]
        except:
            logger.logg_critical('has no update for daily test',\
                                 sys._getframe().f_code.co_filename,sys._getframe().f_code.co_name,sys._getframe().f_lineno)
            sys.exit(-1)
        HDver=ver.text
        urlMCU = '%s/%s%s'%(urls,HDver,'mcuupgrade.bin')
        urlos = '%s/%s%s'%(urls,HDver,'update.zip')
        logger.log_info('starting download MCU(mcuupgrade.bin) to local , pls wait ...',\
                        sys._getframe().f_code.co_filename,sys._getframe().f_code.co_name,sys._getframe().f_lineno)
        logger.log_info("link is :%s" %(urlMCU),\
                 sys._getframe().f_code.co_filename,sys._getframe().f_code.co_name,sys._getframe().f_lineno)
        site2 = requests.get(urlMCU,stream = True)
        with open("Common/update/mcuupgrade.bin",'wb') as ofp:
            for chunk in site2.iter_content(chunk_size=512):
                ofp.write(chunk)
        logger.log_info('MCU download finished !',\
                        sys._getframe().f_code.co_filename,sys._getframe().f_code.co_name,sys._getframe().f_lineno)
        logger.log_info('starting download OS(update.zip) to local, pls wait ...',\
                            sys._getframe().f_code.co_filename,sys._getframe().f_code.co_name,sys._getframe().f_lineno)
        logger.log_info("link is :%s" %(urlos),\
                        sys._getframe().f_code.co_filename,sys._getframe().f_code.co_name,sys._getframe().f_lineno)
        site3 = requests.get(urlos,stream = True)
        with open("Common/update/update.zip",'wb') as ofp:
            for chunk in site3.iter_content(chunk_size=512):
                ofp.write(chunk)
        logger.log_info('OS download finished !',\
                            sys._getframe().f_code.co_filename,sys._getframe().f_code.co_name,sys._getframe().f_lineno)
    '''
    function for ase-1 test
    '''
    def copy_local_to_udisk(self,sn):
        '''
        function :copy update.zip and bin file to udisk
        :param sn:
        :return:
        '''
        #subprocess.call('adb -s %s reboot' % sn, shell=True)
        os.system('adb -s %s wait-for-device' % sn)
        os.system('adb -s %s shell am force-stop com.wm.activate' % sn)
        subprocess.call('adb -s %s root' % sn, shell=True)
        while True:
            time.sleep(5)
            if sn not in ADB_SN().get_sn_from_adb_command():
                logger.log_warn('%s: wait adb connect' % sn,\
                                sys._getframe().f_code.co_filename,sys._getframe().f_code.co_name,sys._getframe().f_lineno)
            else:
                break
        # init_u2 = Prepare_Ui()
        # init_u2.check_ui(sn)
        logger.log_info('%s: copy new image into DUT(udisk)' % sn,\
                        sys._getframe().f_code.co_filename,sys._getframe().f_code.co_name,sys._getframe().f_lineno)
        udisk = subprocess.Popen('adb -s %s shell "df | grep media_rw"' % sn, stdout=subprocess.PIPE,
                                 shell=True).stdout.read()
        if str.encode('media_rw') not in udisk:
            logger.log_error('%s: no udisk found, pls insert udisk' % sn,\
                             sys._getframe().f_code.co_filename,sys._getframe().f_code.co_name,sys._getframe().f_lineno)
            sys.exit(-1)
        try:
            os.system('adb -s %s root' % sn)
            cmd = "$(df |grep media_rw|/yf/bin/busybox awk '{print $1}')"
            os.system('adb -s %s shell "mount -o remount,rw %s"' %(sn,cmd))
            time.sleep(5)
            os.system('adb -s %s push Common/update/mcuupgrade.bin /mnt/udisk/update/devices/mcuupgrade.bin' % sn)
            time.sleep(5)
            os.system('adb -s %s push Common/update/update.zip /mnt/udisk/update/os/update.zip' % sn)
            logger.log_info("copy mcuupgrade.bin and update.zip to udisk successfully",\
                            sys._getframe().f_code.co_filename,sys._getframe().f_code.co_name,sys._getframe().f_lineno)
        except Exception as e:
            logger.log_error("Error message is :%s" %(e),\
                             sys._getframe().f_code.co_filename,sys._getframe().f_code.co_name,sys._getframe().f_lineno)

    def update_system_through_fastboot(self, flag):
        '''
        function: update system
        :return:
        '''
        # print("antony@@@debug")
        serial = Serial()
        serial.enter_fastboot_mode()
        # path = os.path.dirname(os.path.dirname(__file__))+"\\Main\\Common\\update\\fastboot"
        current_path = os.getcwd()
        path = current_path + "\\Common\\update\\fastboot"
        logger.log_info("start install system through fastboot mode,pls wait...",\
                        sys._getframe().f_code.co_filename,sys._getframe().f_code.co_name,sys._getframe().f_lineno)
        os.chdir("%s" %(path))
        os.system("%s\\fastboot.bat < nul" % (path))
        time.sleep(5)
        os.chdir("%s" % (current_path))
        logger.log_info("fastboot install over,wait system launch...",\
                        sys._getframe().f_code.co_filename,sys._getframe().f_code.co_name,sys._getframe().f_lineno)

        if serial.wait_ui_through_serial() == True:
            adb_sn = ADB_SN()
            count = 0
            while True:
                if adb_sn.check_adb_status() == False:
                    serial.open_adb_through_serial(flag)
                    # self.open_adb_through_serial(self.update_fota_package()[4],flag)
                    count = count + 1
                    if adb_sn.check_adb_status() == True:
                        break
                    elif adb_sn.check_adb_status() == False and count == flag:
                        while True:
                            serial.open_adb_through_serial(flag -1)
                            if adb_sn.check_adb_status() == False:
                                count = count - 1
                            else:
                                break
                            if count == 0 and adb_sn.check_adb_status() == False:
                                logger.log_error("can not open adb port",\
                                                 sys._getframe().f_code.co_filename,sys._getframe().f_code.co_name,sys._getframe().f_lineno)
                                return 1
                        break
                else:
                    return 0
            return 0
        else:
            logger.log_error("boot can not completed",\
                             sys._getframe().f_code.co_filename,sys._getframe().f_code.co_name,sys._getframe().f_lineno)
            return 1

    def flash_through_system(self,sn):
        '''
        function:
        :param sn:
        :return:
        '''
        logger.log_info('%s: MCU and OS start upgrade !!!' % sn,\
                        sys._getframe().f_code.co_filename,sys._getframe().f_code.co_name,sys._getframe().f_lineno)
        os.system('adb -s %s shell am force-stop com.wm.activate' % sn)
        subprocess.call('adb -s %s root' % sn, shell=True)
        init_u2 = Prepare_Ui()
        init_u2.check_ui(sn)
        d = u2.connect(sn)
        delete_file(sn)
        d.press("home")
        d.app_start("com.android.settings",
                    "com.android.settings.WMSystemUpdateActivity")
        time.sleep(5)
        if d(resourceId="android:id/button1"):
            print (d(resourceId="android:id/button1").get_text())
            d(resourceId="android:id/button1").click()
        d(resourceId="com.android.settings:id/btn_start_update").click()
        while True:
            time.sleep(20)
            if sn not in ADB_SN().get_sn_from_adb_command():
                break
            logger.log_info('%s: OS are flashing, pls wait ...' % sn,\
                            sys._getframe().f_code.co_filename,sys._getframe().f_code.co_name,sys._getframe().f_lineno)
       # init_u2 = Prepare_Ui()
        init_u2.wait_ui(sn)
        time.sleep(20)
        logger.log_info('%s: clean up system ...' % sn,\
                        sys._getframe().f_code.co_filename,sys._getframe().f_code.co_name,sys._getframe().f_lineno)
        os.system('adb -s %s shell am force-stop com.wm.activate' % sn)
        init_u2.check_ui(sn)
        d = u2.connect(sn)
        if d(resourceId="android:id/button1"):
            print (d(resourceId="android:id/button1").get_text())
            d(resourceId="android:id/button1").click()
        os.system('adb -s %s shell am start -a android.settings.DATE_SETTINGS' % sn)
        status = d(resourceId="android:id/switchWidget")
        if u"关闭" in status.get_text():
            status.click()
        status.click_gone(maxretry=9, interval=1.0)
        d.press("home")
        os.system('adb -s %s root' % sn)
        cmd = "$(df |grep media_rw|%s awk '{print $1}')" %(busybox)
        os.system('adb -s %s shell "mount -o remount,rw %s"' % (sn, cmd))
        os.system('adb -s %s shell rm -rf /mnt/udisk/logFile/*' % sn)
        os.system('adb -s %s shell rm -rf /mnt/udisk/BaiduMapLog/*' % sn)
        logger.log_info('%s: MCU and OS upgrade completed !' % sn,\
                        sys._getframe().f_code.co_filename,sys._getframe().f_code.co_name,sys._getframe().f_lineno)

    def flash_through_recovery(self,sn):
        '''
        function:flash system through recovery normally
        :param sn:
        :return:
        '''
        logger.log_info("flash system through recovery mode",\
                        sys._getframe().f_code.co_filename,sys._getframe().f_code.co_name,sys._getframe().f_lineno)
        self.usb_root_and_install(sn)

    def update_fota_package(self):
        '''
        function:get data_for_fota file content
        :return:
        '''
        filelist = []
        file_name = os.path.join(os.path.dirname(__file__),'Configuration')
        # print("antony @@@debug %s" %(file_name))
        # logger.log_info("file path is : %s" %(file_name),\
        #                 sys._getframe().f_code.co_filename,sys._getframe().f_code.co_name,sys._getframe().f_lineno)
        if os.path.exists(file_name):
            with open(file_name,'r+') as f:
                for msg in f:
                    filelist.append(msg.strip())
        return filelist

    def get_software_version(self,sn):
        '''
        function:get software version
        :param sn:
        :return:version
        '''
        cut_cmd = 'cut -d"[" -f2 | cut -d"]" -f1'
        try:
            version = subprocess.Popen('adb -s %s shell "getprop | grep -E ASE* | %s awk \'{print $NF}\'| %s| uniq"' %(sn,busybox,cut_cmd),\
                stdout=subprocess.PIPE, shell=True).stdout.read()
            version = str(version, encoding="utf-8").replace('\r\r\n','')
            return version.strip()
        except Exception as e:
            logger.log_error("%s" %e,\
                             sys._getframe().f_code.co_filename,sys._getframe().f_code.co_name,sys._getframe().f_lineno)

    def get_tbox_verison(self,sn):
        '''
        function:get tbox version
        :param sn:
        :return:
        '''
        str_msg = 'adb -s %s shell "cat %s |head -n1"' %(sn, tbox_version)
        try:
            return removal(subprocess.check_output(str_msg)).strip()
        except Exception as e:
            logger.log_error("%s" %e,\
                             sys._getframe().f_code.co_filename,sys._getframe().f_code.co_name,sys._getframe().f_lineno)


    def usb_root_and_install(self,sn):
        '''
        function:check udisk status and reboot recovery to install old version
        :param sn:
        :return: re_code
        '''
        udisk = subprocess.Popen('adb -s %s shell "df | grep media_rw"' % sn, stdout=subprocess.PIPE, \
                                 shell=True).stdout.read()
        if str.encode('media_rw') not in udisk:
            logger.log_error('%s: no udisk found, pls insert udisk' % sn,\
                             sys._getframe().f_code.co_filename,sys._getframe().f_code.co_name,sys._getframe().f_lineno)
            sys.exit(-1)
        else:
            try:
                subprocess.check_output('adb -s %s shell reboot recovery' % sn)
            except subprocess.CalledProcessError as e:
                logger.log_error("%s: execute reboot recovery command fail" % sn,\
                                 sys._getframe().f_code.co_filename,sys._getframe().f_code.co_name,sys._getframe().f_lineno)
                return e.returncode

    def check_download_progress(self, sn,flag):
        cmd = 'adb -s %s shell "cat %s |grep DownLoadProcess |tail -n1 |%s sed \'s/.*DownLoadProcess.\{2\}\([0-9]\{1,3\}\).*/\\1/\'"' %(sn,log_path,busybox)
        while True:
            try:
                if int(removal(subprocess.check_output(cmd)).strip()) >= 0 and int(removal(subprocess.check_output(cmd)).strip()) < 100:
                    logger.log_debug("current download progress is :%s " %(removal(subprocess.check_output(cmd)).strip()),\
                                     sys._getframe().f_code.co_filename,sys._getframe().f_code.co_name,sys._getframe().f_lineno)
                    time.sleep(5)
                elif int(removal(subprocess.check_output(cmd)).strip()) >= 0 and int(removal(subprocess.check_output(cmd)).strip()) == 100:
                    logger.log_debug("download %s package success" %(get_packagename_from_json_file(sn,flag)),\
                                     sys._getframe().f_code.co_filename,sys._getframe().f_code.co_name,sys._getframe().f_lineno)
                    return 0
                else :
                    logger.log_error("can not find download process through serach log file",\
                                        sys._getframe().f_code.co_filename,sys._getframe().f_code.co_name,sys._getframe().f_lineno)
                    return 1
            except Exception as e:
                logger.log_error("%s" %e,\
                                 sys._getframe().f_code.co_filename,sys._getframe().f_code.co_name,sys._getframe().f_lineno)
                return 1

'''
this class for platform information
'''
class Platform_Information(object):
    def __init__(self):
        self.vin_version = 'None'
        self.sw_version = 'None'
        self.sw_version_old = 'None'
        self.sw_version_new = 'None'
        self.device = 'None'
        self.mcu_version = 'None'

    def set_vin_version(self, vin_version):
        self.vin_version = vin_version

    def get_vin_version(self):
        return self.vin_version

    def set_sw_version(self, sw_version):
        self.sw_version = sw_version

    def get_sw_version(self):
        return self.sw_version

    def set_sw_version_old(self, sw_version_old):
        self.sw_version_old = sw_version_old

    def get_sw_version_old(self):
        return self.sw_version_old

    def set_sw_version_new(self, sw_version_new):
        self.sw_version_new = sw_version_new

    def get_sw_version_new(self):
        return self.sw_version_new

    def set_device(self,device):
        self.device = device

    def get_device(self):
        return self.device

    def set_mcu_version(self,mcu_version):
        self.mcu_version = mcu_version

    def get_mcu_version(self):
        return self.mcu_version

    def get_vin_verbose(self,sn):
        '''
        function:get vin number
        :param sn:
        :return: str
        '''
        cmd = 'getprop |grep -r ".*vehicle\.vin"|%s awk -F \':\' \'{print $NF}\'| %s sed \'s/\[\([0-9A-Z]*\)\]/\\1/\'' %(busybox,busybox)
        try:
            version = subprocess.Popen(
                'adb -s %s shell "%s"' % (sn, cmd), \
                stdout=subprocess.PIPE, shell=True).stdout.read()

            version = str(version, encoding="utf-8").replace('\r\r\n', '')
            return version.strip()
        except Exception as e:
            logger.log_error("can not find vin number,more details is %s" %(e),\
                             sys._getframe().f_code.co_filename,sys._getframe().f_code.co_name,sys._getframe().f_lineno)


    def get_software_version(self, sn):
        '''
        function:get software version
        :param sn:
        :return:version
        '''
        cut_cmd = 'cut -d"[" -f2 | cut -d"]" -f1'
        version = subprocess.Popen(
            'adb -s %s shell "getprop | grep -E ASE* | %s awk \'{print $NF}\'| %s"' % (sn, busybox, cut_cmd), \
            stdout=subprocess.PIPE, shell=True).stdout.read()
        version = str(version, encoding="utf-8").replace('\r\r\n', '')
        return version.strip()

    def temporary_get_port_data(self, vin_version, device, sw_version_old, mcu_version):
        time_value = int(time.time())
        data_json = \
            {
                "token": None,
                "timestamp": time_value,
                "vin": "%s" % (vin_version),
                "device_list":
                    [{
                        "device_type": "%s" % (device),
                        "device_id": "SN00001",
                        "part_number": "PN00001",
                        "software_list":
                            [{
                                "software_type": "mpu",
                                "sw_version": "%s" % (sw_version_old),
                                "backup_sw_version": "%s" % (sw_version_old)
                            }]
                    },
                        {
                            "device_type": "%s" %(device),
                            "device_id": "SN00001",
                            "part_number": "PN00001",
                            "software_list": [{
                                "software_type": "mcu",
                                "sw_version": "%s" %(mcu_version)
                            }]
                        }
                    ]
            }
        return data_json

    def get_post_data(self, vin_version, device, sw_version_old, sw_version_new,mcu_version):
        '''
        function:get data_json
        :param vin_version:
        :param device:
        :param sw_version_old:
        :param sw_version_new:
        :return:
        '''
        time_value = int(time.time())
        data_json = \
            {
                "token": None,
                "timestamp": time_value,
                "vin": "%s" % (vin_version),
                "device_list":
                    [{
                        "device_type": "%s" % (device),
                        "device_id": "SN00001",
                        "part_number": "PN00001",
                        "software_list":
                            [{
                                "software_type": "mpu",
                                "sw_version": "%s" % (sw_version_old),
                                "backup_sw_version": "%s" % (sw_version_old)
                            }]
                    },
                        {
                            "device_type": "%s" % (device),
                            "device_id": "SN00001",
                            "part_number": "PN00001",
                            "software_list": [{
                                "software_type": "mcu",
                                "sw_version": "%s" % (mcu_version)
                            }]
                        }
                    ]
            }
        return data_json

    def get_header(self, vin_version):
        '''
        function:get header
        :param vin_version:
        :return:
        '''
        header = {"Content-Type": "application/json", "vin": "%s" % (vin_version)}
        return header

'''
prepare device environment 
'''
class Prepare_Ui(object):
    def __init__(self):
        pass

    def wait_ui(self,sn):
        '''
        functin:wait hu devices
        :param sn:
        :return:
        '''
        os.system('adb -s %s wait-for-device' % sn)
        while True:
            retryRet = subprocess.Popen('adb -s %s shell "getprop | grep boot_completed"' % sn, stdout=subprocess.PIPE,
                                        shell=True).stdout.read()
            if str.encode('sys.boot_completed') not in retryRet:
                logger.log_warn('%s: waitting for device boot up' % sn,\
                                sys._getframe().f_code.co_filename,sys._getframe().f_code.co_name,sys._getframe().f_lineno)
            else:
                break
            time.sleep(5)
        logger.log_info('%s: boot into system success' % sn,\
                        sys._getframe().f_code.co_filename,sys._getframe().f_code.co_name,sys._getframe().f_lineno)
        osVersion = subprocess.Popen('adb -s %s shell "getprop | grep ro.headunit.version"' % (sn),
                                     stdout=subprocess.PIPE, shell=True).stdout.read().decode('utf-8')
        p = re.compile(r": \[(ASE.*)\]")
        logger.log_info("%s: OS current version: %s" % (sn, re.findall(p, osVersion)[0]),\
                        sys._getframe().f_code.co_filename,sys._getframe().f_code.co_name,sys._getframe().f_lineno)

    def check_ui(self,sn):
        '''
        function:check uiautomator
        :param sn:
        :return:
        '''
        r = subprocess.Popen('''adb -s %s shell "ps | grep -E 'atx-agent|com.github.uiautomator'"''' % sn,
                             stdout=subprocess.PIPE, shell=True).stdout.read()
        logger.log_debug("%s" %(r),\
                 sys._getframe().f_code.co_filename,sys._getframe().f_code.co_name,sys._getframe().f_lineno)
        if b"uiautomator" not in r:
            self.apk_step(sn)

    def apk_step(self,sn):
        rtn = subprocess.Popen(
            "adb -s %s shell pm list packages" % sn, stdout=subprocess.PIPE, shell=True).stdout.readlines()
        packageList = list(map(lambda x: re.split(r"[:|\\]", str(x))[1].strip(), rtn))
        if "com.github.uiautomator" not in packageList or "com.github.uiautomator.test" not in packageList:
            # os.system('adb -s %s install -r %s' %
            #           (sn, os.path.join(os.getcwd(), "Source", "app-uiautomator.apk")))
            # os.system(
            #     'adb -s %s install -r %s' % (sn, os.path.join("Source", "app-uiautomator-test.apk")))
            logger.log_debug("init install uiautomator2",\
                            sys._getframe().f_code.co_filename,sys._getframe().f_code.co_name,sys._getframe().f_lineno)
            os.system('python -m uiautomator2 init')
        else:
            logger.log_warn("start uiautomator services",\
                            sys._getframe().f_code.co_filename,sys._getframe().f_code.co_name,sys._getframe().f_lineno)
            os.system('adb -s %s shell am start -n com.github.uiautomator/.IdentifyActivity' % sn)

'''
check install package message from fotaClient.log
'''
class Check_message(object):
    def __init__(self):
        self.delay_time = 240
        self.flag_list = ["Full","Diff"]
        # data_json = '/update/data.json'
        # fota_Client = '/update/fotaClient.log'
        # lib_hufota = '/update/libHUfota/libHUfota.log'
        self.message_full = ["Download.*HU.*New.*Full.*Package", "HU.*Package.*Download.*Finished",\
                   "Start.*Silence.*Install.*HU.*package", ".*1136.*FOTAFlash.*HU_start_upgrade.*Return:0.*"]
        self.message_diff = ["Download.*HU.*New.*Delta.*Package", "HU.*Package.*Download.*Finished",\
                   "Start.*Silence.*Install.*HU.*package", ".*1136.*FOTAFlash.*HU_start_upgrade.*Return:0.*"]

    def set_time(self, delay_time):
        self.delay_time = delay_time

    def get_time(self):
        return self.delay_time

    def check_data_file(self, sn):
        '''
        function: check data.json file
        :param sn:
        :return:
        '''
        delay_time = self.get_time()
        logger.log_debug("verify data.json if exist", \
                         sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name, sys._getframe().f_lineno)
        while True:
            cmd = 'adb -s %s shell "if [ -f %s ]; then %s wc -c %s | %s awk \'{print $1}\';fi"' % (sn,json_name,busybox,json_name,busybox)
            if removal(subprocess.check_output(cmd)) >= data_size:
                logger.log_info("data.json has existed", \
                                sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name,
                                sys._getframe().f_lineno)
                return True
            else:
                delay_time = delay_time - 1
                if delay_time >= 0:
                    logger.log_debug("wait ...", \
                                     sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name,
                                     sys._getframe().f_lineno)
                    time.sleep(2)
                else:
                    logger.log_error("data.json can not find...,request sever fail", \
                                     sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name,
                                     sys._getframe().f_lineno)
                    return False

    def check_fota_Client(self, sn, flag = None):
        '''
        function: check fotaClient.log
        :param sn:
        :param flag:
        :return:
        '''
        logger.log_debug("start to check fota_Client.log progress", \
                         sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name, sys._getframe().f_lineno)
        delay_time = self.get_time()

        if flag == self.flag_list[0]:
            msg_list = self.message_full
        elif flag == self.flag_list[1]:
            msg_list = self.message_diff
        for msg in msg_list:
            logger.log_info("check if start %s" % (msg.replace(".*", " ")), \
                            sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name,
                            sys._getframe().f_lineno)
            os.system('adb -s %s root' % sn)
            os.system('adb -s %s shell "mount -o remount,rw /"' % sn)
            os.system('adb -s %s shell "chmod -R 777 /update/"' % sn)
            cmd = 'adb -s %s shell "if [ -f /update/fotaClient.log ];then cat /update/fotaClient.log |grep -E "%s";fi' % (
            sn, msg)
            count = 0
            while count < delay_time:
                if check_log_message(sn, cmd, msg):
                    logger.log_info("has start %s\n" % (msg.replace(".*", " ")),\
                                    sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name,sys._getframe().f_lineno)
                    break
                else:
                    logger.log_warn("can not get %s field,wait 5s time" %(msg.replace(".*", " ")),\
                                sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name,sys._getframe().f_lineno)
                    time.sleep(5)
                count = count + 1
                if count >= delay_time:
                    logger.log_error("can not get %s field,wait 5s time" %(msg.replace(".*", " ")),\
                                        sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name,sys._getframe().f_lineno)
                    return False
        return True

    def check_system_directory(self, sn):
        '''
        function:check system directory
        :param sn:
        :return:
        '''
        count = self.get_time()
        cmd = 'adb -s %s shell "if [ -d /update/system/ ];then ls -al /update/system | %s wc -l ;fi"' % (sn,busybox)
        while True:
            try:
                result = removal(subprocess.check_output(cmd, shell=True))
                logger.log_info("%s %s" % (result, result1), \
                                sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name,
                                sys._getframe().f_lineno)
                if result.strip() != '' and result.strip() == '0':
                    time.sleep(20)
                    return True
                else:
                    count = count - 1
                    time.sleep(5)
                    if count <= 0:
                        return False
                    continue
            except subprocess.CalledProcessError as e:
                logger.log_info("%s" % (e.message), \
                                sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name,
                                sys._getframe().f_lineno)
                return False

    def check_libHUfota_exist(self,sn):
        count = self.get_time()
        cmd = 'adb -s %s shell "if [ -f %s ];then echo 0;else echo 1;fi"' % (sn, libHufota)
        while True:
            try:
                result = removal(subprocess.check_output(cmd, shell=True))
                logger.log_info("%s" % (result), \
                                sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name,
                                sys._getframe().f_lineno)
                if int(result.strip()) == 0:
                    time.sleep(20)
                    return True
                else:
                    count = count - 1
                    time.sleep(5)
                    if count <= 0:
                        logger.log_error("loop over and install package failed", \
                                         sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name,
                                         sys._getframe().f_lineno)
                        return False
            except subprocess.CalledProcessError as e:
                logger.log_error("%s" % (e.message), \
                                 sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name,
                                 sys._getframe().f_lineno)
                return False


    def check_libHUfota(self, sn):
        '''
        function:check libHUfota.log file
        :param sn:
        :return:
        '''
        count = self.get_time()
        # cmd = 'adb -s %s shell "if [ -f %s ];then grep -E "LibHUfota.*install.*success" \
        #                                                         %s | %s wc -l ;fi"' % (sn, libHufota, libHufota, busybox)
        cmd = 'adb -s %s shell "if [ -f %s ];then grep -E "LIBHUFOTA_MSG.*INSTALL_COMPLETE" \
                                                                %s | %s wc -l ;fi"' % (sn, libHufota, libHufota, busybox)
        while True:
            try:
                result = removal(subprocess.check_output(cmd, shell=True))
                logger.log_info("%s" % (result), \
                                sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name,
                                sys._getframe().f_lineno)
                if result.strip() != '' and int(result.strip()) >= 1:
                    time.sleep(20)
                    return True
                else:
                    count = count - 1
                    time.sleep(5)
                    if count <= 0:
                        logger.log_error("loop over and install package failed", \
                                         sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name,sys._getframe().f_lineno)
                        return False
            except subprocess.CalledProcessError as e:
                logger.log_error("%s" % (e.message), \
                                sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name,
                                sys._getframe().f_lineno)
                return False

class activeupgrade(object):
    def __init__(self):
        pass

    def delete_lvlog(self,sn):
        try:
            os.system('adb -s %s shell "mount -o rw,remount /;rm -rf %s;rm -rf %s"' %(sn, lvlog, settinglog))
        except Exception as e:
            logger.log_error("%s" %(e),\
                             sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name,sys._getframe().f_lineno)

    def check_activeupgrade_starui(self, sn):
        '''
        function:get start ui log
        :param sn:
        :return:
        '''
        cmd = 'adb -s %s shell "cat %s |grep createWindow|wc -l"' %(sn, lvlog)
        try:
            return int(removal(subprocess.check_output(cmd, shell=True)).strip())
        except Exception as e:
            logger.log_error("%s" %e,\
                             sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name,sys._getframe().f_lineno)

    def check_activeupgrade_starui_from_settings(self, sn):
        '''
        function:get start ui log
        :param sn:
        :return:
        '''
        cmd = 'adb -s %s shell "cat %s |grep LVSettingHomePageActivity:onStop|wc -l"' %(sn, settinglog)
        try:
            print(int(removal(subprocess.check_output(cmd, shell=True)).strip()))
            return int(removal(subprocess.check_output(cmd, shell=True)).strip())
        except Exception as e:
            logger.log_error("%s" %e,\
                             sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name,sys._getframe().f_lineno)


    def check_activeupgrade_cancleui(self, sn, delay_time = 20):
        '''
        function:get cancle ui log
        :param sn:
        :return:
        '''
        cmd = 'adb -s %s shell "cat %s |grep  -E "WindowUtils.*destroy"|wc -l"' % (sn, lvlog)
        try:
            while delay_time > 0:
                if int(removal(subprocess.check_output(cmd, shell=True)).strip()) >= 1:
                    logger.log_info("cancle ui successfully",\
                                    sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name,sys._getframe().f_lineno)
                    return 0
                else :
                    delay_time = delay_time - 1
                    time.sleep(0.5)
            logger.log_error("timeout,and can not find upgrade result",\
                             sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name,sys._getframe().f_lineno)
            return 1
        except Exception as e:
            logger.log_error("%s" % e,\
                             sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name,sys._getframe().f_lineno)
            return 1

    def check_install_progress(self, sn, pcan, delay_time= 360):
        '''
        function: check install progress
        :param sn:
        :param delay_time:
        :return:
        '''
        str_msg = "cat %s |grep -E 'upgrade progress info' | tail -n1|%s awk -F \'process\' \'{print $2}\' " % (
        lvlog, busybox)
        str_msg2 = "cat %s |grep -E 'upgrade progress info' | tail -n1|%s awk -F \'process\' \'{print $2}\' |%s awk  \'{print $1}\' " % (lvlog, busybox, busybox)
        # str_msg = "cat /sdcard/lvlog/com.living.ota/normal/123.log |grep -E 'upgrade progress info' | tail -n1|%s awk -F \'process\' \'{print $2}\' " %  (busybox)
        cmd = 'adb -s %s shell "%s"' % (sn, str_msg)
        # cmd1 = 'adb -s %s shell "if [ -f %s ];then grep -E "LIBHUFOTA_MSG.*INSTALL_COMPLETE" \
        #                                                                 %s | %s wc -l ;fi"' % (sn, libHufota, libHufota, busybox)
        cmd2 = 'adb -s %s shell "%s"' % (sn, str_msg2)
        # cmd ='adb -s %s shell "cat %s |grep -E "upgrade progress info" | tail -n1|%s awk -F \'process\' \'{print $2}\'"' %(sn, lvlog, busybox)
        try:
            while delay_time > 0:
                pcan.enter_ota_lopper()
                print(removal(subprocess.check_output(cmd, shell=True)).strip())
                # print(removal(subprocess.check_output(cmd1, shell=True)).strip())
                print(removal(subprocess.check_output(cmd2, shell=True)).strip())
                if '100' in removal(subprocess.check_output(cmd, shell=True)).strip() and 'errorCode 0' in removal(
                        subprocess.check_output(cmd, shell=True)).strip():
                    # if '100' in removal(subprocess.check_output(cmd, shell=True)).strip():
                    logger.log_info("install package successfully for active upgrade", \
                                    sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name,
                                    sys._getframe().f_lineno)
                    return 0
                elif '100' not in removal(
                        subprocess.check_output(cmd, shell=True)).strip() and 'errorCode 0' in removal(
                        subprocess.check_output(cmd, shell=True)).strip():
                    print("delay 0.5 second")
                    time.sleep(0.5)

                # if int(removal(subprocess.check_output(cmd2, shell=True)).strip()) > 1 and 'errorCode 0' not in removal(
                #         subprocess.check_output(cmd, shell=True)).strip():
                #     logger.log_error("install failed and errorCode is not zero", \
                #                      sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name,
                #                      sys._getframe().f_lineno)
                #     return 1
                delay_time = delay_time - 1
            logger.log_error("timeout,and can not find upgrade result", \
                             sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name,
                             sys._getframe().f_lineno)
            return 1
        except Exception as e:
            logger.log_error("%s" % e, \
                             sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name,
                             sys._getframe().f_lineno)
            return 1

    def check_activeupgrade_resultui(self, sn):
        '''
        function: check result log
        :param sn:
        :param delay_time:
        :return:
        '''
        # os.system("adb -s %s shell su" %(sn))
        # os.system("adb -s %s shell chmod 777 -R %s" %(sn, lvlog_path))
        cmd = 'adb -s %s shell "cat %s |grep -E "FotaUpgradeResult.*upgradeResult=true.*rebootResult=false.*"|%s wc -l "' %(sn,lvlog,busybox)
        try:
            print(int(removal(subprocess.check_output(cmd, shell=True)).strip()))
            if int(removal(subprocess.check_output(cmd, shell=True)).strip()) >= 1:
                print("antony@@@debug")
                logger.log_info("install package successfully for active upgrade",\
                                sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name,sys._getframe().f_lineno)
                return 0
            #     else :
            #         delay_time = delay_time - 1
            #         time.sleep(0.5)
            # logger.log_error("timeout,and can not find upgrade result",\
            #                  sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name,sys._getframe().f_lineno)
            # return 1
        except Exception as e:
            logger.log_error("%s" % e,\
                             sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name,sys._getframe().f_lineno)
            return 1

def removal(stg):
    '''
    funciton :removal msg
    :param stg:
    :return:
    '''
    new_stg = str(stg, encoding="utf-8").replace('\r\r\n','')
    return new_stg


def check_log_message(sn,cmd,msg):
    '''
    functioncheck log status
    :param:sn
    :return:
    '''
    message = subprocess.Popen(cmd,shell = True,stdout = subprocess.PIPE).stdout.read()
    new_message = removal(message)
    if new_message.strip() != '':
        logger.log_debug("%s successfully" %(msg.replace(".*"," ")),\
                        sys._getframe().f_code.co_filename,sys._getframe().f_code.co_name,sys._getframe().f_lineno)
        return True
    else :
        logger.log_warn("%s cannot finish,need to wait ...." %(msg.replace(".*"," ")),\
                        sys._getframe().f_code.co_filename,sys._getframe().f_code.co_name,sys._getframe().f_lineno)
        return False

def execute_cmd(cmd,delay_time=2):
    '''
    function:execute adb shell command
    :param sn:
    :return:
    '''
    p = subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE, shell= True,stdin = None)
    count = 0
    while count < delay_time:
        if p.poll() is None:
            time.sleep(5)
        else :
            return p.stdout.read()
        count = count + 1
    time.sleep(5)
    if p.poll() is None:
        p.kill()
        logger.log_debug("force to kill progress",\
                         sys._getframe().f_code.co_filename,sys._getframe().f_code.co_name,sys._getframe().f_lineno)
        return None
    else:
        logger.log_debug("%s" %(p.stdout.read()),\
                        sys._getframe().f_code.co_filename,sys._getframe().f_code.co_name,sys._getframe().f_lineno)
        return p.stdout.read()

def execute_cmd_getcode(cmd,delay_time = 2 ):
    '''
    get cmd return status:
    {0: successfully
    1: fail}
    :param cmd:
    :param delay_time:
    :return: ret_code
    '''
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, stdin=None)
    count = 0
    while count < delay_time:
        if p.poll() is None:
            time.sleep(5)
        else:
            return 0
        count = count + 1
    time.sleep(5)
    if p.poll() is None:
        p.kill()
        logger.debug("force to kill progress", \
                         sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name, sys._getframe().f_lineno)
        return 1


def reboot_device(sn):
    '''
    function:reboot devices
    :param sn:
    :return:
    '''
    os.system('adb -s %s root' % sn)
    os.system('adb -s %s shell "reboot"' % sn)
    logger.log_debug("reboot system...",\
                    sys._getframe().f_code.co_filename,sys._getframe().f_code.co_name,sys._getframe().f_lineno)

def delete_file(sn):
    '''
    function:delete file from /update
    :param sn:
    :return:
    '''
    updatedirectory_rw(sn)
    os.system('adb -s %s shell "mount -o rw,remount /;rm -rf /update/*;sleep 2;rm -rf /update/*"' %sn)
    logger.log_debug("delete /update/ directory",\
                    sys._getframe().f_code.co_filename,sys._getframe().f_code.co_name,sys._getframe().f_lineno)

def updatedirectory_rw(sn):
    '''
    function chmod update directory rw
    :param sn:
    :return:
    '''
    os.system('adb -s %s root' % sn)
    os.system('adb -s %s shell "mount -o remount,rw /"' % sn)
    os.system('adb -s %s shell "chmod -R 777 /update/*"' % sn)

def wait_hu_recovery(sn, wait_time = 20):
    '''
    function wait hu recovery
    :param sn:
    :return:
    '''
    # os.system('adb -s %s wait-for-device' % sn)
    #
    # while wait_time >= 0:
    #     retryRet = subprocess.Popen('adb -s %s shell "getprop | grep boot_completed"' % sn, stdout=subprocess.PIPE,
    #                                 shell=True).stdout.read()
    #     if 'sys.boot_completed' not in str(retryRet):
    #         logger.log_warn('%s: waitting for device boot up' % sn,\
    #                         sys._getframe().f_code.co_filename,sys._getframe().f_code.co_name,sys._getframe().f_lineno)
    #         time.sleep(6)
    #     else:
    #         return 0
    #     wait_time = wait_time - 1
    # return 1
    loop_count = 15
    p = subprocess.Popen('adb -s %s wait-for-device' % (sn), stderr=subprocess.PIPE, stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE, shell=False)
    while loop_count > 0:
        time.sleep(random.randint(20, 30))
        print(p.poll())
        if p.poll() is not None:
            logger.log_info("adb devices init successfully", \
                            sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name,
                            sys._getframe().f_lineno)
            break
        else:
            serial = Serial()
            serial.open_adb_through_serial(5)
        loop_count = loop_count - 1

    while wait_time >= 0:
        retryRet = subprocess.Popen('adb -s %s shell "getprop | grep boot_completed"' % sn, stdout=subprocess.PIPE,
                                    shell=True).stdout.read()
        if 'sys.boot_completed' not in str(retryRet):
            logger.log_warn('%s: waitting for device boot up' % sn, \
                            sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name,
                            sys._getframe().f_lineno)
            time.sleep(6)
        else:
            return 0
        wait_time = wait_time - 1
    return 1


def check_json_file(sn,delay_time = 60):
    '''
    function :check json file
    :param sn:
    :param delay_time: =60
    :return:
    '''
    while True:
        cmd ='adb -s %s shell "if [ -f %s ]; then %s wc -c %s | %s awk \'{print $1}\';fi"' % (sn,json_name,busybox,json_name,busybox)
        if removal(subprocess.check_output(cmd)) >= data_size:
            logger.log_debug("server respond OK and client receive data.json successfully",\
                            sys._getframe().f_code.co_filename,sys._getframe().f_code.co_name,sys._getframe().f_lineno)
            return 0
        else :
            delay_time = delay_time - 1
            if delay_time >= 0:
                logger.log_debug("wait 2s for data.json file ...",\
                                 sys._getframe().f_code.co_filename,sys._getframe().f_code.co_name,sys._getframe().f_lineno)
                time.sleep(2)
            else:
                logger.log_error("Client reveive fail",\
                                 sys._getframe().f_code.co_filename,sys._getframe().f_code.co_name,sys._getframe().f_lineno)
                return 1

def get_packagesize_from_json_file(sn, flag, delay_time = 240):
    '''
    function:get package size
    :param sn:
    :param delay_time:
    :return:
    '''
    if flag == "Full":
        str_msg = "%s sed 's/.*file_size.\{2\}\([0-9]*\).*/\\1/' %s" % (busybox, json_name)
    elif flag == "Diff":
        str_msg = "%s sed 's/.*file_size.\{2\}\([0-9]*\).*file_size.\{2\}\([0-9]*\).*/\\1/' %s" % (busybox, json_name)
    cmd = 'adb -s %s shell "if [ -f %s ]; then %s;fi"' % (sn, json_name, str_msg)
    while True:
        try:
            if removal(subprocess.check_output(cmd)):
                logger.log_debug("will download package size is %s" %(removal(subprocess.check_output(cmd))), \
                                sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name,
                                sys._getframe().f_lineno)
                return removal(subprocess.check_output(cmd))
            delay_time = delay_time - 1
            if delay_time >= 0:
                logger.log_debug("wait ...", \
                                 sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name,
                                 sys._getframe().f_lineno)
                time.sleep(2)
            else:
                logger.log_error("Client receive fail,can not find data.json file", \
                                 sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name,
                                 sys._getframe().f_lineno)
                return None
        except Exception as e:
            logger.log_error("%s" %(e),\
                             sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name,sys._getframe().f_lineno)
            return None


def get_packagename_from_json_file(sn, flag, delay_time = 240):
    if flag == "Full":
        str_msg = "%s sed 's/.*file_name.\{3\}\(.*\).\{3\}file_size.*/\\1/' %s" % (busybox, json_name)
    elif flag == "Diff":
        str_msg = "%s sed 's/.*file_name.\{3\}\(.*zip.*ed\).*file_size.*/\\1/' %s" % (busybox, json_name)
    cmd = 'adb -s %s shell "if [ -f %s ]; then %s;fi"' % (sn, json_name, str_msg)
    while True:
        try:
            if removal(subprocess.check_output(cmd)):
                logger.log_debug("will download package name is %s" % (removal(subprocess.check_output(cmd))),\
                                 sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name,sys._getframe().f_lineno)
                return removal(subprocess.check_output(cmd))
            delay_time = delay_time - 1
            if delay_time >= 0:
                logger.log_debug("wait ...", \
                                 sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name,
                                 sys._getframe().f_lineno)
                time.sleep(2)
            else:
                logger.log_error("Client receive fail,can not find data.json file", \
                                 sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name,
                                 sys._getframe().f_lineno)
                return None
        except Exception as e:
            logger.log_error("%s" %(e),\
                             sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name,sys._getframe().f_lineno)
            return None


# def get_diffpackagename_from_json_file(sn,delay_time = 240):
#     while True:
#         str_msg="/yf/bin/busybox sed 's/.*file_name.\{3\}\(.*\).\{3\}file_size.*/\\1/' / update / data.json"
#         # str_msg = "/yf/bin/busybox sed 's/.*file_name.\{3\}\(.*zip.*ed\).*file_size.*/\\1/' /update/data.json"
#         cmd = 'adb -s %s shell "if [ -f /update/data.json ]; then %s;fi"' % (sn, str_msg)
#         # print (removal(subprocess.check_output(cmd)))
#         if removal(subprocess.check_output(cmd)) is not None:
#             logger.log_debug("will download package name is %s" % (removal(subprocess.check_output(cmd))), \
#                              sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name,
#                              sys._getframe().f_lineno)
#             return removal(subprocess.check_output(cmd))
#         else:
#             delay_time = delay_time - 1
#             if delay_time >= 0:
#                 logger.log_debug("wait ...", \
#                                  sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name,
#                                  sys._getframe().f_lineno)
#                 time.sleep(2)
#             else:
#                 logger.log_error("Client receive fail,can not find data.json file", \
#                                  sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name,
#                                  sys._getframe().f_lineno)
#                 return None

def check_package_exist(sn, flag, delay_time = 240):
    '''
    function :Check if the package exists
    :param sn:
    :return:
    '''
    package_name = get_packagename_from_json_file(sn, flag)
    while True:
        cmd = 'adb -s %s shell "ls -al %s/%s |%s wc -l 2>/dev/null"' %(sn, package_path, package_name, busybox)
        try:
            print (removal(subprocess.check_output(cmd).strip()))
            if '1' in removal(subprocess.check_output(cmd).strip()):
                logger.log_debug("%s exists and downloading ..." %(package_name),\
                                 sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name,sys._getframe().f_lineno)
                return 0
            delay_time = delay_time - 1
            if delay_time >= 0:
                logger.log_debug("wait a minute...", \
                                 sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name,
                                 sys._getframe().f_lineno)
                time.sleep(5)
            else:
                logger.log_error("can not find %s," % (package_name), \
                                 sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name,
                                 sys._getframe().f_lineno)
                return 1
        except Exception as e:
            logger.log_error("%s" %(e),\
                             sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name,sys._getframe().f_lineno)
            return 1


def check_package_size(sn, flag, delay_time = 240):
    '''
    function:check package size
    :param sn:
    :param flag:
    :param delay_time:
    :return:
    '''
    package_name = get_packagename_from_json_file(sn,flag)
    if check_package_exist(sn,flag,delay_time) == 0:
        while True:
            str_msg = "ls -al %s/%s |%s awk '{print $5}'" %(package_path,package_name ,busybox)
            # str_msg = "ls -al /update/ota-full.zip|/oem/bin/busybox awk '{print $4}'"
            cmd = 'adb -s %s shell "%s"' % (sn, str_msg)
            try :
                if int (removal(subprocess.check_output(cmd)).strip()) >=0:
                    logger.log_debug("has downloaded package size: %s" % (removal(subprocess.check_output(cmd))), \
                                    sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name,
                                    sys._getframe().f_lineno)
                    return removal(subprocess.check_output(cmd)).strip()
                delay_time = delay_time - 1
                if delay_time >= 0:
                    logger.log_debug("wait ...", \
                                     sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name,
                                     sys._getframe().f_lineno)
                    time.sleep(2)
                else:
                    logger.log_debug("can not find package size ,may be has  download well", \
                                     sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name,
                                     sys._getframe().f_lineno)
                    return None
            except Exception as e:
                # print (delay_time)
                logger.log_error("%s" %(e),\
                                 sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name,sys._getframe().f_lineno)


def enable_network(sn):
    '''
    function:enable network
    :param sn:
    :return:
    '''
    cmd = 'adb -s %s shell "ifconfig %s up && sleep 2 && ifconfig |grep %s >> /dev/null && echo $?"' %(sn,network_device,network_device)
    try:
        if removal(subprocess.check_output(cmd)).strip() == '0':
            logger.log_debug("execute enable command successfully",\
                            sys._getframe().f_code.co_filename,sys._getframe().f_code.co_name,sys._getframe().f_lineno)
            return True
        else:
            logger.log_error("execute enable command fail",\
                             sys._getframe().f_code.co_filename,sys._getframe().f_code.co_name,sys._getframe().f_lineno)
            return False
    except Exception as e:
        logger.log_error("%s" %(e),\
                         sys._getframe().f_code.co_filename,sys._getframe().f_code.co_name,sys._getframe().f_lineno)
        return False

def disable_network(sn):
    '''
    function:disable network
    :param sn:
    :return:
    '''
    os.system("adb -s %s root" %(sn))
    cmd = 'adb -s %s shell "ifconfig %s down && sleep 2 && ifconfig |grep "%s" 2>&1 || echo $?"' %(sn,network_device,network_device)
    # print (removal(subprocess.check_output(cmd)).strip())
    try:
        if removal(subprocess.check_output(cmd)).strip() == '1':
            logger.log_debug("execute disable command successsfully",\
                            sys._getframe().f_code.co_filename,sys._getframe().f_code.co_name,sys._getframe().f_lineno)
            return True
        else:
            logger.log_error("execute disable command fail",\
                             sys._getframe().f_code.co_filename,sys._getframe().f_code.co_name,sys._getframe().f_lineno)
            return False
    except Exception as e:
        logger.log_error("%s" %(e),\
                         sys._getframe().f_code.co_filename,sys._getframe().f_code.co_name,sys._getframe().f_lineno)
        return  False
def get_vin_number(sn):
    '''
    function:get vin number
    :param sn:
    :return: str
    '''
    cmd = 'getprop |grep -r ".*vehicle\.vin"|%s awk -F \':\' \'{print $NF}\'| %s sed \'s/\[\([0-9A-Z]*\)\]/\\1/\'' %(busybox,busybox)
    # print (cmd)
    try:
        version = subprocess.Popen(
            'adb -s %s shell "%s"' % (sn, cmd), \
            stdout=subprocess.PIPE, shell=True).stdout.read()

        version = str(version, encoding="utf-8").replace('\r\r\n', '')
        return version.strip()
    except Exception as e:
        logger.log_error("%s" %e,\
                         sys._getframe().f_code.co_filename,sys._getframe().f_code.co_name,sys._getframe().f_lineno)

def get_software_version(sn):
    '''
    function:get software version
    :param sn:
    :return:version
    '''
    cut_cmd = 'cut -d"[" -f2 | cut -d"]" -f1'
    version = subprocess.Popen(
        'adb -s %s shell "getprop | grep -E ASE* | %s awk \'{print $NF}\'| %s |uniq"' % (sn, busybox, cut_cmd), \
        stdout=subprocess.PIPE, shell=True).stdout.read()
    version = str(version, encoding="utf-8").replace('\r\r\n', '')
    return version.strip()

def post_request(sn, header={}, data={}, url=None):
    '''
    platform :window
    function: post request
    :param sn:
    :return:
    '''
    try:
        if url == None:
            # url = "https://qa-hu1.wm-icenter.net/api/vehicle/fota/softwares"
            url = "https://qa-hu1.wm-icenter.net/api/v2/vehicle/fota/softwares"
        print("antony@@@debug")
        print(json.dumps(data))
        r = requests.post(url=url,headers=header,data=json.dumps(data))
        # print (header,data)
        print (r.text)
        if "success" in r.text and r.status_code == 200:
            logger.log_info("respond ok and status is :%s" %(r.status_code),\
                            sys._getframe().f_code.co_filename,sys._getframe().f_code.co_name,sys._getframe().f_lineno)
            return 0
        else:
            logger.log_error("respond failed and status is :%s" %(r.status_code),\
                             sys._getframe().f_code.co_filename,sys._getframe().f_code.co_name,sys._getframe().f_lineno)
            return 1
    except Exception as e:
        logger.log_error("may be has no network",\
                         sys._getframe().f_code.co_filename,sys._getframe().f_code.co_name,sys._getframe().f_lineno)
        return 1

def post_request_to_file(sn, header={}, data={}, url=None):
    try:
        if url == None:
            # url = "https://qa-hu1.wm-icenter.net/api/vehicle/fota/softwares"
            url = "https://qa-hu1.wm-icenter.net/api/v2/vehicle/fota/softwares"
        r = requests.post(url=url, headers=header, data=json.dumps(data))
        print (r.text)
        return write_request_content_file_and_push_to_hu(sn,r.text)
    except Exception as e:
        logger.log_error("%s" %(e),\
                         sys._getframe().f_code.co_filename,sys._getframe().f_code.co_name,sys._getframe().f_lineno)
        return 1

def write_request_content_file_and_push_to_hu(sn,msg):
    '''
    funciton :write data.json to android
    :param sn:
    :param msg:
    :return:
    '''
    current_path = os.getcwd()
    # print (current_path)
    current_time = int(time.time())
    current_filename = current_path+"\\"+str(current_time)+'.txt'
    # print (current_time,current_filename)
    with open(current_filename,'w') as f:
        f.write(msg)
    os.system('adb root')
    cmd = 'adb -s %s push %s %s' %(sn, current_filename, json_name)
    os.system(cmd)
    os.remove(current_filename)
    cmd = 'adb -s %s shell ""if [ -f %s ];then echo "0";else echo "1";fi"' %(sn, json_name)
    return int(removal(subprocess.check_output(cmd)).strip())


def get_md5_value(sn, package_name, new_name):
    '''
    function : get package md5 value
    :param sn:
    :param package_name:
    :param new_name:
    :return:
    '''
    try:
        os.system('adb -s %s root' %(sn))
        cmd = 'adb -s %s  shell "mv /%s/%s /%s/%s;md5sum /%s/%s |%s awk \'{print $1}\'"'\
                            %(sn,package_path,package_name,package_path,new_name,package_path,new_name,busybox)
        return removal(subprocess.check_output(cmd)).strip()
    except Exception as e:
        logger.log_error("%s" %(e),sys._getframe().f_code.co_filename,sys._getframe().f_code.co_name,sys._getframe().f_lineno)

def get_md5_value_from_datafile(sn, flag):
    '''
    function: get md5 value from datafile
    :param sn:
    :return:
    '''
    try:
        os.system('adb -s %s root' %(sn))
        if flag == "Full":
            str_msg = "%s sed  \'s/.*sign.\{3\}\(.*\).\{3\}package_type.*/\\1/\' %s" %(busybox,json_name)
        elif flag == "Diff":
            str_msg = "%s sed  \'s/.*sign.\{3\}\(.*\).\{3\}package_type.*sign.\{3\}\(.*\).\{3\}package_type.*/\\1/\' %s" %(busybox,json_name)
        cmd = 'adb -s %s shell "%s"' %(sn,str_msg)
        return removal(subprocess.check_output(cmd)).strip()
    except Exception as e:
        logger.log_error("%s" %(e),sys._getframe().f_code.co_filename,sys._getframe().f_code.co_name,sys._getframe().f_lineno)


def delete_update_directory(sn):
    '''
    function: delete update directory
    :param sn:
    :return:
    '''
    os.system("adb -s %s root" %(sn))
    cmd = "if [ -d /update ] && [ $(ls -al /update/| %s wc -l) != 0 ];then mount -o rw,remount /;rm -rf /update/*;fi" %(busybox)
    try:
        subprocess.check_output('adb -s %s shell "%s"' %(sn,cmd))
    except Exception as e:
        logger.log_error("%s" %(e),\
                         sys._getframe().f_code.co_filename,sys._getframe().f_code.co_name,sys._getframe().f_lineno)

def kill_fota_daemon(sn):
    '''
    function : kill fota daemon
    :param sn:
    :return:
    '''
    cmd = 'adb -s %s shell "ps -ef|grep FotaModule|grep -v grep|%s awk \'{print $2}\'|xargs kill -9"' %(sn,busybox)
    try:
        subprocess.check_output(cmd)
        return 0
    except Exception as e:
        logger.log_error("%s" %(e),\
                         sys._getframe().f_code.co_filename,sys._getframe().f_code.co_name,sys._getframe().f_lineno)
        return 1

def start_fota_daemon_child(sn, cmd):
    '''
    function run fota daemon process
    :param sn:
    :param cmd:
    :return:
    '''
    cmd_start_fotamodule = 'adb -s %s shell "LD_LIBRARY_PATH=/system/lib/fotalib /system/bin/FotaModule &' % (sn)
    execute_cmd(cmd_start_fotamodule)
    if int(removal(subprocess.check_output(cmd))) >= 1:
        logger.log_info("start fota module success", \
                        sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name, sys._getframe().f_lineno)
        return 0
    else:
        logger.log_error("start fota module failed", \
                         sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name, sys._getframe().f_lineno)
        return 1

def start_fota_daemon(sn):
    '''
    function:start fota daemon process
    :param sn:
    :return:
    '''
    os.system("adb -s %s root" %(sn))
    cmd_check_fotamodule = 'adb -s %s shell "ps -ef|grep FotaModule|grep -v grep | %s wc -l"' %(sn, busybox)
    # print(int(removal(subprocess.check_output(cmd_check_fotamodule)).strip()))
    try:
        # if int(removal(subprocess.check_output(cmd_check_fotamodule)).strip()) == 0:
        #     return start_fota_daemon_child(sn,cmd_check_fotamodule)
        # elif int(removal(subprocess.check_output(cmd_check_fotamodule)).strip()) > 0:
        #     kill_fota_daemon(sn)
        #     return start_fota_daemon_child(sn, cmd_check_fotamodule)
        return 0
    except Exception as e:
        logger.log_error("error as follow: %s" %(e),\
                         sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name,sys._getframe().f_lineno)
        return 1

def send_signal(sn, arry_list=[], device_flag = None, cycle = 10):
    '''
    function :send update signal and install package through ui
    :param sn: 
    :param cycle = 100: 
    :return: 
    '''
    def send_tbox_signal(pcan):
        try:
            pcan.enterota()
            if ag.check_install_progress(sn,pcan) == 1:
                pcan.poweron_and_clean()
                return 1
        except Exception as e:
            logger.log_error("%s" %(e),\
                             sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name,sys._getframe().f_lineno)
            pcan.poweron_and_clean()
            return 1
    try:
        pcan = SC.PCAN()
        ag = activeupgrade()
        logger.log_info("delete lvlog", \
                        sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name, sys._getframe().f_lineno)
        ag.delete_lvlog(sn)
        time.sleep(1)
        for i in range(5):
            logger.log_info("start install ui",sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name, sys._getframe().f_lineno)
            if ag.check_activeupgrade_starui(sn) == 0:
                for i in range(cycle):
                    pcan.send_arry(arry_list)
        time.sleep(5)
        serial = Serial()
        logger.log_info("start enter ui to upgrade package", \
                        sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name, sys._getframe().f_lineno)
        # print("2222222")
        # serial.enter_softupgrade_page()
        logger.log_info("start click install button",\
                        sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name, sys._getframe().f_lineno)
        serial.active_upgrade()
        logger.log_info("start send ota signal", \
                        sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name, sys._getframe().f_lineno)
        pcan.enterota()
        time.sleep(5)
        logger.log_info("check install progress...", \
                        sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name, sys._getframe().f_lineno)
        if ag.check_install_progress(sn, pcan) == 1:
            pcan.poweron_and_clean()
            return 1
        if device_flag == "tbox":
            logger.log_info("first package install successfully,start send exit ota signal",\
                            sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name, sys._getframe().f_lineno)
            pcan.exit_ota_lopper()
            logger.log_info("second send enter ota signal",\
                            sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name, sys._getframe().f_lineno)
            send_tbox_signal(pcan)
        # logger.log_info("start send power on signal", \
        #                 sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name, sys._getframe().f_lineno)
        # pcan.poweron()
        # logger.log_info("power on signal done", \
        #                 sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name, sys._getframe().f_lineno)
        for i in range(cycle * 9):
            logger.log_info("start send exit ota normal signal,send signal times is:%s" % (i), \
                            sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name,
                            sys._getframe().f_lineno)
            pcan.exitota()
            logger.log_info("wait install successfully", \
                            sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name,
                            sys._getframe().f_lineno)
            if ag.check_activeupgrade_resultui(sn) == 0:
                pcan.clean()
                logger.log_info("check laster result successfully", \
                                sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name,
                                sys._getframe().f_lineno)
                return 0
        pcan.clean()
        logger.log_error("check laster result failed", \
                         sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name, sys._getframe().f_lineno)
        return 1
    except Exception as e:
        logger.log_error("%s" %(e),\
                         sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name,sys._getframe().f_lineno)
        return 1


def alway_send_signal(sn, arry_list=[], delay_time = 300):
    try:
        pcan = SC.PCAN()
        ag = activeupgrade()
        logger.log_info("delete lvlog", \
                        sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name, sys._getframe().f_lineno)
        ag.delete_lvlog(sn)
        logger.log_info("start send signal ,and wait install ui...")
        while delay_time > 0:
            if ag.check_activeupgrade_starui(sn) == 0:
                    pcan.send_arry(arry_list)
                    time.sleep(0.5)
                    delay_time = delay_time - 1
            else:
                pcan.poweron_and_clean()
                return 0
        pcan.poweron_and_clean()
        return 1
    except Exception as e:
        logger.log_error("%s" %e,\
                         sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name, sys._getframe().f_lineno)
        return 1


def upgrade_through_ui(sn, arry_list = [],device_flag = None, cycle = 10):
    def send_tbox_signal(pcan):
        try:
            pcan.enterota()
            if ag.check_install_progress(sn,pcan) == 1:
                pcan.poweron_and_clean()
                return 1
        except Exception as e:
            logger.log_error("%s" %(e),\
                             sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name,sys._getframe().f_lineno)
            pcan.poweron_and_clean()
            return 1
    try:
        serial = Serial()
        pcan = SC.PCAN()
        for i in range(100):
            pcan.send_arry(arry_list)
        ag = activeupgrade()
        logger.log_info("delete lvlog", \
                        sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name, sys._getframe().f_lineno)
        ag.delete_lvlog(sn)
        logger.log_info("start enter ui to upgrade package", \
                        sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name, sys._getframe().f_lineno)
        serial.active_upgrade()
        logger.log_info("start send ota normal signal",\
                        sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name, sys._getframe().f_lineno)
        pcan.enterota()
        if ag.check_install_progress(sn,pcan) == 1:
            logger.log_error("has enter ota normal,but can not install",\
                             sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name, sys._getframe().f_lineno)
            pcan.poweron_and_clean()
            return 1

        if device_flag == "tbox":
            logger.log_info("first package install successfully,start send exit ota signal",\
                            sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name, sys._getframe().f_lineno)
            pcan.exit_ota_lopper()
            logger.log_info("second send enter ota signal",\
                            sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name, sys._getframe().f_lineno)
            send_tbox_signal(pcan)

        for i in range(cycle * 9):
            logger.log_info("start send exit ota normal signal,send signal times is:%s" % (i), \
                            sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name,
                            sys._getframe().f_lineno)
            pcan.exitota()
            logger.log_info("wait install successfully", \
                            sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name,
                            sys._getframe().f_lineno)
            if ag.check_activeupgrade_resultui(sn) == 0:
                pcan.clean()
                logger.log_info("check laster result successfully", \
                                sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name,
                                sys._getframe().f_lineno)
                return 0
        pcan.clean()
        logger.log_error("check laster result failed", \
                         sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name, sys._getframe().f_lineno)
        return 1

        # logger.log_info("start send exit ota normal signal",\
        #                 sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name, sys._getframe().f_lineno)
        # pcan.exitota()
        # pcan.clean()
        # logger.log_info("wait install successfully", \
        #                 sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name, sys._getframe().f_lineno)
        # if ag.check_activeupgrade_resultui(sn) == 0:
        #     return 0
        # else:
        #     logger.log_error("maybe can not exit 99% ui page,so upgrade failed",\
        #                      sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name, sys._getframe().f_lineno)
        #     return 1
    except Exception as e:
        logger.log_error("%s" %(e),\
                         sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name, sys._getframe().f_lineno)
        return 1

def cancle_install_through_ui(sn):
    try:
        serial = Serial()
        ag = activeupgrade()
        logger.log_info("delete lvlog", \
                        sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name, sys._getframe().f_lineno)
        ag.delete_lvlog(sn)
        logger.log_info("start cancle ui ", \
                        sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name, sys._getframe().f_lineno)
        serial.cancel_activeupgrade()
        if ag.check_activeupgrade_cancleui(sn) == 0:
            logger.log_info("cancle successfully", \
                            sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name,
                            sys._getframe().f_lineno)
            return 0
        else:
            return 1
    except Exception as e:
        logger.log_error("%s" % (e), \
                         sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name, sys._getframe().f_lineno)
        return 1

def cancleinstall_through_setting(sn, arry_list = [],cycle = 100):
    try:
        serial = Serial()
        pcan = SC.PCAN()
        ag = activeupgrade()
        logger.log_info("delete lvlog", \
                        sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name, sys._getframe().f_lineno)
        ag.delete_lvlog(sn)
        for i in range(cycle):
            pcan.send_arry(arry_list)
        serial.enter_softupgrade_page()
        for i in range(5):
            if ag.check_activeupgrade_starui_from_settings(sn) == 0:
                time.sleep(6)
            else :
                serial.cancle_activeupgrade_through_settings()
                if ag.check_activeupgrade_cancleui(sn) == 0:
                    pcan.poweron_and_clean()
                    return 0
                else:
                    pcan.poweron_and_clean()
                    return 1
        pcan.poweron_and_clean()
        return 1
    except Exception as e:
        logger.log_error("%s" %(e),\
                         sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name, sys._getframe().f_lineno)
        return 1

def activeupgrade_through_setting(sn, arry_list = [], device_flag = None, cycle = 100):
    def send_tbox_signal(pcan):
        try:
            pcan.enterota()
            if ag.check_install_progress(sn,pcan) == 1:
                pcan.poweron_and_clean()
                return 1
        except Exception as e:
            logger.log_error("%s" %(e),\
                             sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name,sys._getframe().f_lineno)
            pcan.poweron_and_clean()
            return 1
    try:
        serial = Serial()
        pcan = SC.PCAN()
        ag = activeupgrade()
        logger.log_info("delete lvlog", \
                        sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name, sys._getframe().f_lineno)
        ag.delete_lvlog(sn)
        time.sleep(5)
        for i in range(5):
            if ag.check_activeupgrade_starui(sn) == 0:
                for i in range(cycle):
                    pcan.send_arry(arry_list)
            else :
                time.sleep(5)
                serial.cancel_activeupgrade()
                time.sleep(5)
                if ag.check_activeupgrade_cancleui(sn) == 0:
                    logger.log_debug("cancle successfully", \
                                     sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name,
                                     sys._getframe().f_lineno)
                    ag.delete_lvlog(sn)
                    logger.log_info("start enter soft upgrade page", \
                                    sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name,
                                    sys._getframe().f_lineno)
                    serial.enter_softupgrade_page()
                    for i in range(5):
                        if ag.check_activeupgrade_starui_from_settings(sn) == 0:
                            print("aaaaa")
                            time.sleep(6)
                        else:
                            time.sleep(5)
                            logger.log_info("start upgrade through setting page", \
                                            sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name,
                                            sys._getframe().f_lineno)
                            serial.activeupgrade_through_settings()
                            pcan.enterota()
                            time.sleep(5)
                            if ag.check_install_progress(sn,pcan) == 1:
                                pcan.poweron_and_clean()
                                return 1
                            if device_flag == "tbox":
                                pcan.exit_ota_lopper()
                                send_tbox_signal(pcan)
                            for i in range(cycle * 9):
                                logger.log_info("start send exit ota normal signal,send signal times is:%s" % (i), \
                                                sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name,
                                                sys._getframe().f_lineno)
                                pcan.exitota()
                                logger.log_info("wait install successfully", \
                                                sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name,
                                                sys._getframe().f_lineno)
                                if ag.check_activeupgrade_resultui(sn) == 0:
                                    pcan.clean()
                                    logger.log_info("check laster result successfully", \
                                                    sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name,
                                                    sys._getframe().f_lineno)
                                    return 0
                            pcan.clean()
                            logger.log_error("check laster result failed", \
                                             sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name,
                                             sys._getframe().f_lineno)
                            return 1
                    return 1
                else:
                    pcan.clean()
                    logger.log_error("cancle install through ui", \
                                     sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name,sys._getframe().f_lineno)
                    return 1
        pcan.poweron_and_clean()
        return 1
    except Exception as e:
        pcan.poweron_and_clean()
        logger.log_error("%s" %(e),\
                         sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name, sys._getframe().f_lineno)
        return 1

def check_md5_status(sn, delay_time=240):
    '''
    function:check md5 value status
    :param sn:
    :param delay_time:
    :return:
    '''
    try:
        cmd = 'adb -s %s shell "grep -Er "verify.*OTA.*success" %s |%s wc -l"' % (sn, log_path, busybox)
        while delay_time > 0:
            if removal(subprocess.check_output(cmd)).strip() == '2':
                logger.log_info("check md5 successfully", \
                                sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name,
                                sys._getframe().f_lineno)
                return 0
            else:
                delay_time = delay_time - 1
                time.sleep(1)
        logger.log_error("check md5 timeout", \
                         sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name,
                         sys._getframe().f_lineno)
        return 1
    except Exception as e:
        logger.log_error("%s" % (e), \
                         sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name,
                         sys._getframe().f_lineno)
        return 1

def Set_Logcat_Message(sn):
    '''
    function for set logcat
    :param module_name:
    :return:
    '''
    lgc = lcf.logcat()
    lgc.set_file_name("logcat.log")
    lgc.set_file_path("/update")
    lgc.collect_logcat_file(sn, lgc.get_file_path(), lgc.get_file_name())
    return lgc

def Get_Logcat_Message(sn, lgc):
    '''
    function for get logcat
    :param module_name:
    :return:
    '''
    lgc = lcf.logcat()
    try:
        print (lgc)
        lgc.set_pull_file_path("..\Result\%s\%s" %(loger.file_dir,loger.case_name_directory))
        lgc.pull_logcat_file(sn ,lgc.get_file_name(), lgc.get_file_path(),\
                             lgc.get_pull_file_path(), time.strftime('%Y-%m-%d__%H-%M-%S',time.localtime(time.time())))
    except Exception as e:
        logger.log_error("%s" %e,\
                         sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name, sys._getframe().f_lineno)


def Set_Screencap_Message(sn):
    '''
    function for set screencap
    :param module_name:
    :return:
    '''
    snp = scp.screen_cap()
    snp.set_picture_name("screen.png")
    snp.set_picture_path("/update")
    snp.get_screencap(sn, snp.get_picture_name(), snp.get_picture_path())
    return snp


def Get_Screencap_Message(sn, snp):
    '''
    function for get screencap
    :return:
    '''
    snp.set_pull_picture_path("..\Result\%s\%s" %(loger.file_dir,loger.case_name_directory))
    snp.pull_screencap(sn, snp.get_pull_picture_path(), snp.get_picture_path(), \
                       snp.get_picture_name(),time.strftime('%Y-%m-%d__%H-%M-%S', time.localtime(time.time())))

def Get_libHU_Message(sn):
    try:
        libHU_path = "..\Result\%s\%s" %(loger.file_dir,loger.case_name_directory)
        cm = Check_message()
        # if cm.check_libHUfota_exist(sn) == True:
        #     file_name = removal(subprocess.check_output('adb -s %s shell "ls /update/log/libHU*"' %(sn))).strip()
        #     os.system("adb -s %s pull %s %s/%s_%s" \
        #               %(sn,file_name,libHU_path,time.strftime('%Y-%m-%d__%H-%M-%S', time.localtime(time.time())), "libHUfota.log"))
        os.system("adb -s %s pull /sdcard/lvlog/com.living.ota/normal/. %s/%s_%s" \
                  %(sn,libHU_path,time.strftime('%Y-%m-%d__%H-%M-%S', time.localtime(time.time())), "com_living_ota.log"))
        os.system("adb -s %s pull /update/log/.  %s/%s_%s" \
                  %(sn,libHU_path,time.strftime('%Y-%m-%d__%H-%M-%S', time.localtime(time.time())), "update_log"))
    except Exception as e:
        logger.log_error("%s" %(e),\
                         sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name, sys._getframe().f_lineno)



def open_tbox_adb():
    time.sleep(10)
    import pyautogui
    screenWidth, screenHeight = pyautogui.size()
    print("height:%s width:%s" %(screenHeight,screenWidth))
    currentMouseX, currentMouseY = pyautogui.position()
    print("currentMouseX:%s currentMouseY:%s" %(currentMouseX,currentMouseY))
    pyautogui.moveTo(currentMouseX, currentMouseY)
    pyautogui.click()
























