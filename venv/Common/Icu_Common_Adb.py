from Common import Common as co
from log import logger as loger
import subprocess
import os
import time
import sys

logger = loger.Current_Module()

class excute_adb_command(object):

    def __init__(self):
        pass

    def execute_command_to_qnx_system(self, sn, telnet, command):
        try:
            # cmd = '%s "%s"' %(telnet,command)
            cmd = " %s touch 1234.log" %(telnet)
            print(cmd)
            ret_value = subprocess.check_call('adb -s %s shell %s' %(sn, cmd), shell=True)
            # ret_value = subprocess.check_output('adb -s %s shell  "%s "%s""' %(sn, telnet,command))
            print("antony@@@debug %s" %(ret_value))
            if ret_value == 0:
                logger.log_debug("execute command :%s successfully" %(command),\
                                 sys._getframe().f_code.co_filename,sys._getframe().f_code.co_name,sys._getframe().f_lineno)
                return 0
            else:
                logger.log_error("execute command :%s failed" %(command),\
                                 sys._getframe().f_code.co_filename,sys._getframe().f_code.co_name,sys._getframe().f_lineno)
                return 1
        except Exception as e:
            logger.log_error("%s" %(e),sys._getframe().f_code.co_filename,sys._getframe().f_code.co_name,sys._getframe().f_lineno)
            return 1

    def copy_file_from_qnx_to_android(self, sn, ftpget, qnx_ip, qnx_path, android_path):
        try:
            execute_command = "%s %s %s %s" %(ftpget, qnx_ip, qnx_path, android_path)
            ret_value = subprocess.check_output("adb -s %s shell %s" %(sn, execute_command))
            if ret_value == 0:
                logger.log_debug("execute command : %s successfully" %(execute_command),\
                                 sys._getframe().f_code.co_filename,sys._getframe().f_code.co_name,sys._getframe().f_lineno)
                return 0
            else:
                logger.log_error("execute command : %s failed" %(execute_command),\
                                 sys._getframe().f_code.co_filename,sys._getframe().f_code.co_name,sys._getframe().f_lineno)
                return 1
        except Exception as e:
            logger.log_error("%s" %(e),\
                             sys._getframe().f_code.co_filename,sys._getframe().f_code.co_name,sys._getframe().f_lineno)
            return 1

    def pull_file_to_local(self, sn, sour_path, des_path):
        '''
        function: through adb device to pull file to local
        :param sn:
        :param sour_path:
        :param des_path:
        :return:
        '''
        try:
            ret_value = subprocess.check_output("adb -s %s pull %s %s" %(source_path, des_path))
            if ret_value == 0:
                logger.log_debug("execute command : %s successfully" %(),\
                                 sys._getframe().f_code.co_filename,sys._getframe().f_code.co_name,sys._getframe().f_lineno)
                return 0
            else:
                logger.log_error("execute command : %s failed" %(),\
                                 sys._getframe().f_code.co_filename,sys._getframe().f_code.co_name,sys._getframe().f_lineno)
                return 1
        except Exception as e:
            logger.log_error("%s" %(e),\
                             sys._getframe().f_code.co_filename,sys._getframe().f_code.co_name,sys._getframe().f_lineno)
            return 1






