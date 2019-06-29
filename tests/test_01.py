#! usr/bin/env python
# -*- coding: utf-8 -*-
# Date: 2019/6/23
# Author: snow

import os
import requests
import threading
from bs4 import BeautifulSoup

SPIDER_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/67.0.3396.87 Safari/537.36',
}

def auto_delay_reply_msg():
    print(datetime.datetime.now())
    print("msg")
    auto_delay_reply_msg_timer()

def auto_delay_reply_msg_timer():
    global timer  # 定义变量
    timer = threading.Timer(5, auto_delay_reply_msg)  # 60秒调用一次函数
    # 定时器构造函数主要有2个参数，第一个参数为时间，第二个参数为函数名
    timer.start()  # 启用定时器

import datetime
print(datetime.datetime.now())
auto_delay_reply_msg_timer()
