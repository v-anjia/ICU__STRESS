'''
for icu test case class
@author : antony jiangwei
date: 2019/11/26
'''
import os
import time
import sys
import serial

import random
import multiprocessing
import threading
from log import logger as loger
from Common import SSH_Connection as sshc
from Common import Signal_List as SL
from Common import Signal_Common as SC
from Common import Common as co
from Common import Picture_Compare as pc
from Common import Icu_Common_Adb as ica
from multiprocessing import pool

# adb = co.ADB_SN()
# adb_number = adb.get_sn_from_adb_command()[0]
execute_adb_command = ica.excute_adb_command()
logger = loger.Current_Module()

ssh = sshc.SSH_Client()
sftp = sshc.SFTP_Client()
ping_object = sshc.Ping_Object()
package = co.Install_Package()
CPP = pc.Compare_Picture()

username = "root"
password = "wm123456"
script_name = "/root/configurate_ase3.sh"
save_picture_directory = "screenshot -file=/fs/usb0/"
udisk_path = "/fs/usb0/"
screen_command = "screenshot -file="
# save_picture_directory = "/tmp/"
# create_screen_directory = "mkdir -p /fs/usb0/screen/"
delete_screen_picture = "rm -rf /fs/usb0/*.png"
root_read_write = "mount -uw  /fs/usb0/"
icu_logfile = "/fs/usb0/cluster_service.log"
mcu_logfile = "/fs/usb0/mcu_service.log"

collect_icu_log = "nohup slog2info -w -b cluster_service > %s &" %(icu_logfile)
collect_mcu_log = "nohup slog2info -w -b mcuservice > %s &" %(mcu_logfile)

kill_icu_progress = "pidin arg|grep slog2info|grep cluster_service|awk '{print \$1}' | xargs -n 1 slay -9"
kill_mcu_progress = "pidin arg|grep slog2info|grep mcuservice|awk '{print \$1}' | xargs -n 1 slay -9"

# kill_icu_progress = "slay -9 $(pidin arg|grep slog2info  |grep cluster_service | awk '{print $1}') "
# kill_mcu_progress = "slay -9 $(pidin arg|grep slog2info  |grep mcuservice | awk '{print $1}') "

delete_icu_logfile = "rm -rf %s" %(icu_logfile)
delete_mcu_logfile = "rm -rf %s" %(mcu_logfile)

telnet = "telnet.sh"
qnx_ip = "192.168.225.39"
ftpget = "busybox ftpget -u root"

adb_mount = "mount -o rw,remount /"
android_icu_file = "/cluster_service.log"
android_mcu_file = "/mcu_service.log"
port = 22

def save_picture_and_delete(sn, picture_full_path, android_full_path, local_picture_location):
    logger.log_debug("screenshot picturen and save", \
                     sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name, sys._getframe().f_lineno)

    execute_adb_command.execute_command_to_qnx_system(sn, telnet, picture_full_path)

    logger.log_debug("copy picture from qnx to android", \
                     sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name, sys._getframe().f_lineno)
    execute_adb_command.copy_file_from_qnx_to_android(sn, ftpget, qnx_ip, picture_full_path, android_full_path)
    logger.log_debug("rm picture from qnx", \
                     sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name, sys._getframe().f_lineno)
    execute_adb_command.execute_command_to_qnx_system(sn, telnet, delete_screen_picture)

    logger.log_debug("copy picture to local", \
                     sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name, sys._getframe().f_lineno)
    execute_adb_command.pull_file_to_local(sn, android_full_path, local_picture_location)

    logger.log_debug("rm picture from android", \
                     sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name, sys._getframe().f_lineno)
    os.system('adb -s %s shell "%s"' % (sn, "rm -rf /*.png"))

