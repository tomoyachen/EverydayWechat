# coding=utf-8
"""
https://github.com/MZCretin/RollToolsApi#七笑花段子
获取随机段子
"""
import requests

def get_randomJokes():
    """
    获取随机段子
     https://github.com/MZCretin/RollToolsApi#七笑花段子
    :param
    :return: 随机段子
    """
    print('获取随机段子...')
    try:
        resp = requests.get('https://www.mxnzp.com/api/jokes/list/random')
        # print(resp.text)
        '''
        {
            "code": 1,
            "msg": "数据返回成功",
            "data": [
                {
                    "content": "朋友问我，如果在这个时代做个普通人，你最想做什么样的。我说，我想做个皇城根底下的社会闲散人员，好吃懒做，游手好闲，靠着祖上的余荫收点租子过日子。",
                    "updateTime": "2018-04-30 13:45:44"
                },
                ...这里只显示了一条数据...
            ]
        }
        '''
        if resp.status_code == 200:
            if resp.json()['code'] == 1:
                data_dict = resp.json()['data']
                content = data_dict[0]['content'].strip()
                return_text = content
                return "分享一个段子吧~\r\n" + return_text
            else:
                print('获取段子失败:{}'.format(resp.json()['msg']))
                # return None
        print('获取段子失败。')
    except Exception as exception:
        print(exception)
        # return None
    # return None


get_random_joke = get_randomJokes

if __name__ == '__main__':
    get_random_joke()

