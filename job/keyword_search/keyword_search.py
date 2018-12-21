# -*- coding:utf-8 -*-
import logging
import os
import re
import time
from functools import reduce

import requests

from job.keyword_search.setting import SITES, KEYWORDS, RESULT_PATH, RESULT_FILENAME, NET_LOCATIONS, WAIT_TIME, HEADERS
from job.keyword_search.utils.logger import Logger

logger = logging.getLogger('search')


class KeywordSearch:

    def __init__(self):
        """
        初始化程序
        """
        Logger()
        self.visited = set()
        self.path = os.path.join(RESULT_PATH, RESULT_FILENAME)
        if not os.path.exists(RESULT_PATH):
            os.makedirs(RESULT_PATH)
            with open(self.path, 'a', encoding='gb18030') as file:
                file.write('标题,关键字数量,网址\n')

    def get_count_by_keywords(self, html, keywords):
        """
        对每个关键词出现的次数统计并累加
        :param html:
        :param keywords:
        :return:
        """
        count = reduce(lambda x, y: x + y, map(lambda x: len(re.findall(x, str(html))), keywords))
        return count

    def in_spec_loc(self, loc, net_locations):
        """
        判断网页地址是否是需要爬取网站的域名
        :param loc: 网址
        :param net_locations:网站域名抓取范围
        :return:True or False
        """
        return True if True in list(map(lambda x: True if x in loc else False, net_locations)) else False

    def save_result(self, url, title, keyword_num):
        """
        保存结果文件
        :param url:路径
        :param title:网页标题
        :param keyword_num:关键词数量
        :return:
        """
        with open(self.path, 'a', encoding='gb18030') as file:
            res = title[0].text + ',' + str(keyword_num) + ',' + url + '\n'
            logger.info('正在保存:[%s]' % (res.strip(),))
            file.write(res)

    def get_html(self, url, headers=None, params=None):
        """
        请求网页，获取HTML
        :param url: 请求的网址
        :param headers: 模拟请求头信息
        :param params: 模拟参数
        :return: req.text or error code
        """
        req = requests.get(url, headers=headers, params=params)
        req.encoding = req.apparent_encoding
        try:
            req.raise_for_status()
            return req.text
        except Exception as e:
            logging.error(e)
            return req.status_code

    def get_tag(self, text, selector):
        from bs4 import BeautifulSoup
        bs = BeautifulSoup(text, 'lxml')
        res = bs.select(selector)
        return res

    def dfs(self, url, depth):
        """
        对网址进行请求，处理，判断
        :param url:需要处理的网址
        :param depth:处理深度
        :return:
        """
        depth += 1
        if depth >= 4:
            return
        if 'http://' not in url:
            url = 'http://' + url
        if url in self.visited:
            logger.info('该网址已遍历:%s' % (url,))
            return

        logger.info('当前处理深度为:[%d]\t正在处理:[%s]' % (depth, url))
        html = self.get_html(url, headers=HEADERS)
        if isinstance(html, int):
            logger.info('请求出错:[%s],错误代码为:[%d]' % (url, html))
            return
        self.visited.add(url)
        keyword_num = self.get_count_by_keywords(html, KEYWORDS)
        if keyword_num > 0:
            title = self.get_tag(html, 'title')
            if len(title) == 0:
                title = '无标题'
            self.save_result(url, title, keyword_num)
        a_tags = self.get_tag(html, 'a')
        if len(a_tags) == 0:
            return
        urls = list()
        try:
            urls = list(map(lambda x: x.attrs['href'].strip() if 'href' in list(x.attrs) else '', a_tags))
        except Exception as e:
            logger.error(e)
        time.sleep(WAIT_TIME)
        try:
            list(map(lambda x: self.dfs(x, depth) if self.in_spec_loc(x, NET_LOCATIONS) else False, urls))
        except Exception as e:
            logger.error(e)

    def run(self):
        """
        主函数，依次需要处理的站点
        :return:
        """
        for url in SITES:
            self.dfs(url, 0)


if __name__ == '__main__':
    KeywordSearch().run()
