'''
picture compare
author: antony weijiang
date: 2019/11/27
'''

import numpy as np
import os
import  time
import cv2
import sys
import imutil
from skimage.metrics import structural_similarity
from log import logger as loger
logger = loger.Current_Module()


'''
for compare picture object
'''
class Compare_Picture(object):
    def __init__(self):
        pass

    def __call__(self, *args, **kwargs):
        pass

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def picture_split_colour(self,picture):
        '''
        function:split colour (B,G,R)
        :param picture:
        :return: (b,g,r)
        '''
        picture_objec =  cv2.imread("{0}".format(picture))
        b,g,r =cv2.split(picture_objec)
        return (b,g,r)

    def three_channel_merge(self,b,g,r):

        return cv2.merge([b,g,r])

    def set_barrier(self, wide, high, orign_picture, latest_picture):
        '''
        function : set barrier
        :param wide:
        :param high:
        :param orign_picture:
        :param latest_picture:
        :return:
        '''
        # cv2.imread(orign_picture).shape
        #to be defined
        pass


    def face_compare(self):
        recognizer = cv2.face.LBPHFaceRecognizer_create()
        pass

    def find_diff(self,orign_picture, latest_picture,actual_result_path):
        '''
        function: find picture different
        :param orign_picture:
        :param latest_picture:
        :param actual_result_path:
        :return:
        '''
        orign_picture = cv2.imread(orign_picture)
        latest_picture = cv2.imread(latest_picture)
        gray1 = cv2.cvtColor(orign_picture, cv2.COLOR_BGR2GRAY)
        gray2 = cv2.cvtColor(latest_picture,cv2.COLOR_BGR2GRAY)
        '''
        find two picture is different part
        '''
        (score, diff) = structural_similarity(gray1,gray2,full = True,multichannel = True)
        diff = (diff * 255).astype("uint8")
        '''
        threshold to deal with picture
        '''
        (retval, dst) = cv2.threshold(diff,0,255,cv2.THRESH_BINARY_INV| cv2.THRESH_OTSU)
        '''
        total different part 
        '''
        (cnts, hierarchy) = cv2.findContours(dst.copy(),cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)

        for c in cnts:
            (x,y,w,h) = cv2.boundingRect(c)
            cv2.rectangle(latest_picture,(x,y),(x+w,y+h),(0,0,255),2)
        cv2.imwrite("{0}{1}_different.png".format(actual_result_path, time.strftime('%Y-%m-%d__%H-%M-%S', time.localtime(time.time()))), latest_picture)
        cv2.waitKey()
        cv2.destroyAllWindows()

    def compare_picture(self,orign_picture,latest_picture,actual_result_path):
        '''
        function: compare picture
        :param orign_picture:
        :param latest_picture:
        :param actual_result_path:
        :return:
        '''
        picture1_object = cv2.imread("{0}".format(orign_picture))
        picture2_object = cv2.imread("{0}".format(latest_picture))

        # picture2_object = self.modify_picture_No_Speed(picture2_object)
        # # picture2_object = self.modify_picture(picture2_object)
        # cv2.imwrite("%s" %(latest_picture),picture2_object)

        high = picture1_object.shape[0]
        wide = picture1_object.shape[1]
        count = 0
        for i in range(0,high):
            for j in range(0,wide):
                if picture1_object[i,j,0] == picture2_object[i,j,0] and \
                        picture1_object[i,j,1] == picture2_object[i,j,1] and \
                            picture1_object[i, j, 2] == picture2_object[i, j, 2]:
                    continue
                else:
                    logger.log_error("i :%s ,j : %s" %(i,j),\
                                     sys._getframe().f_code.co_filename,sys._getframe().f_code.co_name,sys._getframe().f_lineno)
                    count = count + 1
                    break
            if count > 0:
                break
        if count == 0:
            logger.log_info("the picture is the same,picture compare successfully",\
                sys._getframe().f_code.co_filename,sys._getframe().f_code.co_name,sys._getframe().f_lineno)
            return 0
        else:
            logger.log_error("the picture is different,picture compare failed",\
                             sys._getframe().f_code.co_filename,sys._getframe().f_code.co_name,sys._getframe().f_lineno)

            self.find_diff(orign_picture,latest_picture,actual_result_path)
            return 1

    def modify_picture_reboot_self_inspection(self, picture_object):
        '''
        modify the picture
        :param picture_object:
        :return:
        '''
        '''去掉底部的公里数和Trip'''
        for i in range(650,700):
            for j in range(100,423):
                picture_object.itemset((i, j, 0), 0)
                picture_object.itemset((i, j, 1), 0)
                picture_object.itemset((i, j, 2), 0)
            for k in range(1740,1900):
                picture_object.itemset((i, k, 0), 0)
                picture_object.itemset((i, k, 1), 0)
                picture_object.itemset((i, k, 2), 0)

        ''' 去掉速度'''
        for i in range (110,260):
            for j in range(0,520):
                picture_object.itemset((i, j, 0), 0)
                picture_object.itemset((i, j, 1), 0)
                picture_object.itemset((i, j, 2), 0)
        ''' 去掉速度'''
        for i in range (260,510):
            for j in range(65,520):
                picture_object.itemset((i, j, 0), 0)
                picture_object.itemset((i, j, 1), 0)
                picture_object.itemset((i, j, 2), 0)
        ''' 去掉速度'''
        for i in range (50,200):
            for j in range(0,145):
                picture_object.itemset((i, j, 0), 0)
                picture_object.itemset((i, j, 1), 0)
                picture_object.itemset((i, j, 2), 0)
        '''去掉左下面的指示灯'''
        for i in range(80,110):
            for j in range(140,350):
                picture_object.itemset((i, j, 0), 0)
                picture_object.itemset((i, j, 1), 0)
                picture_object.itemset((i, j, 2), 0)

        # '''去掉远光灯的动态'''
        # for i in range (300,450):
        #     for j in range(410,630):
        #         picture_object.itemset((i, j, 0), 0)
        #         picture_object.itemset((i, j, 1), 0)
        #         picture_object.itemset((i, j, 2), 0)

        '''去掉安全带指示灯'''
        # for i in range (20,70):
        #     for j in range(555,590):
        #         picture_object.itemset((i, j, 0), 0)
        #         picture_object.itemset((i, j, 1), 0)
        #         picture_object.itemset((i, j, 2), 0)
        '''去掉安全带指示灯'''
        # for i in range(20, 70):
        #     for j in range(1335, 1375):
        #         picture_object.itemset((i, j, 0), 0)
        #         picture_object.itemset((i, j, 1), 0)
        #         picture_object.itemset((i, j, 2), 0)

        return picture_object

    def modify_picture_No_Speed(self, picture_object):
        '''
        modify the picture
        :param picture_object:
        :return:
        '''
        '''去掉底部的公里数和Trip'''
        for i in range(650,700):
            for j in range(100,423):
                picture_object.itemset((i, j, 0), 0)
                picture_object.itemset((i, j, 1), 0)
                picture_object.itemset((i, j, 2), 0)
            for k in range(1740,1900):
                picture_object.itemset((i, k, 0), 0)
                picture_object.itemset((i, k, 1), 0)
                picture_object.itemset((i, k, 2), 0)

        ''' 去掉速度'''
        for i in range (110,260):
            for j in range(0,520):
                picture_object.itemset((i, j, 0), 0)
                picture_object.itemset((i, j, 1), 0)
                picture_object.itemset((i, j, 2), 0)
        ''' 去掉速度'''
        for i in range (260,510):
            for j in range(65,520):
                picture_object.itemset((i, j, 0), 0)
                picture_object.itemset((i, j, 1), 0)
                picture_object.itemset((i, j, 2), 0)
        ''' 去掉速度'''
        for i in range (50,200):
            for j in range(0,145):
                picture_object.itemset((i, j, 0), 0)
                picture_object.itemset((i, j, 1), 0)
                picture_object.itemset((i, j, 2), 0)

        '''去掉远光灯的动态'''
        for i in range (300,450):
            for j in range(410,630):
                picture_object.itemset((i, j, 0), 0)
                picture_object.itemset((i, j, 1), 0)
                picture_object.itemset((i, j, 2), 0)

        '''去掉安全带指示灯'''
        # for i in range (20,70):
        #     for j in range(555,590):
        #         picture_object.itemset((i, j, 0), 0)
        #         picture_object.itemset((i, j, 1), 0)
        #         picture_object.itemset((i, j, 2), 0)
        '''去掉安全带指示灯'''
        # for i in range(20, 70):
        #     for j in range(1335, 1375):
        #         picture_object.itemset((i, j, 0), 0)
        #         picture_object.itemset((i, j, 1), 0)
        #         picture_object.itemset((i, j, 2), 0)

        return picture_object

    def modify_picture_driver(self, picture_object):
        '''
        modify the picture
        :param picture_object:
        :return:
        '''
        '''去掉底部的公里数和Trip'''
        for i in range(650, 700):
            for j in range(100, 423):
                picture_object.itemset((i, j, 0), 0)
                picture_object.itemset((i, j, 1), 0)
                picture_object.itemset((i, j, 2), 0)
            for k in range(1740, 1900):
                picture_object.itemset((i, k, 0), 0)
                picture_object.itemset((i, k, 1), 0)
                picture_object.itemset((i, k, 2), 0)

        ''' 去掉速度'''
        for i in range(110, 260):
            for j in range(0, 520):
                picture_object.itemset((i, j, 0), 0)
                picture_object.itemset((i, j, 1), 0)
                picture_object.itemset((i, j, 2), 0)
        ''' 去掉速度'''
        for i in range(260, 510):
            for j in range(65, 520):
                picture_object.itemset((i, j, 0), 0)
                picture_object.itemset((i, j, 1), 0)
                picture_object.itemset((i, j, 2), 0)
        ''' 去掉速度'''
        for i in range(50, 200):
            for j in range(0, 145):
                picture_object.itemset((i, j, 0), 0)
                picture_object.itemset((i, j, 1), 0)
                picture_object.itemset((i, j, 2), 0)

        '''去掉远光灯的动态'''
        for i in range(300, 450):
            for j in range(410, 630):
                picture_object.itemset((i, j, 0), 0)
                picture_object.itemset((i, j, 1), 0)
                picture_object.itemset((i, j, 2), 0)

        '''去掉右底部时间显示'''
        for i in range(655,695):
            for j in range(1645,1760):
                picture_object.itemset((i, j, 0), 0)
                picture_object.itemset((i, j, 1), 0)
                picture_object.itemset((i, j, 2), 0)

        '''去掉第二排部分显示'''
        for i in range(90,120):
            for j in range(115,400):
                picture_object.itemset((i, j, 0), 0)
                picture_object.itemset((i, j, 1), 0)
                picture_object.itemset((i, j, 2), 0)

        for i in range(300,520):
            for j in range(700,1300):
                picture_object.itemset((i, j, 0), 0)
                picture_object.itemset((i, j, 1), 0)
                picture_object.itemset((i, j, 2), 0)

        '''去掉多媒体信息'''
        for i in range(420,470):
            for j in range(1550,1760):
                picture_object.itemset((i, j, 0), 0)
                picture_object.itemset((i, j, 1), 0)
                picture_object.itemset((i, j, 2), 0)

        '''去掉安全带指示灯'''
        # for i in range (20,70):
        #     for j in range(555,590):
        #         picture_object.itemset((i, j, 0), 0)
        #         picture_object.itemset((i, j, 1), 0)
        #         picture_object.itemset((i, j, 2), 0)
        '''去掉安全带指示灯'''
        # for i in range(20, 70):
        #     for j in range(1335, 1375):
        #         picture_object.itemset((i, j, 0), 0)
        #         picture_object.itemset((i, j, 1), 0)
        #         picture_object.itemset((i, j, 2), 0)

        return picture_object

    def modify_reboot_self_inspection_picture(self,orgin_picture):
        picture1_object = cv2.imread("{0}".format(orgin_picture))
        self.modify_picture_reboot_self_inspection(picture1_object)
        cv2.imwrite("%s" % (orgin_picture), picture1_object)

    def modify_no_sepeed_expect_picture(self,orgin_picture):
        picture1_object = cv2.imread("{0}".format(orgin_picture))
        self.modify_picture_No_Speed(picture1_object)
        # self.modify_picture(picture1_object)
        cv2.imwrite("%s" % (orgin_picture), picture1_object)

    def modify_driver_expect_picture(self,orgin_picture):
        picture1_object = cv2.imread("{0}".format(orgin_picture))
        self.modify_picture_driver(picture1_object)
        # self.modify_picture(picture1_object)
        cv2.imwrite("%s" % (orgin_picture), picture1_object)

    def split_channel(self,picture_object):
        '''
        function :split b g r channel
        :param picture_object:
        :return:
        '''
        b,g,r = cv2.split(picture_object)
        return (b,g,r)

    def merge_channel(self,b,g,r):
        '''
        function :merge b,g,r channel
        :param b:
        :param g:
        :param r:
        :return:
        '''
        return cv2.merge([b,g,r])


    def modify_pixel(self,x,y,channel,picture_object,value):
        '''
        function: modify pixel
        :param x:  high
        :param y:  wide
        :param channel: {R,G,B}
        :param picture_object:
        :param value: {0~255}
        :return:
        '''
        picture_object.itemset((x,y,channel),value)
        return picture_object


    def picture_property(self,picture_object):
        pass

