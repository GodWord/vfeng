# -*- coding:utf-8 -*-

MOVIE_URL = 'https://movie.douban.com/subject/27110296/'
FILE_PATH = './'  # 结果文件路径
FILE_NAME = 'result.csv'  # 结果文件名称

SHORT_CONFIG = {
    'start': 0,  # 短评从第几条开始获取
    'short_num': 2000  # 爬取短评条数
}
DOUBAN_USERNAME = 'z1914007838@outlook.com'
DOUBAN_PASSWORD = 'zjf197378'
API_SHORT = """
https://movie.douban.com/subject/27110296/comments?start=%d&limit=20&sort=new_score&status=P&percent_type=
"""
HEADER = """
Accept:text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8
Accept-Language:zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7
Cache-Control:no-cache
Connection:keep-alive
Cookie:bid=_YiWD7Jayk0; douban-fav-remind=1; ll="108309"; _vwo_uuid_v2=D52D6B197AA63FDA49463045DEBB06C69|1030a8d0d2199dd0991d94e1155ca1e2; __yadk_uid=BhfX9dykHmfyTLt8DSbmaNJrUsRx1LSM; gr_user_id=52719b10-0c5a-470e-843c-7650c88cf1f5; viewed="5977150_30304849_3995526"; _pk_ref.100001.4cf6=%5B%22%22%2C%22%22%2C1544183032%2C%22https%3A%2F%2Fwww.google.com.sg%2F%22%5D; _pk_ses.100001.4cf6=*; __utma=30149280.598247501.1528771024.1544013668.1544183032.11; __utmb=30149280.0.10.1544183032; __utmc=30149280; __utmz=30149280.1544183032.11.8.utmcsr=google|utmccn=(organic)|utmcmd=organic|utmctr=(not%20provided); __utma=223695111.1595282729.1534683203.1544013668.1544183032.4; __utmb=223695111.0.10.1544183032; __utmc=223695111; __utmz=223695111.1544183032.4.2.utmcsr=google|utmccn=(organic)|utmcmd=organic|utmctr=(not%20provided); _pk_id.100001.4cf6=a3a9da58c92d9e62.1534683203.4.1544183041.1544015609.; ap_v=0,6.0
Host:movie.douban.com
Pragma:no-cache
Referer:https://movie.douban.com/explore
Upgrade-Insecure-Requests:1
User-Agent:Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36
"""
