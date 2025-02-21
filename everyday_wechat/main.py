# coding=utf-8

"""
每天定时给多个女友发给微信暖心话
核心代码。
"""
import os
import time
import threading
import datetime
# from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.schedulers.background import BackgroundScheduler
import itchat
import random
from itchat.content import *
import sys
sys.path.append("..") # 引入上一级目录
from everyday_wechat.utils.common import get_yaml
from everyday_wechat.utils.data_collection import (
    get_bot_info,
    get_weather_info,
    get_dictum_info,
    get_diff_time,
    get_xzw_info,
    get_joke_info,
    get_one_image,
)

reply_userNames = []
FILEHELPER_MARK = ['文件传输助手', 'filehelper']  # 文件传输助手标识
FILEHELPER = 'filehelper'


def run():
    """ 主运行入口 """
    conf = get_yaml()
    if not conf:  # 如果 conf，表示配置文件出错。
        print('程序中止...')
        return
    # 判断是否登录，如果没有登录则自动登录，返回 False 表示登录失败
    if not is_online(auto_login=True):
        return




def is_online(auto_login=False):
    """
    判断是否还在线。
    :param auto_login: bool,当为 Ture 则自动重连(默认为 False)。
    :return: bool,当返回为 True 时，在线；False 已断开连接。
    """

    def _online():
        """
        通过获取好友信息，判断用户是否还在线。
        :return: bool,当返回为 True 时，在线；False 已断开连接。
        """
        try:
            if itchat.search_friends():
                return True
        except IndexError:
            return False
        return True

    if _online(): return True  # 如果在线，则直接返回 True
    if not auto_login:  # 不自动登录，则直接返回 False
        print('微信已离线..')
        return False

    hotReload = not get_yaml().get('is_forced_switch', False)  # 切换微信号，重新扫码。
    loginCallback = init_wechat
    exitCallback = exit_msg
    for _ in range(2):  # 尝试登录 2 次。
        if os.environ.get('MODE') == 'server':
            # 命令行显示登录二维码。
            itchat.auto_login(enableCmdQR=2, hotReload=hotReload, loginCallback=loginCallback,
                              exitCallback=exitCallback)
            itchat.run(blockThread=True)
        else:
            itchat.auto_login(hotReload=hotReload, loginCallback=loginCallback, exitCallback=exitCallback)
            itchat.run(blockThread=True)
        if _online():
            print('登录成功')
            return True

    print('登录失败。')
    return False


def init_wechat():
    """ 初始化微信所需数据 """
    set_system_notice('登录成功')

    conf = get_yaml()
    itchat.get_friends(update=True)  # 更新好友数据。
    itchat.get_chatrooms(update=True)  # 更新群聊数据。
    for name in conf.get('auto_reply_names'):
        if name.lower() in FILEHELPER_MARK:  # 判断是否文件传输助手
            if FILEHELPER not in reply_userNames:
                reply_userNames.append(FILEHELPER)
            continue
        friend = get_friend(name)
        if friend:
            reply_userNames.append(friend['UserName'])
        else:
            print('自动回复中的好友昵称『{}』有误。'.format(name))
    # print(reply_userNames)


    if conf.get('is_auto_relay'):
        print('已开启图灵自动回复...')

    init_alarm()  # 初始化定时任务

def init_alarm():
    """ 初始化定时提醒 """
    alarm_info = get_yaml().get('alarm_info', None)
    if not alarm_info: return
    is_alarm = alarm_info.get('is_alarm', False)
    if not is_alarm: return
    alarm_timed = alarm_info.get('alarm_timed', None)
    if not alarm_timed: return
    hour, minute = [int(x) for x in alarm_timed.split(':')]

    # 检查数据的有效性
    for info in get_yaml().get('girlfriend_infos'):
        if not info: break  # 解决无数据时会出现的 bug。
        wechat_name = info.get('wechat_name')
        if (wechat_name and wechat_name.lower() not in FILEHELPER_MARK
                and not get_friend(wechat_name)):
            print('定时任务中的好友名称『{}』有误。'.format(wechat_name))

        # 更新信息
        group_name = info.get('group_name')
        if group_name and not get_group(group_name):
            print('定时任务中的群聊名称『{}』有误。'
                  '(注意：必须要把需要的群聊保存到通讯录)'.format(group_name))

    # 定时任务
    scheduler = BackgroundScheduler()
    # 每天9：30左右给女朋友发送每日一句
    scheduler.add_job(send_alarm_msg, 'cron', hour=hour,
                      minute=minute, misfire_grace_time=15 * 60)

    # # 每隔 30 秒发送一条数据用于测试。
    # scheduler.add_job(send_alarm_msg, 'interval', seconds=30)

    print('已开启定时发送提醒功能...')
    scheduler.start()


@itchat.msg_register([TEXT])
def text_reply(msg):
    """ 监听用户消息，用于自动回复 """
    try:
        if not get_yaml().get('is_auto_relay'):
            return
        # print(json.dumps(msg, ensure_ascii=False))
        # print(reply_userNames)
        # 获取发送者的用户id
        uuid = FILEHELPER if msg['ToUserName'] == FILEHELPER else msg.fromUserName
        # 如果用户id是自动回复列表的人员
        if uuid in reply_userNames:
            receive_text = msg['Content']  # 好友发送来的消息内容
            # 好友叫啥
            nickName = FILEHELPER if uuid == FILEHELPER else msg.user.nickName
            print('\n{}发来信息：{}'.format(nickName, receive_text))
            reply_text = get_bot_info(receive_text, uuid)  # 获取自动回复
            time.sleep(random.randint(0, 2))  # 休眠一秒，保安全。想更快的，可以直接注释。
            if receive_text == "test":
                reply_text = "./one_today_image.jpg"  # 获取自动回复
                # reply_text = "D:\\sss.jpg"  # 获取自动回复
                itchat.send_image(reply_text, toUserName=uuid)
                print('回复图片{}：{}\n'.format(nickName, reply_text))
            elif reply_text:  # 如内容不为空，回复消息
                reply_text = reply_text if not uuid == FILEHELPER else '机器人回复：' + reply_text
                itchat.send(reply_text, toUserName=uuid)

                print('回复{}：{}\n'.format(nickName, reply_text))
            else:
                print('自动回复失败\n'.format(receive_text))
    except Exception as e:
        print(str(e))

