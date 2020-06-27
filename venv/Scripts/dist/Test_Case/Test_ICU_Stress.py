'''
icu stress case
author :antony weijiang
date:2020/4/23
'''
import pytest
import sys
import os
import time
import random
import pytest_html.extras
import pytest_html.hooks
import pytest_html.plugin
from log import logger as loger
from Test_Case_ICU_Stress import  Test_Reboot_Self_Inspection as TRSI
from Test_Case_ICU_Stress import  Test_No_Speed_Model as TNSM
from Test_Case_ICU_Stress import Test_Driver_Model as TDM
logger = loger.Current_Module()


class Test_ICU_STRESS():
    @pytest.fixture(scope='function',autouse= True)
    def message(self):
        '''check test environment'''
        logger.log_info("start Test",sys._getframe().f_code.co_filename,sys._getframe().f_code.co_name,sys._getframe().f_lineno)
        yield
        logger.log_info("end Test",sys._getframe().f_code.co_filename,sys._getframe().f_code.co_name,sys._getframe().f_lineno)


    def test_driver_model(self):
        if TDM.test() == 0:
            assert True
        else:
            assert False



