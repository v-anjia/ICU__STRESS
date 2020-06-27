'''
function:  self-inspection then check picture content
author antony weijiang
date 2019/12/13
'''
import time
import os
import sys
from Common import ICU_Common as ICUC
from log import logger as loger
logger = loger.Current_Module()
icu_common = ICUC.ICU_Common()
def test():
    try:
        icu_common.test_reboot_self_inspection(os.path.basename(__file__).split(".")[0])
        
        return 0
    except Exception as e:
        logger.log_error("%s" %(e),\
                         sys._getframe().f_code.co_filename,sys._getframe().f_code.co_name,sys._getframe().f_lineno)
        return 1
