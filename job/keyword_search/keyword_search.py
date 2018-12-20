# -*- coding:utf-8 -*-
import logging

from utils.logger import Logger

__author__ = 'zhoujifeng'
__date__ = '2018/12/20 15:00'
import os
import re
import time
from functools import reduce

from job.keyword_search.setting import SITES, KEYWORDS, RESULT_PATH, RESULT_FILENAME, NET_LOCATIONS, WAIT_TIME, HEADERS
from utils.CrawlerUtils import CrawlerUtils

logger = logging.getLogger('search')


def get_count_by_keywords(html, keywords):
    # 对每个关键词出现的次数依次累加
    count = reduce(lambda x, y: x + y, map(lambda x: len(re.findall(x, str(html))), keywords))
    return count


def in_spec_loc(loc, net_locations):
    """
    判断网页地址是否是需要爬取网站的域名
    :param loc: 网址
    :param net_locations:
    :return:
    """
    return True if True in list(map(lambda x: True if x in loc else False, net_locations)) else False


def save_result(url, title, keyword_num):
    with open(path, 'a', encoding='gb18030') as file:
        res = title[0].text + ',' + str(keyword_num) + ',' + url + '\n'
        logger.info('正在保存:[%s]' % (res.strip(),))
        file.write(res)


def dfs(url, depth):
    depth += 1
    if depth >= 4:
        return
    if 'http://' not in url:
        url = 'http://' + url
    if url in visited:
        logger.info('该网址已遍历:%s' % (url,))
        return
    html = CrawlerUtils.get_html(url, headers=HEADERS)
    if isinstance(html, int):
        logger.info('请求出错:[%s]' % (url,))
        return
    keyword_num = get_count_by_keywords(html, KEYWORDS)
    if keyword_num > 0:
        title = CrawlerUtils.get_tag(html, 'title')
        if len(title) == 0:
            title = '无标题'
        save_result(url, title, keyword_num)
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
        list(map(lambda x: dfs(x, depth) if in_spec_loc(x, NET_LOCATIONS) else False, urls))
    except Exception as e:
        logger.error(e)


def main():
    for url in SITES:
        dfs(url, 0)


if __name__ == '__main__':
    Logger()
    visited = set()
    path = os.path.join(RESULT_PATH, RESULT_FILENAME)
    if not os.path.exists(RESULT_PATH):
        os.makedirs(RESULT_PATH)
        with open(path, 'a', encoding='gb18030') as file:
            file.write('标题,关键字数量,网址\n')
    main()
