import paramiko
import os
import time
import serial
import sys

from log import logger as loger
logger = loger.Current_Module()

class SSH_Client(object):
    def __init__(self):
        self.ip_address = None
        self.username = None
        self.password = ""
        self.port = None
        self.banner_timeout = 300
        self.ssh = paramiko.SSHClient()

    def set_ip_address(self, ip_address):
        self.ip_address = ip_address

    def get_ip_address(self):
        return self.ip_address

    def set_username(self, username):
        self.username = username

    def get_username(self):
        return  self.username

    def set_password(self, password):
        self.password = password

    def get_password(self):
        return self.password

    def set_port(self, port):
        self.port = port

    def get_port(self):
        return self.port

    def set_banner_timeout(self, banner_timeout):
        self.banner_timeout = banner_timeout

    def get_banner_timeout(self):
        return self.banner_timeout


    def ssh_connect(self):
        '''
        funciton：ssh connect
        :param ip_address:
        :param username:
        :param password:
        :return:
        '''
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh.connect(hostname=self.get_ip_address(), port=self.get_port(), username=self.get_username(), password=self.get_password(), banner_timeout=self.get_banner_timeout())
        return self.ssh


    def excute_command(self, ssh_command, timeout):
        (stdin, stdout, stderr)= self.ssh.exec_command(ssh_command, timeout=timeout)
        logger.log_debug("excute command output is :%s" %(stdout.read().decode('utf-8')),\
                         sys._getframe().f_code.co_filename,sys._getframe().f_code.co_name,sys._getframe().f_lineno)
        # print(stdout.read().decode('utf-8'))
    
    def close(self):
        self.ssh.close()


    def __call__(self, *args, **kwargs):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass



class SFTP_Client(SSH_Client):
    def __init__(self):
        self.username = None
        self.password = None
        self.port = None
        self.ip_address = None
        self.sftp = None
        super(SFTP_Client,self).__init__()

    def set_sftp(self,sftp):
        self.sftp = sftp

    def get_sftp(self):
        return self.sftp

    def ssh_sftp(self,ssh_object):
        '''
        function: get sftp object
        :param ssh_object:
        :return:
        '''
        self.sftp = paramiko.SFTPClient.from_transport(ssh_object.get_transport())
        return self.sftp
    
    def sftp_close(self):
        self.sftp.close()
        
    def get_file_from_qnx_to_local(self, remote_path, local_path):
        '''
        function:copy file from qnx to local
        :param local_path:
        :param remote_path:
        :param sftp_object:
        :return:
        '''
        self.sftp.get(remote_path, local_path)


    def put_file_from_local_to_qnx(self, local_path, remote_path, ):
        '''
        function:copy file from local to qnx
        :param local_path:
        :param remote_path:
        :param sftp_object:
        :return:
        '''
        self.sftp.put(local_path, remote_path)

    def __call__(self, *args, **kwargs):
        pass

class Ping_Object(SSH_Client):
    def __init__(self):
        super(Ping_Object,self).__init__()


    def ping_qnx_system(self):
        # print(self.get_ip_address())
        if os.system('ping -n 3 %s >nul' % (self.get_ip_address())) == 0:
            logger.log_info("qnx system works well",\
                            sys._getframe().f_code.co_filename,sys._getframe().f_code.co_name,sys._getframe().f_lineno)
            return 0
        else:
            logger.log_error("qnx system init failed",\
                             sys._getframe().f_code.co_filename,sys._getframe().f_code.co_name,sys._getframe().f_lineno)
            return 1
