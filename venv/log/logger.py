'''
deposit public class or function
data:2019-3-28
@author antony weijiang
'''
import logging
import logging.config
import os
import ctypes
import colorlog
import time

LOG_FORMAT_CONSOLE = "%(log_color)s%(asctime)s [%(levelname)-5.5s] %(message)s"
LOG_FORMAT_FILE = "%(asctime)s [%(levelname)-5.5s] %(message)s"
DATE_FORMAT = '%a,%d %b %Y %H:%M:%S'
formatter_console = colorlog.ColoredFormatter(
	LOG_FORMAT_CONSOLE,
	DATE_FORMAT,
	reset=True,
	log_colors={
		'DEBUG':    'cyan',
		'INFO':     'green',
		'WARNING':  'bold_yellow',
		'ERROR':    'bold_red',
		'CRITICAL': 'bold_red,bg_white',
	},
	secondary_log_colors={},
	style='%'
)
case_name_directory = ""
formatter_file = logging.Formatter(LOG_FORMAT_FILE, DATE_FORMAT)

file_dir = time.strftime('%Y-%m-%d',time.localtime(time.time()))
if not os.path.exists('..\Result\%s' %(file_dir)):
    os.makedirs('..\Result\%s' %(file_dir))

class Current_Module(object):
    def __init__(self):
        self.current_name = ""

    def set_current_name(self, current_name):
        self.current_name = current_name

    def get_current_name(self):
        return self.current_name

    def get_logg_info(self):
        if case_name_directory != "" and not os.path.exists('..\Result\%s\%s' %(file_dir,case_name_directory)):
            os.makedirs('..\Result\%s\%s' % (file_dir, case_name_directory))
        return '..\Result\%s\%s\Info.log' % (file_dir, case_name_directory)

    def get_logg_debug(self):
        if case_name_directory != "" and not os.path.exists('..\Result\%s\%s' %(file_dir,case_name_directory)):
            os.makedirs('..\Result\%s\%s' % (file_dir, case_name_directory))
        return '..\Result\%s\%s\Debug.log' %(file_dir,case_name_directory)

    def get_logg_error(self):
        if case_name_directory != "" and not os.path.exists('..\Result\%s\%s' %(file_dir,case_name_directory)):
            os.makedirs('..\Result\%s\%s' % (file_dir, case_name_directory))
        return '..\Result\%s\%s\Error.log' %(file_dir,case_name_directory)

    def get_logg_warn(self):
        if case_name_directory != "" and not os.path.exists('..\Result\%s\%s' %(file_dir,case_name_directory)):
            os.makedirs('..\Result\%s\%s' % (file_dir, case_name_directory))
        return '..\Result\%s\%s\Warn.log' %(file_dir,case_name_directory)

    def get_logg_critical(self):
        if case_name_directory != "" and not os.path.exists('..\Result\%s\%s' %(file_dir,case_name_directory)):
            os.makedirs('..\Result\%s\%s' % (file_dir, case_name_directory))
        return '..\Result\%s\%s\Critical.log' %(file_dir,case_name_directory)

    def get_logg_result(self):
        if case_name_directory != "" and not os.path.exists('..\Result\%s\%s' %(file_dir,case_name_directory)):
            os.makedirs('..\Result\%s\%s' % (file_dir, case_name_directory))
        return '..\Result\%s\%s\Result.log' %(file_dir,case_name_directory)

    def log_info(self, msg, filename=None, funname=None, line=None):
        '''
        function: print info message
        :param msg:
        :param filename:
        :param funname:
        :param line:
        :return:
        '''
        logger = logging.getLogger()
        logger.setLevel('INFO')
        shr = logging.StreamHandler()
        shr.setFormatter(formatter_console)
        shr.setLevel('INFO')
        fhr = logging.FileHandler('%s' % (self.get_logg_info()), 'a')
        fhr1 = logging.FileHandler('%s' % (self.get_logg_result()), 'a')
        fhr.setFormatter(formatter_file)
        fhr1.setFormatter(formatter_file)
        fhr.setLevel('INFO')
        fhr1.setLevel('INFO')
        logger.addHandler(shr)
        logger.addHandler(fhr)
        logger.addHandler(fhr1)
        logger.info("File:%s Function:%s Line:%s\n=====> %s" % (filename, funname, line, msg))
        logger.removeHandler(shr)
        logger.removeHandler(fhr)
        logger.removeHandler(fhr1)

    def log_debug(self, msg, filename=None, funname=None, line=None):
        '''
        funciton :print debug message
        :param msg:
        :param filename:
        :param funname:
        :param line:
        :return:
        '''
        logger = logging.getLogger()
        logger.setLevel('DEBUG')
        shr = logging.StreamHandler()
        shr.setFormatter(formatter_console)
        shr.setLevel('DEBUG')
        fhr = logging.FileHandler('%s' % (self.get_logg_debug()), 'a')
        fhr1 = logging.FileHandler('%s' % (self.get_logg_result()), 'a')
        fhr.setFormatter(formatter_file)
        fhr1.setFormatter(formatter_file)
        fhr.setLevel('DEBUG')
        fhr1.setLevel('DEBUG')
        logger.addHandler(shr)
        logger.addHandler(fhr)
        logger.addHandler(fhr1)
        logger.debug("File:%s Function:%s Line:%s\n=====> %s" % (filename, funname, line, msg))
        logger.removeHandler(shr)
        logger.removeHandler(fhr)
        logger.removeHandler(fhr1)

    def log_warn(self, msg, filename=None, funname=None, line=None):
        '''
        function:print warn message
        :param msg:
        :param filename:
        :param funname:
        :param line:
        :return:
        '''
        logger = logging.getLogger()
        logger.setLevel('WARN')
        shr = logging.StreamHandler()
        shr.setFormatter(formatter_console)
        shr.setLevel('WARN')
        fhr = logging.FileHandler('%s' % (self.get_logg_warn()), 'a')
        fhr1 = logging.FileHandler('%s' % (self.get_logg_result()), 'a')
        fhr.setFormatter(formatter_file)
        fhr1.setFormatter(formatter_file)
        fhr.setLevel('WARN')
        fhr1.setLevel('WARN')
        logger.addHandler(shr)
        logger.addHandler(fhr)
        logger.addHandler(fhr1)
        logger.warn("File:%s Function:%s Line:%s\n=====> %s" % (filename, funname, line, msg))
        logger.removeHandler(shr)
        logger.removeHandler(fhr)
        logger.removeHandler(fhr1)

    def log_error(self, msg, filename=None, funname=None, line=None):
        '''
        function:print error message
        :param msg:
        :param filename:
        :param funname:
        :param line:
        :return:
        '''
        logger = logging.getLogger()
        logger.setLevel('ERROR')
        shr = logging.StreamHandler()
        shr.setFormatter(formatter_console)
        shr.setLevel('ERROR')
        fhr = logging.FileHandler('%s' % (self.get_logg_error()), 'a')
        fhr1 = logging.FileHandler('%s' % (self.get_logg_result()), 'a')
        fhr.setFormatter(formatter_file)
        fhr1.setFormatter(formatter_file)
        fhr.setLevel('ERROR')
        fhr1.setLevel('ERROR')
        logger.addHandler(shr)
        logger.addHandler(fhr)
        logger.addHandler(fhr1)
        logger.error("File:%s Function:%s Line:%s\n=====> %s" % (filename, funname, line, msg))
        logger.removeHandler(shr)
        logger.removeHandler(fhr)
        logger.removeHandler(fhr1)

    def log_critical(self, msg, filename=None, funname=None, line=None):
        '''
        function:print critical message
        :param msg:
        :param filename:
        :param funname:
        :param line:
        :return:
        '''
        logger = logging.getLogger()
        logger.setLevel('CRITICAL')
        shr = logging.StreamHandler()
        shr.setFormatter(formatter_console)
        shr.setLevel('CRITICAL')
        fhr = logging.FileHandler('%s' % (self.get_logg_critical()), 'a')
        fhr1 = logging.FileHandler('%s' % (self.get_logg_result()), 'a')
        fhr.setFormatter(formatter_file)
        fhr1.setFormatter(formatter_file)
        fhr.setLevel('CRITICAL')
        fhr1.setLevel('CRITICAL')
        logger.addHandler(shr)
        logger.addHandler(fhr)
        logger.addHandler(fhr1)
        logger.critical("File:%s Function:%s Line:%s\n=====> %s" % (filename, funname, line, msg))
        logger.removeHandler(shr)
        logger.removeHandler(fhr)
        logger.removeHandler(fhr1)

    def Total_Result(self, total, passrate, failrate, module_name):
        '''
        function :generate total result
        :param total:
        :param passrate:
        :param failrate:
        :param module_name:
        :return:
        '''
        str_msg = '''
        -----------------------------------------------------------------------------------------------------
                    Total\t\t\tPASS\t\t\tFail
                    %s\t\t\t\t%s\t\t\t\t%s
        TestCase:%s\t\t   passrate:%s\t\t  failrate:%s
        -----------------------------------------------------------------------------------------------------
        ''' % (total, passrate, failrate, module_name, float(passrate) / total, float(failrate) / total)
        print(str_msg)
        current_date = time.strftime('%Y-%m-%d__%H-%M-%S', time.localtime(time.time()))
        # current_date = time.strftime('%Y-%m-%d__%H-%M-%S', time.localtime(time.time()))
        # result_file = "..\Result\%s_%s.log" %(current_date,module_name)
        result_file1 = "..\Result\%s\Total_%s_%s.log" % (file_dir, current_date, module_name)
        # with open('%s' %(result_file), 'w') as f:
        #     f.write(str_msg)
        with open('%s' % (result_file1), 'w') as f:
            f.write(str_msg)

    def Current_Result(self, total, passrate, failrate, module_name):
        '''
        function :generate total result
        :param total:
        :param passrate:
        :param failrate:
        :param module_name:
        :return:
        '''
        str_msg = '''
        -----------------------------------------------------------------------------------------------------
                    Total\t\t\tPASS\t\t\tFail
                    %s\t\t\t\t%s\t\t\t\t%s
        TestCase:%s\t\t   passrate:%s\t\t  failrate:%s
        -----------------------------------------------------------------------------------------------------
        ''' % (total, passrate, failrate, module_name, float(passrate) / total, float(failrate) / total)
        print(str_msg)
        current_date = time.strftime('%Y-%m-%d__%H-%M-%S',time.localtime(time.time()))
        # current_date = time.strftime('%Y-%m-%d', time.localtime(time.time()))
        # result_file = "..\Result\%s_%s.log" %(current_date,module_name)
        result_file1 = "..\Result\%s\Current_%s_%s.log" % (file_dir, current_date, module_name)
        # with open('%s' %(result_file), 'w') as f:
        #     f.write(str_msg)
        with open('%s' % (result_file1), 'w') as f:
            f.write(str_msg)








