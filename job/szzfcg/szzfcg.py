# -*- coding:utf-8 -*-
from utils.CrawlerUtils import CrawlerUtils

__author__ = 'zhoujifeng'
__date__ = '2019/1/17 10:13'
URL = 'http://www.szzfcg.cn/portal/topicView.do?method=view&id=2719966'


def main():
    headers = {
        'User-Agent': CrawlerUtils.get_user_agent()
    }
    html = CrawlerUtils.get_html(url=URL, headers=headers)
    tr_tags = CrawlerUtils.get_tag(html, 'tbody.tableBody tr')
    for i in tr_tags:
        content = i.contents
        print(content[3].text.strip())
        print(content[5].text.strip())
        print(content[9].text.strip())
        print('======================================================================')


if __name__ == '__main__':
    main()
