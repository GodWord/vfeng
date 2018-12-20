# -*- coding: utf-8 -*-

import re, time
from urllib import parse
from urllib import request
import random
import urllib
from bs4 import BeautifulSoup


# 根据网址请求网页内容
def getContent(url):
    req = request.Request(url, headers={
        'Connection': 'keep-alive',
        'Pragma': 'no-cache',
        'Cache-Control': 'no-cache',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.139 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9',
    })

    # 这里写的有问题，后面要改一下。
    # proxies=['219.141.153.11:8080','39.137.69.6:80','39.137.69.10:80','39.137.77.66:80','39.137.77.66:8080']
    # proxy= random.choice(proxies)
    #
    # proxy_support = urllib.request.ProxyHandler({'http':proxy})
    # opener = urllib.request.build_opener(proxy_support)
    # urllib.request.install_opener(opener)
    #
    # response = urllib.request.urlopen(url)
    # # html= response.read()

    time.sleep(wait_time)

    # return html
    return request.urlopen(req).read().decode('utf-8')


# 获取网站标题
def getTitle(html):
    # 初始化分割器
    soup = BeautifulSoup(html, "html.parser")

    titles = soup.find_all(name='title')
    if len(titles) > 0:
        return titles[0].text.replace(',', '.')
    return 'Untitled'


# 获取网页中的所有超链接
def getLinkers(html):
    # 初始化分割器
    soup = BeautifulSoup(html, "html.parser")

    # 寻找并保存所有链接
    links = []
    for link in soup.find_all(name='a'):
        href = link.get('href')
        if href is not None:
            links.append(href.strip())

    return links


# 统计其中包含了多少个关键词
def CountNumberOfKeywords(html):
    count = 0

    # 对每个关键词出现的次数依次累加
    for key_word in key_words:
        count += len(re.findall(key_word, html))

    return count


# 判断网页地址是否是我们想抓取的网站的域名
def in_spec_loc(loc, net_locations):
    # 依次判断
    for net_loc in net_locations:
        # 只要在我们指定的列表中出现，就表示是我们想要抓取的网址
        if loc.find(net_loc) != -1:
            return True
    return False


# 深度优先搜索
def dfs(url, depth):
    if depth > max_depth:
        return

    info = parse.urlparse(url)

    if not in_spec_loc(info.netloc, net_locations):
        return

        # 检测网站是否已经被遍历过了
    if url in visited:
        return

    visited[url] = True

    try:
        # 尝试抓取这个网页内容
        html = getContent(url)
    except Exception as e:

        count = -1
        title = str(e).replace(',', '.')
        links = []
    else:
        # 如果抓取成功，那么就

        # 获取网站标题
        title = getTitle(html)

        # 获取网页中关键字的数量
        count = CountNumberOfKeywords(html)

        # 获取网页中的所有超链接
        links = getLinkers(html)


    finally:
        # 最后，我们把抓取到的信息更新到CSV中
        csv = open(save_filename, 'a')
        csv.write(url + ',' + title + ',' + str(count) + '\n')
        csv.close()

        print("已经抓取网页数:", len(visited), "当前正在抓取:", url, title)

        # 然后对于其中的每个超链接，依次访问，此时depth+1表示深度加了一个
        for link in links:
            dfs(parse.urljoin(url, link), depth + 1)


# 抓取的起始网址
root_list = ['http://www.sztu.edu.cn',
             'http://english.sztu.edu.cn',
             'http://www.sztu.edu.cn/mobile',
             ]

# 设置需要保存的位置，注意\要换成/或者\\
save_filename = 'result.csv'

# 设置要抓取的网站范围
net_locations = ['sztu.edu.cn']

# 需要抓取到第几层网页
max_depth = 4

# 设置的关键字或关键词列表
key_words = [u'截至2025年']

# 抓取网页前等待多少秒
wait_time = 0.2

# 创建一个用来保存的csv文件
csv = open(save_filename, 'w')
csv.write('网址,标题,关键字数量\n')
csv.close()

# 初始化一个字典，用来保存哪些网址已经被抓取过了
visited = {}

# 从每一个指定的根网址出发，进行深度遍历
for root_link in root_list:
    # 采用的遍历方式是dfs遍历
    dfs(root_link, 1)