def log_kill_copy_local(sn, local_screen_path):
    logger.log_debug("kill icu progress :%s" % (kill_icu_progress), \
                     sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name, sys._getframe().f_lineno)
    execute_adb_command.execute_command_to_qnx_system(sn, telnet, kill_icu_progress)

    logger.log_debug("copy icu log from qnx to android", \
                     sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name, sys._getframe().f_lineno)
    execute_adb_command.copy_file_from_qnx_to_android(sn, ftpget, qnx_ip, icu_logfile, android_icu_file)

    logger.log_debug("rm icu log from qnx", \
                     sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name, sys._getframe().f_lineno)
    execute_adb_command.execute_command_to_qnx_system(sn, telnet, delete_icu_logfile)

    logger.log_debug("copy icu log to local", \
                     sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name, sys._getframe().f_lineno)

    execute_adb_command.pull_file_to_local(sn, android_icu_file, local_screen_path)

    logger.log_debug("kill mcu progress :%s" % (kill_mcu_progress), \
                     sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name, sys._getframe().f_lineno)
    execute_adb_command.execute_command_to_qnx_system(sn, telnet, kill_mcu_progress)

    logger.log_debug("copy mcu log from qnx to android", \
                     sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name, sys._getframe().f_lineno)
    execute_adb_command.copy_file_from_qnx_to_android(sn, ftpget, qnx_ip, mcu_logfile, android_mcu_file)

    logger.log_debug("rm icu log from qnx", \
                     sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name, sys._getframe().f_lineno)
    execute_adb_command.execute_command_to_qnx_system(sn, telnet, delete_mcu_logfile)

    logger.log_debug("copy mcu log to local", \
                     sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name, sys._getframe().f_lineno)
    execute_adb_command.pull_file_to_local(sn, android_mcu_file, local_screen_path)

    logger.log_debug("rm icu & mcu log from android", \
                     sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name, sys._getframe().f_lineno)
    os.system('adb -s %s shell "%s"' % (sn, "rm -rf /*.log"))


def rm_icu_and_mcu_log(sn):
    logger.log_debug("rm icu log from qnx", \
                     sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name, sys._getframe().f_lineno)
    execute_adb_command.execute_command_to_qnx_system(sn, telnet, delete_icu_logfile)

    logger.log_debug("rm icu log from qnx", \
                     sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name, sys._getframe().f_lineno)
    execute_adb_command.execute_command_to_qnx_system(sn, telnet, delete_mcu_logfile)

    logger.log_debug("rm icu & mcu log from android", \
                     sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name, sys._getframe().f_lineno)
    os.system('adb -s %s shell "%s"' % (sn, "rm -rf /*.log"))


class init_environment(object):
    def __init__(self, ip_address, serial_device):
        self.ip_address = ip_address
        self.serial_device = serial_device
        self.baudrate = 115200

    def set_ip_address(self, ip_address):
        self.ip_address = ip_address

    def get_ip_address(self):
        return self.ip_address

    def set_serial_device(self, serial_device):
        self.serial_device = serial_device

    def get_serial_device(self):
        return self.serial_device

    def start_collect_log(self):
        ser = serial.Serial(self.get_serial_device(), self.baudrate)
        logger.log_info("start collect icu log", \
                        sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name,
                        sys._getframe().f_lineno)
        ser.write(("slog2info -w -b cluster_service >> /cluster_service.log\r\n").encode('utf-8'))

        logger.log_info("start collect mcu log", \
                        sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name,
                        sys._getframe().f_lineno)
        ser.write(("slog2info -w -b mcuservice >> /mcu_service.log\r\n").encode('utf-8'))
        ser.close()


    def __call__(self, *args, **kwargs):
        try:
            logger.log_info("configurate qnx system ip address", \
                            sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name,
                            sys._getframe().f_lineno)
            ser = serial.Serial(self.get_serial_device(), self.baudrate)
            ser.write(("mount -uw  / \r\n").encode('utf-8'))
            time.sleep(random.randint(3,5))
            ser.write(("mount -uw  /fs/usb0/ \r\n").encode('utf-8'))
            time.sleep(random.randint(3, 5))

            ser.write(("cp /etc/password   /etc/password.bak \r\n").encode('utf-8'))
            time.sleep(random.randint(3, 5))

            ser.write(("cp /etc/password.bak   /etc/password \r\n").encode('utf-8'))
            time.sleep(random.randint(3, 5))

            ser.write(("chmod 777 /etc/password\r\n").encode('utf-8'))
            time.sleep(random.randint(3,5))

            ser.write(("ifconfig ax0 %s \r\n" % (self.get_ip_address())).encode('utf-8'))
            time.sleep(random.randint(3, 5))
            # ser.write(("ssh-keygen -R %s\r\n" % (self.get_ip_address())).encode('utf-8'))
            # time.sleep(random.randint(3, 5))
            ser.write(("random -U 16:16 -t\r\n").encode('utf-8'))
            time.sleep(random.randint(3, 5))
            ser.write(("mkdir -p /var/ssh\r\n").encode('utf-8'))
            time.sleep(random.randint(3, 5))
            ser.write(("rm -rf /var/ssh/*\r\n").encode('utf-8'))
            time.sleep(random.randint(3, 5))
            ser.write(("ssh-keygen -N '' -q -t dsa  -f /var/ssh/ssh_host_dsa_key\r\n").encode('utf-8'))
            time.sleep(random.randint(3, 5))
            ser.write(("ssh-keygen -N '' -q -t rsa  -f /var/ssh/ssh_host_rsa_key\r\n").encode('utf-8'))
            time.sleep(random.randint(3, 5))
            ser.write(("chmod 700 /var/ssh/*\r\n").encode('utf-8'))
            time.sleep(random.randint(3, 5))
            ser.write(("echo \"sshd:x:74:74:Privilege-separated SSH:/var/empty/sshd:/sbin/nologin\" >> /etc/passwd\r\n").encode('utf-8'))
            time.sleep(random.randint(3, 5))
            ser.write(("mkdir -p /var/chroot/sshd\r\n").encode('utf-8'))
            time.sleep(random.randint(3, 5))
            ser.write(("chmod 755 /var/chroot/sshd\r\n").encode('utf-8'))
            time.sleep(random.randint(3, 5))
            ser.write(("/usr/sbin/sshd &\r\n").encode('utf-8'))
            time.sleep(random.randint(3, 5))
            ser.write(("\r\n").encode('utf-8'))
            # ser.write(("nohup slog2info -w -b cluster_service >> /cluster_service.log &\r\n").encode('utf-8'))
            # time.sleep(random.randint(1,3))
            # ser.write(("nohup slog2info -w -b mcuservice >> /mcu_service.log &\r\n").encode('utf-8'))
            time.sleep(random.randint(1,3))
            ser.close()

        except Exception as e:
            logger.log_error("%s" % (e), \
                             sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name,
                             sys._getframe().f_lineno)

