# !/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time    : 2023/8/27 8:59
# @Author  : ziyou
# -------------------------------
# 喜爱帮注册地址 https://m.xiaicn.cn/invite/768228
# cron "27 7,12,23 * * *" script-path=xxx.py,tag=匹配cron用
# const $ = new Env('喜爱帮')
# 喜爱帮
# export xiaibang_ck='手机号#密码&手机号#密码'
# 注意：密码中不能包含 & # \n
# export xiaibang_ck='18*********#16947027******',多账号使用换行或&
# https://t.me/q7q7q7q7q7q7q7_ziyou


import os
import re
import sys
import time

import requests

CK_LIST = []

ck_list_str = os.getenv("xiaibang_ck")
if ck_list_str:
    CK_LIST += ck_list_str.replace("&", "\n").split("\n")


class XiAiBang:
    def __init__(self, ck, index):
        self.phone_number, self.password = ck.split('#')
        self.cookies = {'NiuToken': '05dbh4p9bidce77uk13vl0fcedsjgapd', }
        self.headers = {'Host': 'm.xiaicn.com',
                        'Connection': 'keep-alive',
                        'Accept': 'application/json, image/webp',
                        'X-Requested-With': 'XMLHttpRequest',
                        'Content-Type': 'application/x-www-form-urlencoded',
                        'Origin': 'https://m.xiaicn.com',
                        'Sec-Fetch-Site': 'same-origin',
                        'Sec-Fetch-Mode': 'cors',
                        'Sec-Fetch-Dest': 'empty',
                        'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7', }

    # 登录
    def login(self):
        headers = self.headers
        params = {'_random': str(time.time() * 1000), }
        data = {'_csrf_token': '8.oKU--pL_C15blWC3r0gQ0hcs0XN7paImwTR4OWq4nDg.'
                               '4pBtksudYBprzBfF6z1ztG1GmyUQ18ZKgl0JZg3d-V3p52S0xqwyOTLvWA',
                '_target_path': '',
                '_username': self.phone_number,
                '_password': self.password, }
        response = requests.post('https://m.xiaicn.com/cas/login', params=params, cookies=self.cookies, headers=headers,
                                 data=data)
        response_dict = response.json()
        # print(response_dict)
        if response_dict.get('code') == 0:
            print('登录成功')
            # print(response.headers.get('Set-Cookie'))
            set_cookie_header = response.headers.get('Set-Cookie')
            # 使用正则表达式提取 USER_REMEMBER_ME 值
            _match = re.search(r"USER_REMEMBER_ME=([^;]+)", set_cookie_header)
            if _match:
                _value = _match.group(1)
                # print(_value)
                self.cookies.update({'USER_REMEMBER_ME': _value})
                return True
        print(f'签到失败 {response_dict.get("msg")}')
        return False

    # 获取用户信息
    def get_infomation(self):
        headers = self.headers
        response = requests.get('https://m.xiaicn.com/user/capital',
                                cookies=self.cookies, headers=headers)  # 领取前请求分红界面
        response_text = response.text
        # print(response_text)
        balance = re.findall(r'<span class="num">(.*?)</span>', response_text)[0]
        print(f'{self.phone_number} 当前余额：{balance}')

    # 签到
    def check_in(self):
        headers = self.headers
        params = {'_random': str(time.time() * 1000), }
        data = {'csrfToken': '861a.Y2pb2RqfUoErOYGXvez77sHIFUVFodFiCqZmJs04v9M.'
                             'JhoclCrsYsdSFOzn26Ok1omtVhUckIsKTJcxF7VZ6uVbLj-BLcsI42hVtQ',
                'requestId': '2a460c7f206e220ead3f7fbd22788ba6', }
        response = requests.post('https://m.xiaicn.com/user/active/daily_sign/sign', params=params,
                                 cookies=self.cookies, headers=headers, data=data)
        response_dict = response.json()
        # print(response_dict)
        if response_dict.get('code') == 0:
            grant_money = response_dict.get("data").get("grantMoney")
            sign_count = response_dict.get("data").get("signCount")
            print(f'签到成功，今日签到获得{int(grant_money) / 10000}元，连续签到天数：{sign_count}')
            return
        print(f'签到失败 {response_dict.get("msg")}')

    # 领取签到任务奖励
    def receive_check_in_task_rewards(self):
        for task_id in ['152', '133']:
            headers = self.headers
            params = {'_random': str(time.time() * 1000), }
            data = 'taskId=152&isCurrent=1'
            response = requests.post('https://m.xiaicn.com/user/active/period_task/reward', params=params,
                                     cookies=self.cookies, headers=headers, data=data)
            response_dict = response.json()
            # print(response_dict)
            if response_dict.get('code') == 0:
                reward_money = response_dict.get("data").get("rewardMoney")
                if task_id == '152':
                    print(f'领取每日签到任务奖励成功，今日签到获得{int(reward_money) / 10000}元')
                    continue
                if task_id == '133':
                    print(f'领取每月签到任务奖励成功，今日签到获得{int(reward_money) / 10000}元')
                    continue
            if task_id == '152':
                print(f'每日签到任务 {response_dict.get("msg")}')
                continue
            if task_id == '133':
                print(f'每月签到任务 {response_dict.get("msg")}')
                continue

    # 领取分红金
    def receive_bonus(self):
        headers = self.headers
        requests.get('https://m.xiaicn.com/user/daily_dividend?_nav=0lkd55uo',
                     cookies=self.cookies, headers=headers)  # 领取前请求分红界面
        time.sleep(0.5)
        params = {'_random': str(time.time() * 1000), }
        data = f'_empty_post={time.time() * 1000}'
        response = requests.post('https://m.xiaicn.com/user/daily_dividend/award', params=params,
                                 cookies=self.cookies, headers=headers, data=data)
        response_dict = response.json()
        # print(response_dict)
        if response_dict.get('code') == 0:
            print(f'领取成功')
            return
        print(f'{response_dict.get("msg")}')

    def main(self):
        character = '★★'
        print(f'{character}开始登录')
        if not self.login():  # 登录
            return
        self.get_infomation()  # 获取用户信息
        print(f'{character}开始签到')
        self.check_in()
        print(f'{character}开始领取签到任务奖励')
        self.receive_check_in_task_rewards()
        print(f'{character}开始领取分红金')
        self.receive_bonus()
        self.get_infomation()  # 获取用户信息


def main(ck_list):
    if not ck_list:
        print('没有获取到账号！')
        return
    print(f'获取到{len(ck_list)}个账号！')
    for index, ck in enumerate(ck_list):
        print(f'*****第{index + 1}个账号*****')
        XiAiBang(ck, index).main()
        print('')


if __name__ == '__main__':
    main(CK_LIST)
    sys.exit()