'''
@itchat.msg_register([itchat.content.TEXT, itchat.content.PICTURE,itchat.content.RECORDING,itchat.content.ATTACHMENT,itchat.content.VIDEO],isFriendChat=True, isGroupChat=True)
def auto_delay_reply(msg): #自动延时回复
    try:
        if not get_yaml().get('is_auto_relay'):
            return
        uuid = FILEHELPER if msg['ToUserName'] == FILEHELPER else msg.fromUserName
        if uuid in reply_userNames:
            receive_text = msg['Content']   # 好友发送来的消息内容
            nickName = FILEHELPER if uuid == FILEHELPER else msg.user.nickName #昵称
            print('\n{}发来信息：{}'.format(nickName, receive_text))
            reply_text = "你好呀。我现在有事在身无法立刻回复，十分抱歉。"
            print(datetime.datetime.now())
            print("start")
            auto_delay_reply_msg_timer(uuid)
    except Exception as e:
        print(str(e))


def auto_delay_reply_msg_timer(uuid):
    print(datetime.datetime.now())
    global timer  # 定义变量
    timer = threading.Timer(60, auto_delay_reply_msg,(uuid))  # 60秒调用一次函数
    # 定时器构造函数主要有2个参数，第一个参数为时间，第二个参数为函数名
    timer.start()  # 启用定时器


def auto_delay_reply_msg(uuid):
    print(datetime.datetime.now())
    itchat.send("你好呀。我现在有事在身无法立刻回复，十分抱歉。", toUserName=uuid)
    auto_delay_reply_msg_timer(uuid)
'''



def send_alarm_msg():
    """ 发送定时提醒 """
    print('\n启动定时自动提醒...')
    conf = get_yaml()
    for gf in conf.get('girlfriend_infos'):
        dictum = get_dictum_info(gf.get('dictum_channel'))
        weather = get_weather_info(gf.get('city_name'))
        diff_time = get_diff_time(gf.get('start_date'))
        sweet_words = gf.get('sweet_words')
        horoscope = get_xzw_info(gf.get("birthday"))
        joke = get_joke_info(gf.get('is_joke', False))
        # 如果渠道是一个·ONE 就发图片
        # send_image_path = get_one_image(gf.get('dictum_channel'))
        send_image_path = get_one_image(1) #强制发one图片

        send_msg = '\n'.join(x for x in [weather, "\r", dictum, "\r", diff_time, sweet_words, "\r", horoscope] if x)
        print(send_msg)

        if not send_msg or not is_online(): continue
        # 给微信好友发信息
        wechat_name = gf.get('wechat_name')
        if wechat_name:
            if wechat_name.lower() in FILEHELPER_MARK:
                if send_image_path:
                    itchat.send_image(send_image_path, toUserName=FILEHELPER)
                itchat.send(send_msg, toUserName=FILEHELPER)
                if joke:
                    itchat.send(joke, toUserName=FILEHELPER)
                print('定时给『{}』发送的内容是:\n{}\n发送成功...\n\n'.format(wechat_name, send_msg))
            else:
                wechat_users = itchat.search_friends(name=wechat_name)
                if not wechat_users: continue
                if send_image_path:
                    wechat_users[0].send_image(send_image_path)
                wechat_users[0].send(send_msg)
                if joke:
                    wechat_users[0].send(joke)
                print('定时给『{}』发送的内容是:\n{}\n发送成功...\n\n'.format(wechat_name, send_msg))

        # 给群聊里发信息
        group_name = gf.get('group_name')
        if group_name:
            group = get_group(group_name)
            if group:
                if send_image_path:
                    group.send_image(send_image_path)
                group.send(send_msg)
                if joke:
                    group.send(joke)
                print('定时给群聊『{}』发送的内容是:\n{}\n发送成功...\n\n'.format(group_name, send_msg))

    print('自动提醒消息发送完成...\n')


def set_system_notice(text):
    """
    给文件传输助手发送系统日志。
    :param text:日志内容
    :return:None
    """
    if text:
        text = '系统通知：' + text
        itchat.send(text, toUserName=FILEHELPER)


def exit_msg():
    set_system_notice('项目已断开连接')



def get_group(gruop_name, update=False):
    """
    根据群组名获取群组数据
    :param wechat_name: 群组名
    :param update: 强制更新群组数据
    :return: msg
    """
    if update: itchat.get_chatrooms(update=True)
    if not gruop_name: return None
    groups = itchat.search_chatrooms(name=gruop_name)
    if not groups: return None
    return groups[0]


def get_friend(wechat_name, update=False):
    """
    根据用户名获取用户数据
    :param wechat_name: 用户名
    :param update: 强制更新用户数据
    :return: msg
    """
    if update: itchat.get_friends(update=True)
    if not wechat_name: return None
    friends = itchat.search_friends(name=wechat_name)
    if not friends: return None
    return friends[0]


if __name__ == '__main__':
    run()
    # send_alarm_msg()
