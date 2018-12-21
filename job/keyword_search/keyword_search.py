# -*- coding:utf-8 -*-
import logging
import os
import re
import time
from functools import reduce

import requests

from job.keyword_search.setting import SITES, KEYWORDS, RESULT_PATH, RESULT_FILENAME, NET_LOCATIONS, WAIT_TIME, HEADERS
from utils.CrawlerUtils import CrawlerUtils
from utils.logger import Logger

logger = logging.getLogger('search')


class KeywordSearch:

    def __init__(self):
        Logger()
        self.visited = set()
        self.path = os.path.join(RESULT_PATH, RESULT_FILENAME)
        if not os.path.exists(RESULT_PATH):
            os.makedirs(RESULT_PATH)
            with open(self.path, 'a', encoding='gb18030') as file:
                file.write('标题,关键字数量,网址\n')

    def get_count_by_keywords(self, html, keywords):
        # 对每个关键词出现的次数依次累加
        count = reduce(lambda x, y: x + y, map(lambda x: len(re.findall(x, str(html))), keywords))
        return count

    def in_spec_loc(self, loc, net_locations):
        """
        判断网页地址是否是需要爬取网站的域名
        :param loc: 网址
        :param net_locations:
        :return:
        """
        return True if True in list(map(lambda x: True if x in loc else False, net_locations)) else False

    def save_result(self, url, title, keyword_num):
        with open(self.path, 'a', encoding='gb18030') as file:
            res = title[0].text + ',' + str(keyword_num) + ',' + url + '\n'
            logger.info('正在保存:[%s]' % (res.strip(),))
            file.write(res)

    def get_html(self, url, headers=None, params=None):
        req = requests.get(url, headers=headers, params=params)
        req.encoding = req.apparent_encoding
        try:
            req.raise_for_status()
            return req.text
        except Exception as e:
            logging.error(e)
            return req.status_code

    def dfs(self, url, depth):
        depth += 1
        if depth >= 4:
            return
        if 'http://' not in url:
            url = 'http://' + url
        if url in self.visited:
            logger.info('该网址已遍历:%s' % (url,))
            return
        html = self.get_html(url, headers=HEADERS)
        if isinstance(html, int):
            logger.info('请求出错:[%s],错误代码为:[%d]' % (url, html))
            return
        self.visited.add(url)
        logger.info('当前处理深度为:[%d]\t正在处理:[%s]' % (depth, url))
        keyword_num = self.get_count_by_keywords(html, KEYWORDS)
        if keyword_num > 0:
            title = CrawlerUtils.get_tag(html, 'title')
            if len(title) == 0:
                title = '无标题'
            self.save_result(url, title, keyword_num)
        a_tags = CrawlerUtils.get_tag(html, 'a')
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
        主函数
        :return:
        """
        for url in SITES:
            self.dfs(url, 0)


if __name__ == '__main__':
    KeywordSearch().run()
