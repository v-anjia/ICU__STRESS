'''
deposit public class or function
data:2019-6-3
@author: antony weijiang
'''
import can
import time
import sys
from Common import Signal_List as SL
from can.bus import BusABC
from can.message import  Message
from log import logger as loger

logger = loger.Current_Module()

class PCAN(object):
    def __enter__(self):
        return self

    def __init__(self):
        self.bus = can.interface.Bus(bustype='pcan', channel='PCAN_USBBUS1', bitrate=500000)

    def recived(self):
        self.bus.recv()

    # def get_bus(self):
    #     return self.bus

    def send(self,id , data):
        id = int(id,16)
        msg = can.Message(arbitration_id=id, dlc=8, data=data, extended_id=False)
        try:
            self.bus.send(msg)
        except can.CanError:
            logger.log_error("Message NOT sent", \
                                  sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name,
                                  sys._getframe().f_lineno)

    def send_arry(self, arry_list = []):
        for i in arry_list:
            self.send(i['id'], i['data'])
        
    def clean(self):
        self.bus.shutdown()

    def send_signal_to_qnx(self, times, ARRY_LIST=[]):
        for i in range(times):
            self.send_arry(ARRY_LIST)
            time.sleep(0.1)

    def __exit__(self, exc_type, exc_val, exc_tb):
        for i in range(10):
            self.send(SL.PowerOn[0]['id'],SL.PowerOn[0]['data'])
            time.sleep(0.1)
        self.bus.shutdown()



    

