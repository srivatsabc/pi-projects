#!/usr/bin/python
# -*- coding:utf-8 -*-

import sys
import os
picdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'pic')
libdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'lib')
if os.path.exists(libdir):
    sys.path.append(libdir)

import logging    
import time
import traceback
from waveshare_OLED import OLED_1in5_rgb
from PIL import Image,ImageDraw,ImageFont
logging.basicConfig(level=logging.DEBUG)
from datetime import date
from datetime import datetime
# Display Refresh
LOOPTIME = 1.0

def init():
    global disp
    disp = OLED_1in5_rgb.OLED_1in5_rgb()
    disp.Init()

    logging.info ("***draw image")
    Himage2 = Image.new('RGB', (disp.width, disp.height), 0)  # 0: clear the frame
    bmp = Image.open(os.path.join(picdir, 'train.bmp'))
    Himage2.paste(bmp, (-7,0))
    Himage2=Himage2.rotate(0) 	
    disp.ShowImage(disp.getbuffer(Himage2)) 
    time.sleep(3)    
    disp.clear()
    #time.sleep(3)

def display_main():
    try:
        image1 = Image.new('RGB', (disp.width, disp.height), 0)
        draw = ImageDraw.Draw(image1)
        font = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 13)
        logging.info ("***draw line")
        draw.line([(0,0),(127,0)], fill = "WHITE")
        draw.line([(0,0),(0,127)], fill = "WHITE")
        draw.line([(0,127),(127,127)], fill = "WHITE")
        draw.line([(127,0),(127,127)], fill = "WHITE")
        logging.info ("***draw text")
        draw.text((10,16), 'Date: ' + date.today().strftime("%b-%d-%Y"), font = font, fill = "CYAN")
        draw.text((10,32), 'Time: ' + datetime.today().strftime("%H:%M:%S"), font = font, fill = "CYAN")
        draw.text((10,64), 'Ready for scan ', font = font, fill = "ORANGE")
        image1 = image1.rotate(0)
        #disp.Draw(image1)
        disp.ShowImage(disp.getbuffer(image1))
        time.sleep(5)
        OLED_1in5_rgb.config.module_exit()
        #disp.Send()
        #disp.Draw()
    except IOError as e:
        logging.info(e)

def display(lat, long):
    try:
        image1 = Image.new('RGB', (disp.width, disp.height), 0)
        draw = ImageDraw.Draw(image1)
        font = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 13)
        logging.info ("***draw line")
        draw.line([(0,0),(127,0)], fill = "WHITE")
        draw.line([(0,0),(0,127)], fill = "WHITE")
        draw.line([(0,127),(127,127)], fill = "WHITE")
        draw.line([(127,0),(127,127)], fill = "WHITE")
        logging.info ("***draw text")
        draw.text((10,0), 'Rfid detected: ', font = font, fill = "ORANGE")
        draw.text((10,16), 'Date: ' + date.today().strftime("%b-%d-%Y"), font = font, fill = "GREEN")
        draw.text((10,32), 'Time: ' + datetime.today().strftime("%H:%M:%S"), font = font, fill = "GREEN")
        image1 = image1.rotate(0)
        #disp.Draw(image1)
        disp.ShowImage(disp.getbuffer(image1))
        time.sleep(5)
        OLED_1in5_rgb.config.module_exit()
        #disp.Send()
        #disp.Draw()
    except IOError as e:
        logging.info(e)

init()