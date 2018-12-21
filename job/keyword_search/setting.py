# -*- coding:utf-8 -*-
import os

SITES = [
    'http://sgim.sztu.edu.cn/',
    'http://www.sztu.edu.cn',
    'http://english.sztu.edu.cn',
    'http://www.sztu.edu.cn/mobile',
]
# 设置需要保存的位置，注意\要换成/或者\\


RESULT_PATH = '.result'
RESULT_FILENAME = 'urls.csv'

# 设置要抓取的网站范围
NET_LOCATIONS = ['sztu.edu.cn']

# 需要抓取到第几层网页
MAX_DEPTH = 4

# 设置的关键字或关键词列表
KEYWORDS = [u'截止2025年']

# 抓取网页前等待多少秒
WAIT_TIME = 1

HEADERS = {
    'Connection': 'keep-alive',
    'Pragma': 'no-cache',
    'Cache-Control': 'no-cache',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.139 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-CN,zh;q=0.9',
}
