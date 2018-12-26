# -*- coding:utf-8 -*-
import io
import logging
import os
import random
import string
import sys
import time

from selenium import webdriver
from selenium.webdriver.common.keys import Keys

from short_setting import SHORT_CONFIG, API_SHORT, \
    FILE_PATH, FILE_NAME, DOUBAN_USERNAME, DOUBAN_PASSWORD
from utils.logger import Logger

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='gb18030')  # 改变标准输出的默认编码
logger = logging.getLogger('douban')


def get_headers(str_headers):
    def __id_generator(size=11, chars=string.ascii_uppercase + string.digits):
        return ''.join(random.choice(chars) for _ in range(size))

    user_agents = [
        'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_8; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50',
        'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50',
        'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:38.0) Gecko/20100101 Firefox/38.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_0) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11',
        'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; 360SE)',
        'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Avant Browser)',
        'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; SE 2.X MetaSr 1.0; SE 2.X MetaSr 1.0; .NET CLR 2.0.50727; SE 2.X MetaSr 1.0)',
        'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; The World)',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_0) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11',
        'Opera/9.80 (Windows NT 6.1; U; en) Presto/2.8.131 Version/11.11',
        'Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; en) Presto/2.8.131 Version/11.11',
    ]

    headers = dict(map(lambda x: x.strip(' ').split(':', 1), str_headers.strip().split('\n')))

    headers['User-Agent'] = user_agents[random.randint(0, len(user_agents) - 1)]
    headers['Cookie'] = 'bid=' + __id_generator() + headers['Cookie'][15:]
    return headers


def get_html(url):
    logger.info('正在获取网页:%s' % (url.strip(),))
    browser.get(url)  # 需要打开的网址
    html = browser.page_source

    return html


def login():
    chromedriver = "C:/Program Files (x86)/Google/Chrome/Application/chromedriver.exe"
    os.environ["webdriver.chrome.driver"] = chromedriver
    option = webdriver.ChromeOptions()
    option.add_argument('headless')
    option.add_argument('--proxy-server=http://202.20.16.82:10152')
    browser = webdriver.Chrome(chromedriver)
    # browser = webdriver.Chrome(chromedriver, chrome_options=option)
    browser.get('https://www.douban.com/accounts/login?source=movie')  # 需要打开的网址
    user = browser.find_element_by_xpath('//*[@id="email"]')  # 审查元素username的id
    user.send_keys(DOUBAN_USERNAME)  # 输入账号
    password = browser.find_element_by_xpath('//*[@id="password"]')  # 审查元素password的name
    password.send_keys(DOUBAN_PASSWORD)  # 输入密码
    password.send_keys(Keys.RETURN)  # 实现自动点击登陆
    logger.info('登陆成功')
    return browser


def get_tag(text, selector):
    from bs4 import BeautifulSoup
    bs = BeautifulSoup(text, 'lxml')
    res = bs.select(selector)
    return res


def deal_by_process(start):
    html = get_html(API_SHORT % (start,))
    comment_tags = get_tag(html, 'div.comment')
    messages = []
    for comment in comment_tags:
        res = {
            'username': comment.select('span.comment-info a')[0].text.replace('\r', '').replace('\n', ''),
            # 'rating': comment.select('span.rating')[0].attrs['title'].replace('\r', '').replace('\n', ''),
            'votes': comment.select('span.votes')[0].text.replace('\r', '').replace('\n', ''),
            'comment_time': comment.select('span.comment-time ')[0].attrs['title'].replace('\r', '').replace('\n', ''),
            'message': comment.select('.short')[0].text.strip().replace('\r', '').replace('\n', ''),
        }
        messages.append(res)

    return messages


def to_csv(data):
    for short in data:
        res = short['username'] + ',' + short['votes'] + ',' + short['comment_time'] + ',' + short['message'] + '\n'
        logger.info('正在保存:%s', (res,))
        file.write(res)


def main():
    Logger()

    for start in range(SHORT_CONFIG['start'], SHORT_CONFIG['short_num'], 20):
        data = deal_by_process(start)
        to_csv(data)
        time.sleep(1)
    # pool = multiprocessing.Pool(processes=PROCESSES_NUM)
    # for start in range(SHORT_CONFIG['start'], SHORT_CONFIG['short_num'], 20):
    #     pool.apply_async(deal_by_process, (start,), callback=to_csv)
    # pool.close()
    # pool.join()

    logger.info('爬取完成')


if __name__ == '__main__':
    if not os.path.exists(FILE_PATH):
        os.makedirs(FILE_PATH)
    file = open(os.path.join(FILE_PATH, FILE_NAME), 'a', encoding='gb18030', errors='ignore')
    browser = login()
    main()
    file.close()
