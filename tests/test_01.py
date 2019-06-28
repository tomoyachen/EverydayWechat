#! usr/bin/env python
# -*- coding: utf-8 -*-
# Date: 2019/6/23
# Author: snow

import os
import requests
from bs4 import BeautifulSoup

SPIDER_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/67.0.3396.87 Safari/537.36',
}



def get_wufazhuce_info():
    """
    获取格言信息（从『一个。one』获取信息 http://wufazhuce.com/）
    :return: str， 一句格言或者短语。
    """
    print('获取 ONE 信息...')
    user_url = 'http://wufazhuce.com/'
    try:
        resp = requests.get(user_url, headers=SPIDER_HEADERS)
        if resp.status_code == 200:
            soup_texts = BeautifulSoup(resp.text, 'lxml')

            # 『one -个』 中的每日一句
            # every_msg = soup_texts.find_all('div', class_='fp-one-cita')[0].find('a').text
            every_msg = soup_texts.find('div', class_='fp-one-cita').text #只取当天的这句
            print("一个·ONE文字内容", every_msg.strip())
            return every_msg
        print('获取 ONE 失败。')
    except Exception as exception:
        print(exception)
        return None
    return None




def get_wufazhuce_image():
    """
    获取格言信息（从『一个。one』获取信息 http://wufazhuce.com/）
    :return: str， 一句格言或者短语。
    """
    print('获取 ONE 信息...')
    user_url = 'http://wufazhuce.com/'
    try:
        resp = requests.get(user_url, headers=SPIDER_HEADERS)
        if resp.status_code == 200:
            soup_texts = BeautifulSoup(resp.text, 'lxml')
            # 『one -个』 中的每日一句
            # every_msg = soup_texts.find_all('div', class_='fp-one-cita')[0].find('a').text
            every_msg = soup_texts.find('img', class_='fp-one-imagen')["src"]  #只取图片地址
            print ("一个·ONE图片地址", every_msg)
            return every_msg
        print('获取 ONE 失败。')
    except Exception as exception:
        print(exception)
        return None
    return None

get_one_words = get_wufazhuce_info
get_one_image = get_wufazhuce_image
print(get_wufazhuce_info())
print(get_one_image())

image_url = get_one_image()
response = requests.get(image_url)
img = response.content
with open('D:\one_today_image.jpg', 'wb') as f:
    f.write(img)