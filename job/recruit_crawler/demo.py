# -*- coding:utf-8 -*-


'http://company.zhaopin.com/CompanyLogo/20150701/8804C020A0F343B18EEA6E2B186F8819.jpg'
from job.recruit_crawler.zhilian import get_html, get_headers

if __name__ == '__main__':
    headers = get_headers()

    url = 'http://www.metel.cn/loginIn'
    html = get_html(url, headers=headers)
    print(html)
