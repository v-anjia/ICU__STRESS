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


def test():
    try:
        return icu_common.test_driver_model(os.path.basename(__file__).split(".")[0])

    except Exception as e:
        logger.log_error("%s" % (e), \
                         sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name, sys._getframe().f_lineno)
        return 1
