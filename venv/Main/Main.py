'''
progress main
author: antony weijiang
date: 2019/11/27
'''
import time
import os
import argparse
import pytest
from pytest_html import plugin
from pytest_html import hooks
from pytest_html import extras
import paramiko
import os
import time
from Common import Common as co
from Common import ICU_Common as icuc
from Test_Case_ICU_Stress import  Test_Reboot_Self_Inspection as TRSI
from Test_Case_ICU_Stress import  Test_No_Speed_Model as TNSM
from Test_Case_ICU_Stress import Test_Driver_Model as TDM

def init_ssh_and_setipaddress():
    package = co.Install_Package()
    init_qnx_system = icuc.init_environment(package.update_fota_package()[1], package.update_fota_package()[4])
    init_qnx_system()

if __name__ == "__main__":
    # init_ssh_and_setipaddress()
    parser = argparse.ArgumentParser(prog='PROG', usage='%(prog)s [options]')
    parser.add_argument('--account', dest="account", metavar='account', help="choose capture picture")
    parser.add_argument('--time', dest='time', metavar='run times', help='how long time cases need to run(hours)')
    arg = parser.parse_args(['--account', '1'])
    # arg = parser.parse_args(['--account', '200'])
    # arg = parser.parse_args(['--time','60'])
    # arg = parser.parse_args()
    if arg.time is not None:
        current_time = int(time.time())
        loop_time = current_time + int(arg.time) * 3600
        time.sleep(1)
        while current_time <= loop_time:
            pytest.main(['-s','--metadata','Tester','Antony WeiJiang','--metadata','Project','ICU STRESS',
                    '--metadata','Company','WM MOTOR','%s' %(os.getcwd() + "\..\Test_Case"),'--html','Report_%s.html' %(current_time),'--self-contained-html'])
            current_time = int(time.time())

    if arg.account is not None:
        account = int(arg.account)
        current_time = int(time.time())
        list_str = ['-s','--metadata','Tester','Antony WeiJiang','--metadata','Project','ICU STRESS',
                    '--metadata','Company','WM MOTOR','--repeat-scope','class','--count','%s' %(arg.account),
                     '%s' %(os.getcwd() + "\..\Test_Case"),'--html','Report_Icu_Stress_%s.html' %(current_time),'--self-contained-html']
        # print(list_str)
        pytest.main(list_str)


