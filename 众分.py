# !/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time    : 2023/10/8 18:47
# @Author  : ziyou
# -------------------------------
# 注册下载地址 http://lses-lcae.ihuju.cn/index.php/Home/Public/reg/recom/711458
# 每日一毛的样子
# cron "1 8,22 * * *" script-path=xxx.py,tag=匹配cron用
# const $ = new Env('众分')
# 抓包 lses-lcae.ihuju.cn 域名下 cookie中的token
# 众分
# export zhongfen_token='df**********18&df**********18',多账号使用换行或&
# 青龙拉取命令 ql raw https://ghproxy.com/https://raw.githubusercontent.com/q7q7q7q7q7q7q7/ziyou/main/众分.py
# https://t.me/q7q7q7q7q7q7q7_ziyou

import concurrent.futures
import os
import re
import sys
import time

import requests

ck_list = []

# 设置最大线程数
MAX_WORKERS = 5
ck_signal_list = []


# 加载环境变量
def get_env():
    global ck_list

    env_str = os.getenv("zhongfen_token")
    if env_str:
        ck_list += env_str.replace("&", "\n").split("\n")


class ZhongFen:
    def __init__(self, ck, index):
        self.ck = ck
        self.index = index
        self.headers = {
            'Host': 'lses-lcae.ihuju.cn',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Linux; Android 13; 22041211AC Build/TP1A.220624.014; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/115.0.5790.166 Mobile Safari/537.36  XiaoMi/MiuiBrowser/10.8.1 LT-APP/45/158/YM-RT/',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'X-Requested-With': 'com.cb.tiaoma.zf',
            'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
            'Cookie': f'token={ck}',
        }

    # 获取个人信息
    def get_infomation(self):
        headers = self.headers
        index = self.index
        response = requests.get('http://lses-lcae.ihuju.cn/', headers=headers)
        response_text = response.text
        # print(response_text)
        pattern = r'<div class="money-c available_money">(\d*\.\d*)</div>'
        balance = re.findall(pattern, response_text)[0]
        pattern = r'<div class="money-c"><span id="jifen">(\d*\.\d*)</span></div>'
        locked_amount = re.findall(pattern, response_text)[0]
        pattern = r'<div class="money-c">(\d*\.\d*)</div>'
        tomorrow_earnings = re.findall(pattern, response_text)[0]
        print(f'[账号{index + 1}] 账户余额：{balance} 锁定金额：{locked_amount} '
              f'明日收益：{tomorrow_earnings}')

    def sign_in(self):
        headers = self.headers
        index = self.index
        for _ in range(10):
            data = {
                'uid': '51590',
            }
            url = 'http://lses-lcae.ihuju.cn/index.php/Home/Index/ad_video_api.html'
            response = requests.post(url, headers=headers, data=data, )
            response_text = response.text
            if '今日已完成' in response_text:
                print(f'[账号{index + 1}] 今日已完成签到')
                return
            response_dict = response.json()
            # print(response.json())
            if response_dict.get('status') == 1:
                num = response_dict.get('num')
                print(f'[账号{index + 1}] 第{num}个视频观看成功')
                time.sleep(0.5)
                continue
            print(f'[账号{index + 1}] 视频观看失败 {response_dict}')

    # 提现
    def withdraw(self):
        headers = self.headers
        index = self.index
        ck = self.ck

        url = 'http://lses-lcae.ihuju.cn/index.php/Home/My/withdrawal.html'
        response = requests.get(url, headers=headers)
        response_text = response.text
        # print(response_text)
        pattern = r'class="jui_fc_red">(.*?)</a>'
        jui_fc_red = re.findall(pattern, response_text)[0]
        # print(jui_fc_red)
        pattern = r'<span id="money_num">(\d*\.\d*)</span>元'
        money_num = float(re.findall(pattern, response_text)[0])
        if '请前往设置您的支付宝账号' in jui_fc_red:
            print(
                f'[账号{index + 1}] 当前余额：{money_num}元 未设置提现的支付宝账号')
            return
        # print(money_num)
        if money_num < 10:
            print(
                f'[账号{index + 1}] 当前余额：{money_num}元 未达到最低提现金额')
            return
        data = {
            'price': f'{money_num}',
        }
        url = 'http://lses-lcae.ihuju.cn/index.php/Home/My/withdrawal.html'
        headers = {
            'Host': 'lses-lcae.ihuju.cn',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'X-Requested-With': 'XMLHttpRequest',
            'User-Agent': 'Mozilla/5.0 (Linux; Android 13; 22041211AC Build/TP1A.220624.014; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/115.0.5790.166 Mobile Safari/537.36  XiaoMi/MiuiBrowser/10.8.1 LT-APP/45/158/YM-RT/',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Origin': 'http://lses-lcae.ihuju.cn',
            'Referer': 'http://lses-lcae.ihuju.cn/index.php/Home/My/withdrawal.html',
            'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
            'Cookie': f'token={ck}',
        }
        response = requests.post(url, headers=headers, data=data, )
        response_dict = response.json()
        info = response_dict.get('info')
        print(f'[账号{index + 1}] 提现{money_num}元 提现结果：{info}')


def threading_task(func):
    # 创建线程池并设置最大线程数
    with concurrent.futures.ThreadPoolExecutor(
            max_workers=MAX_WORKERS) as executor:
        futures = []
        for index, ck in enumerate(ck_list):
            if not ck_signal_list[index]:
                continue
            task = ZhongFen(ck, index)
            task_func = getattr(task, func)
            future = executor.submit(task_func)
            futures.append(future)
        # 等待线程池中的所有任务完成
        concurrent.futures.wait(futures)


def threading_main():
    print('')
    print("============开始获取用户信息============")
    threading_task('get_infomation')
    print('')
    print("============开始观看10个视频广告签到============")
    threading_task('sign_in')
    print('')
    print("============开始提现============")
    threading_task('withdraw')
    print('')


def main():
    global ck_list
    global ck_signal_list

    get_env()
    ck_list = [x for x in ck_list if x.strip() != ""]
    if not ck_list:
        print('没有获取到账号！')
        return
    ck_count = len(ck_list)
    ck_signal_list = [True] * ck_count
    print(f'获取到{ck_count}个账号！')
    threading_main()


if __name__ == '__main__':
    main()
    sys.exit()
