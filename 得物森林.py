# !/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time    : 2023/7/6 12:24
# @Author  : ziyou
# -------------------------------
# cron "1 8,12,15,18,22 * * *" script-path=xxx.py,tag=匹配cron用
# const $ = new Env('得物森林')
# 抓包获取 x_auth_token
# 得物森林
# export dewu_x_auth_token='Bearer ey**&Bearer ey**',多账号使用换行或&

import json
import os
import re
import sys
import time
import requests
from urllib.parse import urlparse, parse_qs

X_AUTH_TOKEN = []
# X_AUTH_TOKEN = ['Bearer eyJhbGciOi*******',
#                 'Bearer eyJhbGciOi*******', ]

dewu_x_auth_token = os.getenv("dewu_x_auth_token")
if dewu_x_auth_token:
    X_AUTH_TOKEN = dewu_x_auth_token.replace("&", "\n").split("\n")


# 获得地址中 params 中 键为key的值
def get_url_key_value(url, key):
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)
    _dict = {k: v[0] if len(v) == 1 else v for k, v in query_params.items()}
    key_value = _dict.get(key)
    return key_value


class DeWu:
    WATERTING_G: int = 40  # 每次浇水克数

    def __init__(self, x_auth_token, waterting_g=WATERTING_G):
        self.waterting_g = waterting_g
        self.session = requests.Session()
        self.headers = {'SK': '', 'x-auth-token': x_auth_token}
        self.tasks_completed_number = 0  # 任务完成数
        self.cumulative_tasks_list = []  # 累计计任务列表
        self.tasks_dict_list = []  # 任务字典列表

    # 种树奖品
    def tree_info(self):
        url = 'https://app.dewu.com/hacking-tree/v1/user/target/info'
        response = self.session.get(url, headers=self.headers)
        response_dict = response.json()
        # print(response_dict)
        if response_dict.get('code') == 200:
            name = response_dict.get('data').get('name')
            level = response_dict.get('data').get('level')
            return name, level

    # 领潮金币签到
    def check_in(self):
        url = 'https://app.dewu.com/hacking-game-center/v1/sign/sign'
        response = self.session.post(url, headers=self.headers)
        response_dict = response.json()
        # print(response_dict)
        if response_dict.get('code') == 200:
            print(f"签到成功！")
            return
        print(f"签到失败！ {response_dict.get('msg')}")

    # 水滴7天签到
    def droplet_check_in(self):
        url = 'https://app.dewu.com/hacking-tree/v1/sign/sign_in'
        response = self.session.post(url, headers=self.headers)
        response_dict = response.json()
        # print(response_dict)
        if response_dict.get('code') == 200:
            # 暂时设置，看看礼盒是什么先
            print(f"签到成功,获得{response_dict.get('data').get('Num')}g水滴！")
            return
        print(f"签到失败！ {response_dict.get('msg')}")

    # 领取气泡水滴
    def receive_droplet_extra(self):
        temporary_number = 0
        countdown_time = 0
        while True:
            url = 'https://app.dewu.com/hacking-tree/v1/droplet-extra/info'
            response = self.session.get(url, headers=self.headers)
            response_dict = response.json()
            # print(response_dict)
            if response_dict.get('code') != 200:
                print(f"获取气泡水滴信息失败! {response_dict}")
                return
            if response_dict.get('data').get('receivable') is True:  # 判断是否能领取
                if response_dict.get('data').get('dailyExtra'):  # 第一次领取时
                    water_droplet_number = response_dict.get('data').get('dailyExtra').get('totalDroplet')
                else:  # 第二次领取时
                    water_droplet_number = response_dict.get('data').get('onlineExtra').get('totalDroplet')
                # 如果二者不相等，说明浇水成功 但奖励有变化 继续浇水
                if temporary_number != water_droplet_number:  # 如果二者相等，说明浇水成功 但奖励没变化 不再浇水 直接领取
                    temporary_number = water_droplet_number
                    if water_droplet_number < 60:
                        print(f'当前气泡水滴未满，开始浇水！')
                        if self.waterting():  # 成功浇水 继续 否则 直接领取
                            time.sleep(1)
                            continue  # 浇水成功后查询信息
                print(f"当前可领取气泡水滴{water_droplet_number}g")
                url = 'https://app.dewu.com/hacking-tree/v1/droplet-extra/receive'
                response = self.session.post(url, headers=self.headers)
                response_dict = response.json()
                # print(response_dict)
                if response_dict.get('code') != 200:
                    countdown_time += 60
                    if countdown_time > 60:  # 已经等待过60s，任为领取成功，退出
                        print(f"领取气泡水滴失败! {response_dict}")
                        return
                    print(f'等待{countdown_time}秒后领取')
                    time.sleep(countdown_time)
                    continue
                print(f"领取气泡水滴成功! 获得{response_dict.get('data').get('totalDroplet')}g水滴")
                countdown_time = 0  # 领取成功，重置等待时间
            else:  # 今天不可领取了，退出
                water_droplet_number = response_dict.get('data').get('dailyExtra').get('totalDroplet')
                print(f"{response_dict.get('data').get('dailyExtra').get('popTitle')},"
                      f"已经积攒{water_droplet_number}g水滴!")
                return

    # 浇水充满气泡水滴
    def waterting_droplet_extra(self):
        while True:
            url = 'https://app.dewu.com/hacking-tree/v1/droplet-extra/info'
            response = self.session.get(url, headers=self.headers)
            response_dict = response.json()
            # print(response_dict)
            count = response_dict.get('data').get('dailyExtra').get('times')
            if not count:
                print(f"气泡水滴已充满，明日可领取{response_dict.get('data').get('dailyExtra').get('totalDroplet')}g")
                return
            for _ in range(count):
                if not self.waterting():  # 无法浇水时退出
                    return
                time.sleep(1)

    # 领取木桶水滴,200秒满一次,每天领取3次
    def receive_bucket_droplet(self):
        url = 'https://app.dewu.com/hacking-tree/v1/droplet/get_generate_droplet'
        response = self.session.post(url, headers=self.headers)
        response_dict = response.json()
        # print(response_dict)
        if response_dict.get('code') != 200:
            print(f"领取木桶水滴失败! {response_dict}")
            return
        print(f"领取木桶水滴成功! 获得{response_dict.get('data').get('droplet')}g水滴")

    # 判断木桶水滴是否可以领取
    def judging_bucket_droplet(self):
        url = 'https://app.dewu.com/hacking-tree/v1/droplet/generate_info'
        response = requests.get(url, headers=self.headers)
        response_dict = response.json()
        # print(response_dict)
        if response_dict.get('data').get('currentDroplet') == 100:
            print(f"今天已领取木桶水滴{response_dict.get('data').get('getTimes')}次！")
            self.receive_bucket_droplet()
            return True
        return False

    # 获取助力码
    def get_shared_code(self):
        url = 'https://app.dewu.com/hacking-tree/v1/keyword/gen'
        response = self.session.post(url, headers=self.headers)
        response_dict = response.json()
        # print(response_dict)
        if response_dict.get('code') != 200:
            print(f"获取助力码失败! {response_dict}")
            return
        keyword = response_dict.get('data').get('keyword')
        keyword_desc = response_dict.get('data').get('keywordDesc').replace('\n', '')
        print(f"获取助力码成功! {keyword_desc}")

    # 获得当前水滴数
    def get_droplet_number(self):
        url = 'https://app.dewu.com/hacking-tree/v1/user/init'
        data = {'keyword': '🌱😻🙉👶🌷💥'}
        response = requests.post(url, headers=self.headers, data=json.dumps(data))
        response_dict = response.json()
        # print(response_dict)
        droplet_number = response_dict.get('data').get('droplet')
        return droplet_number

    # 领取累计任务奖励
    def receive_cumulative_tasks_reward(self, condition):
        url = 'https://app.dewu.com/hacking-tree/v1/task/extra'
        _json = {'condition': condition}
        response = requests.post(url, headers=self.headers, json=_json)
        response_dict = response.json()
        # print(response_dict)
        if response_dict.get('code') != 200:
            print(f"领取累计任务奖励失败! {response_dict}")
            return
        print(f"领取累计任务奖励成功! 获得{response_dict.get('data').get('num')}g水滴")

    # 领取任务奖励
    def receive_task_reward(self, classify, task_id, task_type):
        url = 'https://app.dewu.com/hacking-tree/v1/task/receive'
        if task_type in [251, ]:
            _json = {'classify': classify, 'taskId': task_id, 'completeFlag': 1}
        else:
            _json = {'classify': classify, 'taskId': task_id}
        response = requests.post(url, headers=self.headers, json=_json)
        response_dict = response.json()
        # print(response_dict)
        if response_dict.get('code') != 200:
            print(f"领取任务奖励失败! {response_dict}")
            return
        print(f"领取任务奖励成功! 获得{response_dict.get('data').get('num')}g水滴")

    # 领取浇水奖励
    def receive_watering_reward(self):
        url = 'https://app.dewu.com/hacking-tree/v1/tree/get_watering_reward'
        _json = {'promote': ''}
        response = requests.post(url, headers=self.headers, json=_json)
        response_dict = response.json()
        # print(response_dict)
        if response_dict.get('code') != 200:
            print(f"领取浇水奖励失败! {response_dict}")
            return
        print(f"领取浇水奖励成功! 获得{response_dict.get('data').get('currentWateringReward').get('rewardNum')}g水滴")

    # 领取等级奖励
    def receive_level_reward(self):
        url = 'https://app.dewu.com/hacking-tree/v1/tree/get_level_reward'
        _json = {'promote': ''}
        response = requests.post(url, headers=self.headers, json=_json)
        response_dict = response.json()
        # print(response_dict)
        if response_dict.get('code') != 200:
            print(f"领取浇水奖励失败! {response_dict}")
            return
        print(f"领取浇水奖励成功! 获得{response_dict.get('data').get('currentWateringReward').get('rewardNum')}g水滴")

    # 浇水
    def waterting(self):
        url = 'https://app.dewu.com/hacking-tree/v1/tree/watering'
        response = requests.post(url, headers=self.headers)
        response_dict = response.json()
        # print(response_dict)
        if response_dict.get('code') != 200:
            print(f"浇水失败! {response_dict}")
            return False
        print(f"成功浇水{self.waterting_g}g! ")
        if response_dict.get('data').get('nextWateringTimes') == 0:
            print('开始领取浇水奖励！')
            time.sleep(1)
            self.receive_watering_reward()
        return True

    # 多次执行浇水，领取浇水奖励
    def execute_receive_watering_reward(self):
        while True:
            url = 'https://app.dewu.com/hacking-tree/v1/tree/get_tree_info'
            response = self.session.get(url, headers=self.headers)
            response_dict = response.json()
            # print(response_dict)
            if response_dict.get('code') != 200:
                print(f"获取种树进度失败! {response_dict}")
                return
            if not response_dict.get('data').get('wateringReward'):  # 没有奖励时退出
                return
            count = response_dict.get('data').get('nextWateringTimes')
            for _ in range(count):
                if not self.waterting():  # 无法浇水时退出
                    return
                time.sleep(1)

    # 浇水直到少于1000g
    def waterting_until_less_than_1000g(self):
        droplet_number = self.get_droplet_number()
        if droplet_number > 1000:
            count = int((droplet_number - 1000) / self.waterting_g)
            for _ in range(count + 1):
                if not self.waterting():  # 无法浇水时退出
                    return
                time.sleep(1)

    # 提交任务完成状态
    def submit_task_completion_status(self, _json):
        url = 'https://app.dewu.com/hacking-task/v1/task/commit'
        response = requests.post(url, headers=self.headers, json=_json)
        response_dict = response.json()
        # print(response_dict)
        if response_dict.get('code') == 200:
            return True
        return False

    # 获取任务列表
    def get_task_list(self):
        url = 'https://app.dewu.com/hacking-tree/v1/task/list'
        response = self.session.get(url, headers=self.headers)
        response_dict = response.json()
        # print(response_dict)
        if response_dict.get('code') == 200:
            self.tasks_completed_number = response_dict.get('data').get('userStep')  # 任务完成数量
            self.cumulative_tasks_list = response_dict.get('data').get('extraAwardList')  # 累计任务列表
            self.tasks_dict_list = response_dict.get('data').get('taskList')  # 任务列表
            # 'taskId' 任务ID
            # 'taskName' 任务名字
            # 'isComplete' 是否未完成
            # 'isReceiveReward' 完成后是否领取奖励
            # 'taskType'任务类型
            # 'rewardCount' 完成任务所获得的奖励水滴
            # 'isObtain' 是否完成任务前置要求
            # 'jumpUrl' 是否完成任务前置要求
            return True

    # 水滴大放送任务步骤1
    def task_obtain(self, task_id, task_type):
        url = 'https://app.dewu.com/hacking-task/v1/task/obtain'
        _json = {'taskId': task_id, 'taskType': task_type}
        response = requests.post(url, headers=self.headers, json=_json)
        response_dict = response.json()
        # print(response_dict)
        if response_dict.get('code') == 200 and response_dict.get('status') == 200:
            return True
        return False

    # 浏览任务开始  且等待16s TaskType有变化  浏览15s会场会变成16
    def task_commit_pre(self, _json):
        url = 'https://app.dewu.com/hacking-task/v1/task/pre_commit'
        response = requests.post(url, headers=self.headers, json=_json)
        response_dict = response.json()
        # print(response_dict)
        if response_dict.get('code') == 200 and response_dict.get('status') == 200:
            return True
        return False

    # 执行任务
    def execute_task(self):
        self.get_task_list()  # 刷新任务列表
        for tasks_dict in self.tasks_dict_list:
            if tasks_dict.get('isReceiveReward') is True:  # 今天不能进行操作了，跳过
                continue
            if tasks_dict.get('rewardCount') >= 3000:  # 获取水滴超过3000的，需要下单，跳过
                continue
            classify = tasks_dict.get('classify')
            task_id = tasks_dict.get('taskId')
            task_type = tasks_dict.get('taskType')
            task_name = tasks_dict.get('taskName')
            btd = get_url_key_value(tasks_dict.get('jumpUrl'), 'btd')
            btd = int(btd) if btd else btd  # 如果bid存在 转换为整数类型

            if tasks_dict.get('isComplete') is True:  # 可以直接领取奖励的
                if task_name == '领40g水滴值' and not tasks_dict.get('receivable'):  # 如果该值不存在，说明已经领过40g水滴了
                    continue
                print(f'开始任务：{task_name}')
                self.receive_task_reward(classify, task_id, task_type)
                continue

            print(f'开始任务：{task_name}')
            if task_name == '完成一次签到':  # 签到
                self.check_in()
                data = {'taskId': tasks_dict['taskId'], 'taskType': str(tasks_dict['taskType'])}
                if self.submit_task_completion_status(data):
                    self.receive_task_reward(classify, task_id, task_type)  # 领取奖励
                    continue

            if task_name == '领40g水滴值':  # 每天8点/12点/18点/22点 领40g水滴
                self.receive_task_reward(classify, task_id, task_type)  # 领取奖励
                continue

            if task_name == '收集一次水滴生产':
                if self.judging_bucket_droplet():
                    self.receive_task_reward(classify, task_id, task_type)  # 领取奖励
                else:
                    print('当前木桶水滴为达到100g，下次来完成任务吧！')
                continue

            if task_name in ['去0元抽奖参与抽游戏皮肤', '参与1次上上签活动', '从桌面组件访问许愿树',
                             '去95分App逛潮奢尖货', ]:
                _json = _json = {'taskId': task_id, 'taskType': str(task_type)}
                self.submit_task_completion_status(_json)  # 提交完成状态
                self.receive_task_reward(classify, task_id, task_type)  # 领取奖励
                continue

            if any(re.match(pattern, task_name) for pattern in ['收藏.*']):
                _json = _json = {'taskId': task_id, 'taskType': str(task_type), 'btd': btd, 'spuId': 0}
                self.submit_task_completion_status(_json)  # 提交完成状态
                self.receive_task_reward(classify, task_id, task_type)  # 领取奖励
                continue

            if any(re.match(pattern, task_name) for pattern in ['订阅.*']):
                _json = _json = {'taskId': task_id, 'taskType': str(task_type), 'btd': btd}
                self.submit_task_completion_status(_json)  # 提交完成状态
                self.receive_task_reward(classify, task_id, task_type)  # 领取奖励
                continue

            if any(re.match(pattern, task_name) for pattern in ['逛逛国潮夏季专场', '浏览.*15s']):
                _json = {'taskId': task_id, 'taskType': task_type, 'btd': btd}
                if self.task_commit_pre(_json):
                    print(f'等待16秒！')
                    time.sleep(16)
                    _json = {'taskId': task_id, 'taskType': str(task_type), 'activityType': None, 'activityId': None,
                             'taskSetId': None, 'venueCode': None, 'venueUnitStyle': None, 'taskScene': None,
                             'btd': btd}
                    self.submit_task_completion_status(_json)  # 提交完成状态
                    self.receive_task_reward(classify, task_id, task_type)  # 领取奖励
                    continue

            if any(re.match(pattern, task_name) for pattern in ['晒图']):
                _json = {'taskId': task_id, 'taskType': task_type}
                if self.task_commit_pre(_json):
                    print(f'等待16秒！')
                    time.sleep(16)
                    _json = {'taskId': task_id, 'taskType': str(task_type), 'activityType': None, 'activityId': None,
                             'taskSetId': None, 'venueCode': None, 'venueUnitStyle': None, 'taskScene': None}
                    self.submit_task_completion_status(_json)  # 提交完成状态
                    self.receive_task_reward(classify, task_id, task_type)  # 领取奖励
                    continue

            if task_name == '完成五次浇灌':
                count = tasks_dict.get('total') - tasks_dict.get('curStep')  # 还需要浇水的次数=要浇水的次数-以浇水的次数
                if self.get_droplet_number() < (count * self.waterting_g):
                    print(f'当前水滴不足以完成任务，跳过')
                    continue
                for _ in range(count):
                    if not self.waterting():  # 无法浇水时退出
                        continue
                    time.sleep(1)
                _json = {'taskId': tasks_dict['taskId'], 'taskType': str(tasks_dict['taskType'])}
                if self.submit_task_completion_status(_json):
                    self.receive_task_reward(classify, task_id, task_type)  # 领取奖励
                    continue

            if task_type == 251 and '水滴大放送' in task_name:
                if self.task_obtain(task_id, task_type):
                    _json = {'taskId': task_id, 'taskType': 16}
                    if self.task_commit_pre(_json):
                        print(f'等待16秒！')
                        time.sleep(16)
                        _json = {'taskId': task_id, 'taskType': str(task_type)}
                        self.submit_task_completion_status(_json)  # 提交完成状态
                        self.receive_task_reward(classify, task_id, task_type)  # 领取奖励
                        continue

    # 执行累计任务
    def execute_cumulative_task(self):
        self.get_task_list()  # 刷新任务列表
        for task in self.cumulative_tasks_list:
            if task.get('status') == 1:
                print(f'开始领取累计任务数达{task.get("condition")}个的奖励')
                self.receive_cumulative_tasks_reward(task.get('condition'))
                time.sleep(1)

    # 水滴投资
    def droplet_invest(self):
        url = 'https://app.dewu.com/hacking-tree/v1/invest/info'
        response = requests.get(url, headers=self.headers)
        response_dict = response.json()
        # print(response_dict)
        if response_dict.get('data').get('isToday') is False:  # 可领取
            self.received_droplet_invest()
        else:
            print('今日已领取过水滴投资奖励了')
        if response_dict.get('data').get('triggered') is True:  # 可投资
            url = 'https://app.dewu.com/hacking-tree/v1/invest/commit'
            response = requests.post(url, headers=self.headers)
            response_dict = response.json()
            # print(response_dict)
            if response_dict.get('code') == 200 and response_dict.get('status') == 200:
                print('水滴投资成功，水滴-100g')
            else:
                print(f'水滴投资失败：{response_dict}')
        else:
            print('今日已经水滴投资过了！')

    # 领取水滴投资
    def received_droplet_invest(self):
        url = 'https://app.dewu.com/hacking-tree/v1/invest/receive'
        response = requests.post(url, headers=self.headers)
        response_dict = response.json()
        # print(response_dict)
        profit = response_dict.get('data').get('profit')
        print(f"领取水滴投资成功! 获得{profit}g水滴")

    # 获取种树进度
    def get_tree_planting_progress(self):
        url = 'https://app.dewu.com/hacking-tree/v1/tree/get_tree_info'
        response = self.session.get(url, headers=self.headers)
        response_dict = response.json()
        # print(response_dict)
        if response_dict.get('code') != 200:
            print(f"获取种树进度失败! {response_dict}")
            return
        level = response_dict.get('data').get('level')
        current_level_need_watering_droplet = response_dict.get('data').get('currentLevelNeedWateringDroplet')
        user_watering_droplet = response_dict.get('data').get('userWateringDroplet')
        print(f"种树进度: {level}级 {user_watering_droplet}/{current_level_need_watering_droplet}")

    def main(self):
        name, level = self.tree_info()
        print(f'目标：{name}')
        print(f'剩余水滴：{self.get_droplet_number()}')
        # 获取种树进度
        self.get_tree_planting_progress()
        self.droplet_check_in()  # 签到
        print('开始领取气泡水滴！')
        self.receive_droplet_extra()
        print('开始完成每日任务')
        self.execute_task()
        self.execute_cumulative_task()
        print('开始领取木桶水滴！')
        self.judging_bucket_droplet()
        print('开始多次执行浇水，领取浇水奖励')
        self.execute_receive_watering_reward()
        print('开始浇水充满气泡水滴')
        self.waterting_droplet_extra()
        print('开始进行水滴投资')
        self.droplet_invest()
        print('开始进行浇水直到少于1000g')
        self.waterting_until_less_than_1000g()
        print(f'剩余水滴：{self.get_droplet_number()}')
        # 获取种树进度
        self.get_tree_planting_progress()


# 主程序
def main(ck_list):
    if not ck_list:
        print('没有获取到账号！')
        return
    print(f'获取到{len(ck_list)}个账号！')
    for index, ck in enumerate(ck_list):
        print(f'*****第{index + 1}个账号*****')
        DeWu(ck).main()
        print('')


if __name__ == '__main__':
    main(X_AUTH_TOKEN)
    sys.exit()
