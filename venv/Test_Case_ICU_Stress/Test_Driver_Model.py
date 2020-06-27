'''
function:  Drive Mode then check picture content
author antony weijiang
date 2019/4/23
'''
import time
import os
import sys
from Common import ICU_Common as ICUC
from log import logger as loger

logger = loger.Current_Module()
icu_common = ICUC.ICU_Common()


def test(sn):
    try:
        if sn is not None:
            return icu_common.test_driver_model_adb(os.path.basename(__file__).split(".")[0],sn)
        else:
            return icu_common.test_driver_model_ssh(os.path.basename(__file__).split(".")[0])

    except Exception as e:
        logger.log_error("%s" % (e), \
                         sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name, sys._getframe().f_lineno)
        return 1