class ICU_Common(object):
    
    def __init__(self):
        pass

    def excute_qnx_command(self, port, password = None,username = None, ip_address = None, command = []):
        logger.log_info("excute command:%s" %(command),\
                        sys._getframe().f_code.co_filename,sys._getframe().f_code.co_name,sys._getframe().f_lineno)
        ssh.set_ip_address(ip_address)
        ssh.set_password(password)
        ssh.set_port(port)
        ssh.set_username(username)
        ssh.ssh_connect()
        for i in command:
            ssh.excute_command("%s" %(i),20)
        return ssh

    def screen_shot_and_transfer_to_local(self, port, password = None,username = None, ip_address = None, command = None,command1 = None, orign_path = None, later_path = None):
        logger.log_info("screenshot picture and copy picture to local",\
                        sys._getframe().f_code.co_filename,sys._getframe().f_code.co_name,sys._getframe().f_lineno)
        ssh.set_ip_address(ip_address)
        ssh.set_password(password)
        ssh.set_port(port)
        ssh.set_username(username)
        ssh_object = ssh.ssh_connect()
        ssh.excute_command("%s" %(command+orign_path),20)
        sftp_object = sftp.ssh_sftp(ssh_object)
        print(orign_path)
        print(later_path)
        sftp.get_file_from_qnx_to_local(orign_path,later_path)
        ssh.excute_command("%s" %(command1),20)

    def copy_logfile_to_local(self, port, password = None,username = None, ip_address = None, command = None, orign_path = None, later_path = None):
        logger.log_info("configurate qnx",\
                        sys._getframe().f_code.co_filename,sys._getframe().f_code.co_name,sys._getframe().f_lineno)
        ssh.set_ip_address(ip_address)
        ssh.set_password(password)
        ssh.set_port(port)
        ssh.set_username(username)
        ssh_object = ssh.ssh_connect()
        sftp_object = sftp.ssh_sftp(ssh_object)
        sftp.get_file_from_qnx_to_local(orign_path, later_path)
        ssh.excute_command("%s" % (command), 20)

    def ssh_close(self):
        ssh.close()

    def sftp_close(self):
        sftp.sftp_close()

    
    def create_screen_file_name(self,module_name):
        current_path = os.getcwd()
        date_time = time.strftime('%Y-%m-%d_%H_%M_%S',time.localtime(time.time()))
        date = time.strftime('%Y-%m-%d',time.localtime(time.time()))
        times = time.strftime('%H_%M_%S', time.localtime(time.time()))
        screen_path = os.getcwd() + "\..\Picture\Actual_Result\\" + "{0}\\".format(date) + "{0}_{1}\\".format(module_name,times)
        # print(screen_path)
        if not os.path.exists('%s' % (screen_path)):
            os.makedirs('%s' % (screen_path))
        return screen_path

    def exist_expect_screen_file_name(self,module_name):
        current_path = os.getcwd()
        # date_time = time.strftime('%Y-%m-%d_%H_%M_%S', time.localtime(time.time()))
        # date = time.strftime('%Y-%m-%d', time.localtime(time.time()))
        # times = time.strftime('%H_%M_%S', time.localtime(time.time()))
        expect_file = os.getcwd() + "\..\Picture\Expect_Result\\" + "{0}.png".format(
            module_name)
        # if not os.path.exists('%s' % (screen_path)):
        #     os.makedirs('%s' % (screen_path))
        return expect_file

    def modify_expect_picture(self,module_name):
        '''
        function: modify expect picture
        :param module_name:
        :return:
        '''
        CPP.modify_expect_picture(self.exist_expect_screen_file_name(module_name))

    def start_collect_log(self,command=[]):
        try:
            logger.log_info("root read and write", \
                            sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name,
                            sys._getframe().f_lineno)
            self.excute_qnx_command(port, password="", username=username,
                                    ip_address=package.update_fota_package()[1],
                                    command=command)
            time.sleep(random.randint(1,3))

        except Exception as e:
            print("%s " %(e))

    def end_collect_log(self):
        logger.log_info("end collect icu log", \
                        sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name,
                        sys._getframe().f_lineno)
        self.excute_qnx_command(port, password="", username=username,
                                ip_address=package.update_fota_package()[1],
                                command=kill_icu_progress)
        time.sleep(random.randint(1, 3))

        logger.log_info("end collect mcu log", \
                        sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name,
                        sys._getframe().f_lineno)
        self.excute_qnx_command(port, password="", username=username,
                                ip_address=package.update_fota_package()[1],
                                command=kill_mcu_progress)
        time.sleep(random.randint(1, 3))

    def copy_log_to_local(self,local_screen_path):
        logger.log_info("copy icu file to local",\
                        sys._getframe().f_code.co_filename,sys._getframe().f_code.co_name,sys._getframe().f_lineno)
        self.copy_logfile_to_local(port, password="", username=username,
                                        ip_address=package.update_fota_package()[1],
                                        command=delete_icu_logfile,orign_path=icu_logfile,
                                        later_path=local_screen_path + "icu_server.log")
        logger.log_info("copy mcu file to local",\
                        sys._getframe().f_code.co_filename,sys._getframe().f_code.co_name,sys._getframe().f_lineno)
        self.copy_logfile_to_local(port, password="", username=username,
                                   ip_address=package.update_fota_package()[1],
                                   command=delete_mcu_logfile, orign_path=mcu_logfile,
                                   later_path=local_screen_path + "mcu_server.log")

    def delete_logfile(self):
        logger.log_info("delete icu log", \
                        sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name,
                        sys._getframe().f_lineno)
        self.excute_qnx_command(port, password="", username=username,
                                ip_address=package.update_fota_package()[1],
                                command=delete_icu_logfile)
        time.sleep(random.randint(1, 3))

        logger.log_info("delete mcu log", \
                        sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name,
                        sys._getframe().f_lineno)
        self.excute_qnx_command(port, password="", username=username,
                                ip_address=package.update_fota_package()[1],
                                command=delete_mcu_logfile)
        time.sleep(random.randint(1, 3))

    def test_reboot_self_inspection(self, module_name):
            '''
            function:test activation network and test signal's picture
            :param module_name:
            :return:
            '''
            try:
                logger.log_debug("start reboot self-inspection test", \
                                 sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name,
                                 sys._getframe().f_lineno)
                logger.log_info("configurate ip address for qnx system", \
                                sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name,
                                sys._getframe().f_lineno)

                # logger.log_info("activation network", \
                #                 sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name,
                #                 sys._getframe().f_lineno)
                logger.log_info("send power off signal", \
                                sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name,
                                sys._getframe().f_lineno)
                self.send_signal_to_qnx(SL.Poweroff)
                time.sleep(random.randint(3, 5))
                # logger.log_info("send activation network signal", \
                #                 sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name,
                #                 sys._getframe().f_lineno)
                # self.send_signal_to_qnx(SL.Active_Network)
                # time.sleep(random.randint(3, 5))

                logger.log_debug("set ip address for ping_object", \
                                 sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name,
                                 sys._getframe().f_lineno)
                ping_object.set_ip_address(package.update_fota_package()[1])

                if ping_object.ping_qnx_system() == 0:
                    logger.log_info("send pcan signal to qnx system", \
                                    sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name,
                                    sys._getframe().f_lineno)
                    child_multi = multiprocessing.Process(target=self.send_signal_to_qnx_system, name="send_qnx_thread",
                                                          args=(SL.REBOOT_SELF_INSPECTION,))
                    child_multi.start()
                    time.sleep(random.randint(40, 50))
                    logger.log_info("screen picture and copy to local", \
                                    sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name,
                                    sys._getframe().f_lineno)
                    local_screen_path = self.create_screen_file_name(module_name)
                    # print(local_screen_path)
                    orign_compare_picture = self.exist_expect_screen_file_name(module_name)
                    # print(orign_compare_picture)
                    for i in range(10):
                        date_time = time.strftime('%Y-%m-%d_%H_%M_%S', time.localtime(time.time()))
                        # self.excute_qnx_command(port, password="", username=username,
                        #                         ip_address=package.update_fota_package()[1],
                        #                         command=create_screen_directory)

                        self.excute_qnx_command(port, password="", username=username,
                                                ip_address=package.update_fota_package()[1],
                                                command=screen_command + save_picture_directory + date_time + ".png")
                        self.screen_shot_and_transfer_to_local(port, password="", username=username,
                                                               ip_address=package.update_fota_package()[1],
                                                               command=screen_command, command1=deltet_screen_picture,
                                                               orign_path=save_picture_directory + date_time + ".png",
                                                               later_path=local_screen_path + date_time + ".png")
                        # print("antony@@@debug")
                        CPP.modify_reboot_self_inspection_picture(orign_compare_picture)
                        CPP.modify_reboot_self_inspection_picture(local_screen_path + date_time + ".png")
                        if CPP.compare_picture(orign_compare_picture, local_screen_path + date_time + ".png", local_screen_path) == 0:
                            logger.log_info("compare picture successfully", \
                                            sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name,
                                            sys._getframe().f_lineno)
                            child_multi.join()
                            self.ssh_close()
                            self.sftp_close()
                            return 0
                        logger.log_error("atnony@@@@debug%s" %(i), \
                                         sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name,
                                         sys._getframe().f_lineno)
                        time.sleep(random.randint(1,3))
                    child_multi.join()
                    self.ssh_close()
                    self.sftp_close()
                    return 1
            except Exception as e:
                logger.log_error("%s" % (e), \
                                 sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name,
                                 sys._getframe().f_lineno)
                return 1

    def test_no_speed_model(self, module_name):
        try:
            logger.log_debug("start no speed model test",\
                            sys._getframe().f_code.co_filename,sys._getframe().f_code.co_name,sys._getframe().f_lineno)

            # init_qnx_system = init_environment(package.update_fota_package()[1], package.update_fota_package()[4])
            # init_qnx_system()
            logger.log_info("activation network",\
                            sys._getframe().f_code.co_filename,sys._getframe().f_code.co_name,sys._getframe().f_lineno)
            sc=SC.PCAN()
            sc = self.send_signal_to_qnx(SL.REBOOT_SELF_INSPECTION)
            time.sleep(random.randint(3,5))
            
            logger.log_debug("set ip address for ping_object",\
                             sys._getframe().f_code.co_filename,sys._getframe().f_code.co_name,sys._getframe().f_lineno)
            ping_object.set_ip_address(package.update_fota_package()[1])
            
            if ping_object.ping_qnx_system() == 0:
                logger.log_info("send pcan signal to qnx system",\
                                sys._getframe().f_code.co_filename,sys._getframe().f_code.co_name,sys._getframe().f_lineno)
                child_multi = multiprocessing.Process(target=self.send_signal_to_qnx_system, name="send_qnx_thread",
                                                      args=(SL.NO_SPEED_ICU_SELF_INSPECTION,))
                child_multi.start()
                time.sleep(random.randint(40, 50))
                logger.log_info("screen picture and copy to local", \
                                sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name,
                                sys._getframe().f_lineno)
                local_screen_path = self.create_screen_file_name(module_name)
                # print(local_screen_path)
                orign_compare_picture = self.exist_expect_screen_file_name(module_name)
                # print(orign_compare_picture)
                for i in range(10):
                    date_time = time.strftime('%Y-%m-%d_%H_%M_%S', time.localtime(time.time()))
                    self.excute_qnx_command(port, password="", username=username,
                                            ip_address=package.update_fota_package()[1],
                                            command=create_screen_directory)
                    time.sleep(random.randint(1,3))
                    self.excute_qnx_command(port, password="", username=username,
                                            ip_address=package.update_fota_package()[1],
                                            command=screen_command + save_picture_directory + date_time + ".png")
                    time.sleep(random.randint(1,3))
                    self.screen_shot_and_transfer_to_local(port, password="", username=username,
                                                           ip_address=package.update_fota_package()[1],
                                                           command=screen_command, command1=deltet_screen_picture,
                                                           orign_path=save_picture_directory + date_time + ".png",
                                                           later_path=local_screen_path + date_time + ".png")
                    time.sleep(random.randint(1,3))
                    CPP.modify_no_sepeed_expect_picture(orign_compare_picture)
                    CPP.modify_no_sepeed_expect_picture(local_screen_path + date_time + ".png")
                    if CPP.compare_picture(orign_compare_picture, local_screen_path + date_time + ".png",
                                           local_screen_path) == 0:
                        logger.log_info("compare picture successfully", \
                                        sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name,
                                        sys._getframe().f_lineno)
                        child_multi.join()
                        self.ssh_close()
                        self.sftp_close()
                        return 0
                    time.sleep(random.randint(2, 5))
                child_multi.join()
                self.ssh_close()
                self.sftp_close()
                return 1
        except Exception as e:
            logger.log_error("%s" % (e), \
                             sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name,
                             sys._getframe().f_lineno)
            return 1

    def test_driver_model_ssh(self,module_name):
        try:

            logger.log_debug("start driver model test", \
                             sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name,
                             sys._getframe().f_lineno)
            time.sleep(random.randint(3, 5))
            logger.log_info("start send two groups signal", \
                            sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name,
                            sys._getframe().f_lineno)
            sc = SC.PCAN()
            sc.send_signal_to_qnx(200, SL.REBOOT_SELF_INSPECTION)

            logger.log_debug("set ip address for ping_object", \
                             sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name,
                             sys._getframe().f_lineno)
            ping_object.set_ip_address(package.update_fota_package()[1])
            if ping_object.ping_qnx_system() == 0:
                time.sleep(random.randint(1,3))
                self.start_collect_log(command=[root_read_write,collect_icu_log])
                self.start_collect_log(command=[root_read_write,collect_mcu_log])
                logger.log_info("send many groups signal to qnx system", \
                                sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name,sys._getframe().f_lineno)
                child_thread = threading.Thread(target=sc.send_signal_to_qnx, name="send_qnx_thread",
                                                    args=(2500,SL.DRIVE_MODEL_ICU_SELF_INSPECTION,))
                child_thread.start()
                time.sleep(random.randint(40, 50))
                logger.log_info("get expect picture directory", \
                                sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name,
                                sys._getframe().f_lineno)
                local_screen_path = self.create_screen_file_name(module_name)
                orign_compare_picture = self.exist_expect_screen_file_name(module_name)
                for i in range(10):
                    date_time = time.strftime('%Y-%m-%d_%H_%M_%S', time.localtime(time.time()))

                    self.screen_shot_and_transfer_to_local(port, password="", username=username,
                                                           ip_address=package.update_fota_package()[1],
                                                           command=screen_command, command1=delete_screen_picture,
                                                           orign_path=udisk_path + date_time + ".png",
                                                           later_path=local_screen_path + date_time + ".png")
                    time.sleep(random.randint(1,3))

                    CPP.modify_driver_expect_picture(orign_compare_picture)
                    CPP.modify_driver_expect_picture(local_screen_path + date_time + ".png")
                    if CPP.compare_picture(orign_compare_picture, local_screen_path + date_time + ".png",
                                           local_screen_path) == 0:
                        logger.log_info("compare picture successfully", \
                                        sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name,
                                        sys._getframe().f_lineno)
                        child_thread.join()
                        time.sleep(random.randint(3,5))
                        sc.clean()
                        self.end_collect_log()
                        self.copy_log_to_local(local_screen_path)
                        self.delete_logfile()
                        self.ssh_close()
                        self.sftp_close()
                        return 0
                child_thread.join()
                time.sleep(random.randint(3,5))
                sc.clean()
                self.end_collect_log()
                self.copy_log_to_local(local_screen_path)
                self.delete_logfile()
                self.ssh_close()
                self.sftp_close()
                return 1
            else:
                sc.clean()
                logger.log_error("can not ping network", \
                                 sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name,
                                 sys._getframe().f_lineno
                                 )
                return 1
        except Exception as e:

            # self.copy_log_to_local(local_screen_path)
            try:
                self.end_collect_log()
                logger.log_info("antony@@@debug", \
                                sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name,
                                sys._getframe().f_lineno)
                child_thread.join()
            except Exception as e:
                logger.log_error("%s" % (e), \
                                 sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name,
                                 sys._getframe().f_lineno)
                sc.clean()
                return 1
            sc.clean()
            logger.log_error("%s" % (e), \
                             sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name,
                             sys._getframe().f_lineno)
            return 1

    def test_driver_model_adb(self, module_name, sn):
        try:

            logger.log_debug("start driver model test", \
                             sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name,
                             sys._getframe().f_lineno)
            time.sleep(random.randint(3, 5))
            logger.log_info("start send two groups signal", \
                            sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name,
                            sys._getframe().f_lineno)
            # sc = SC.PCAN()
            # sc.send_signal_to_qnx(200, SL.REBOOT_SELF_INSPECTION)

            logger.log_debug("start collect icu log",\
                             sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name,sys._getframe().f_lineno)
            execute_adb_command.execute_command_to_qnx_system(sn,telnet,collect_icu_log)

            # logger.log_debug("start collect mcu log",\
            #                  sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name,sys._getframe().f_lineno)
            # execute_adb_command.execute_command_to_qnx_system(sn, telnet, collect_mcu_log)
            #
            # logger.log_info("send many groups signal to qnx system", \
            #                 sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name,
            #                 sys._getframe().f_lineno)
            # child_thread = threading.Thread(target=sc.send_signal_to_qnx, name="send_qnx_thread",
            #                                 args=(2500, SL.DRIVE_MODEL_ICU_SELF_INSPECTION,))
            # child_thread.start()
            # time.sleep(random.randint(40, 50))
            #
            # logger.log_info("get expect picture directory", \
            #                 sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name,
            #                 sys._getframe().f_lineno)
            # local_screen_path = self.create_screen_file_name(module_name)
            # print(local_screen_path)
            # orign_compare_picture = self.exist_expect_screen_file_name(module_name)
            # os.system('adb -s %s shell "%s"' % (sn, adb_mount))
            # for i in range(10):
            #     date_time = time.strftime('%Y-%m-%d_%H_%M_%S', time.localtime(time.time()))
            #     picture_full_path = save_picture_directory + date_time + ".png"
            #     android_full_path = "/" + date_time + ".png"
            #     local_picture_location = local_screen_path + date_time + ".png"
            #
            #     save_picture_and_delete(sn, picture_full_path, android_full_path, local_picture_location)
            #
            #     time.sleep(random.randint(1, 3))
            #     CPP.modify_driver_expect_picture(orign_compare_picture)
            #     CPP.modify_driver_expect_picture(local_picture_location)
            #     if CPP.compare_picture(orign_compare_picture, local_picture_location,
            #                            local_screen_path) == 0:
            #         logger.log_info("compare picture successfully", \
            #                         sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name,
            #                         sys._getframe().f_lineno)
            #         child_thread.join()
            #         time.sleep(random.randint(3, 5))
            #         sc.clean()
            #         log_kill_copy_local(sn,local_screen_path)
            #         return 0
            # child_thread.join()
            # time.sleep(random.randint(3, 5))
            # sc.clean()
            # rm_icu_and_mcu_log(sn)
            # return 1
        except Exception as e:
            pass
            # try:
            #     rm_icu_and_mcu_log(sn)
            #     logger.log_info("antony@@@debug", \
            #                     sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name,
            #                     sys._getframe().f_lineno)
            #     child_thread.join()
            # except Exception as e:
            #     logger.log_error("%s" % (e), \
            #                      sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name,
            #                      sys._getframe().f_lineno)
            #     sc.clean()
            #     return 1
            # sc.clean()
            # logger.log_error("%s" % (e), \
            #                  sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name,
            #                  sys._getframe().f_lineno)
            # return 1






