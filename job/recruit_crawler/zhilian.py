# -*- coding:utf-8 -*-
import io
import json
import logging
import random
import sys
import time

import pandas as pd
import requests


from job.recruit_crawler.setting import DB_CONNS,TABLE_CONFIG, ZHILIAN_API_URL, ZHILIAN_CONFIG
from utils.logger import Logger

sys.getdefaultencoding()
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='gbk')

logger = logging.getLogger('crawler.zhilian')


def get_params_by_url(url):
    """
    根据url解析为params字典
    :param url:
    :return:
    """
    from urllib import parse
    params_url = parse.urlsplit(url).query
    params = dict(map(lambda x: x.split('='), params_url.split('&')))
    return params


def get_headers():
    """
    随机返回列表中的User-Agent
    :return:
    """
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
    headers = dict()
    headers['User-Agent'] = user_agents[random.randint(0, len(user_agents) - 1)]
    return headers


def get_json(url, headers=None, params=None, **kwargs):
    """
    请求url返回json对象
    :param url:
    :param headers:
    :param params:
    :param kwargs:
    :return:
    """
    req = requests.get(url, headers=headers, params=params, **kwargs)
    req.encoding = req.apparent_encoding
    try:
        req.raise_for_status()
        data = json.loads(req.content)
    except Exception as e:
        logging.error(e)
        data = dict()

    return data


def get_number(keyword, url, start=0, page_size=60, city_id=None):
    """
    请求接口获取职位信息
    :param keyword:
    :param url:
    :param start:
    :param page_size:
    :param city_id:
    :return:
    """
    params = get_params_by_url(url)
    while True:
        params['start'] = start
        params['pageSize'] = page_size
        params['kw'] = keyword
        if city_id is not None:
            params['cityId'] = city_id
        headers = get_headers()
        data = get_json(ZHILIAN_API_URL, params=params, headers=headers)
        start += page_size
        for res in data['data']['results']:
            logo = res['companyLogo'].strip()
            if len(logo) != 0 and 'http' not in logo:
                logo = str('http:') + logo
            yield res['positionURL'].strip(), res['number'].strip(), res['company']['number'].strip(), \
                  res['jobType']['items'][0]['name'].strip(), logo.strip()
        break


def get_html(url, headers=None, params=None):
    """
    请求网页，获取页面
    :param url:
    :param headers:
    :param params:
    :return:
    """
    import requests
    import logging

    req = requests.get(url, headers=headers, params=params)
    req.encoding = req.apparent_encoding
    try:
        req.raise_for_status()
        return req.text
    except Exception as e:
        logging.error(e)
        return ''


def get_sql_by_list(table_name, columns, values):
    """
    根据values生成sql插入语句
    :param table_name:
    :param columns:
    :param values:
    :return:
    """
    if len(columns) != len(values):
        return None, None
    sql = 'insert into {}(%s) values(%s);'.format(table_name)

    sql = sql % ('{}' * len(columns), '%s' * len(columns))
    sql = sql.replace(r'}{', '},{').replace(r's%', 's,%')
    sql = sql.format(*columns)

    return sql, values


def get_tag(text, selector):
    """
    解析网页
    :param text:
    :param selector:
    :return:
    """
    from bs4 import BeautifulSoup

    bs = BeautifulSoup(text, 'lxml')
    res = bs.select(selector)
    return res


def deal(data):
    """
    解析网页获取需要数据
    :param data:
    :return:
    """
    url, pos_code, com_code, work_nature, com_log_url = data
    html = get_html(url)
    res = dict()
    res['pos_code'] = pos_code
    res['com_code'] = com_code
    res['work_nature'] = work_nature
    res['pos_name'] = get_tag(html, '.new-info h1')[0].text.strip()
    res['address'] = get_tag(html, 'p.add-txt')[0].text.strip()
    res['salary'] = get_tag(html, '.info-money strong')[0].text.strip()
    res['city'], res['exp_require'], res['degree'], res['recruit_num'] = list(
        map(lambda x: x.text, get_tag(html, '.info-three span')))
    res['status'] = 7
    res['description'] = get_tag(html, '.pos-ul')[0].text.strip()

    res['code'] = com_code
    res['name'] = get_tag(html, '.promulgator-info h3')[0].text.strip('\n').strip(r'\n').strip()
    res['scale_num'] = get_tag(html, '.icon-promulgator-link')[0].next_sibling.text.strip()
    res['sub_industry'] = get_tag(html, '.icon-promulgator-person')[0].next_sibling.text.strip()
    res['company_nature'] = get_tag(html, '.icon-promulgator-type')[0].next_sibling.text.strip()
    res['official_website'] = get_tag(html, '.icon-promulgator-url')[0].next_sibling.text.strip()
    res['com_address'] = get_tag(html, '.icon-promulgator-addres')[0].next_sibling.next_sibling.text.strip()
    res['logo'] = com_log_url
    res['introduce'] = get_tag(html, '.intro-content')[0].text.strip()
    try:
        logger.info('pos_url:[%s]' % (url,))
    except UnicodeEncodeError:
        pass
    time.sleep(2)
    return res


def deal_degree(degree):
    """
    处理学历
    :param degree:
    :return:
    """
    if degree == '学历不限':
        return 0
    elif '专' in degree:
        return 1
    elif '本' in degree:
        return 2
    elif degree == '硕士':
        return 3
    elif degree == '博士':
        return 4
    else:
        return -1


def deal_exp_require(exp_require):
    """
    处理经验字段
    :param exp_require:
    :return:
    """
    if exp_require == '经验不限' or exp_require == '无经验':
        return 0
    elif exp_require == '应届生':
        return 1
    elif exp_require == '1年以内' or exp_require == '1年以下':
        return 2
    elif exp_require == '1-3年':
        return 3
    elif exp_require == '3-5年':
        return 4
    elif exp_require == '5-10年':
        return 6
    elif exp_require == '10年以上':
        return 7
    else:
        return 9


def deal_salary(salary_list):
    """
    处理最高最低薪资
    :param salary_list:
    :return:
    """
    def __deal(salary):
        """
        对薪资进行单个处理
        :param salary:
        :return:
        """
        old_salary = salary
        if '元' in salary:
            salary = salary.split('元')[0]

        min_salary = 0
        max_salary = 0
        if '-' in salary:
            min_salary = salary.split('-')[0]
            max_salary = salary.split('-')[1]
        elif salary.endswith('以上'):
            min_salary = salary.split('以上')[0]
            max_salary = 0
        elif salary.endswith('以下'):
            max_salary = 0
            min_salary = salary.split('以下')[0]
        elif '面议' in salary:
            max_salary = 0
            min_salary = 0

        return {
            'salary': old_salary,
            'max_salary': max_salary,
            'min_salary': min_salary
        }

    df = pd.DataFrame(list(map(lambda x: __deal(x), list(set(salary_list)))))
    return df


def to_db(data, table_name, conn):
    """
    将数据保存到数据库
    :param data:
    :param table_name:
    :param conn:
    :return:
    """
    data = data.reset_index()
    sql, values = get_sql_by_list(table_name, tuple(data['index']),
                                  tuple(data[list(data.columns)[-1]].astype('str')))

    logger.info(sql)
    cur = conn.cursor()
    try:
        cur.execute(sql, values)
    except Exception as e:
        logger.error(e)
    conn.commit()
    return 0


def table_exists(table_name, conn):
    """
    判断表是否存在
    :param table_name:
    :param conn:
    :return:
    """
    import re
    cur = conn.cursor()
    sql = "show tables;"
    cur.execute(sql)
    tables = [cur.fetchall()]
    table_list = re.findall('(\'.*?\')', str(tables))
    table_list = [re.sub("'", '', each) for each in table_list]

    if table_name in table_list:
        return True  # 存在返回True
    else:
        return False  # 不存在返回Fals


def execute_sql(sql, conn):
    cur = conn.cursor()
    cur.execute(sql)
    res = cur.fetchall()
    return res


def save_pos(df: pd.DataFrame, conn, pos_table_name):
    """
    清洗数据，将清洗之后的数据保存数据到职位表
    :param df:
    :param conn:
    :param pos_table_name:
    :return:
    """
    logger.info('开始保存职位数据')
    tmp_df = df.copy()  # type:pd.DataFrame
    if not table_exists(pos_table_name, conn):
        execute_sql(TABLE_CONFIG[pos_table_name], conn)
    pos_sql = "SELECT pos_code FROM %s WHERE pos_code IN %s" % (
        pos_table_name, str('(') + str(list(tmp_df['pos_code']))[1:-1] + str(');'))
    df_pos_code = pd.read_sql(pos_sql, conn)
    if len(df_pos_code) != 0:
        tmp_df = tmp_df[~tmp_df['pos_code'].isin(list(df_pos_code['pos_code']))]
        tmp_df.merge(df_pos_code, how='right', on=['pos_code'])
        if len(tmp_df) == 0:
            logger.info('没有需要保存的数据！')
            return

    tmp_df['exp_require'] = tmp_df['exp_require'].apply(deal_exp_require)
    tmp_df['degree'] = tmp_df['degree'].apply(deal_degree)
    salary_df = deal_salary(tmp_df['salary'])
    tmp_df = tmp_df.merge(salary_df, how='left', on='salary')
    tmp_df['city'] = tmp_df['city'].apply(lambda x: x.split('-')[0])
    tmp_df.drop_duplicates(inplace=True)
    tmp_df['source'] = 2
    tmp_df['recruit_num'] = tmp_df['recruit_num'].apply(lambda x: x[1:-1])
    tmp_df.apply(lambda x: to_db(x, pos_table_name, conn), axis=1)
    del tmp_df
    logger.info('职位数据保存完成')


def save_com(df: pd.DataFrame, conn, com_table_name):
    """
    清洗数据，将清洗之后的数据保存数据到公司表
    :param df:
    :param conn:
    :param com_table_name:
    :return:
    """
    logger.info('开始保存公司数据')
    tmp_df = df.copy()
    if not table_exists(com_table_name, conn):
        execute_sql(TABLE_CONFIG[com_table_name], conn)
    pos_sql = "SELECT code FROM %s WHERE code IN %s" % (
        com_table_name, str('(') + str(list(tmp_df['code']))[1:-1] + str(');'))
    df_pos_code = pd.read_sql(pos_sql, conn)
    if len(df_pos_code) != 0:
        tmp_df = tmp_df[~tmp_df['code'].isin(list(df_pos_code['code']))]
        tmp_df.merge(df_pos_code, how='right', on=['code'])
        if len(tmp_df) == 0:
            logger.info('没有需要保存的数据！')
            return

    tmp_df = tmp_df.drop_duplicates().copy()
    tmp_df.apply(lambda x: to_db(x, com_table_name, conn), axis=1)
    del tmp_df
    logger.info('公司数据保存完成')


def main():
    """
    从获取职位信息,并进入职位网址爬取职位信息，清洗并保存到数据库
    :return:
    """
    Logger()
    keyword = ZHILIAN_CONFIG['keyword']
    url = ZHILIAN_CONFIG['url']
    start = ZHILIAN_CONFIG['start']
    page_size = ZHILIAN_CONFIG['page_size']

    while True:
        number_generator = get_number(keyword, url, start=start, page_size=page_size)
        logger.info('开始获取[%d-%d]的数据' % (start, start + page_size))
        start += page_size

        df = pd.DataFrame(list(map(lambda x: deal(x), number_generator)))
        if len(df) == 0:
            logger.info('-*-*-*-*-*-*-*-*-完成-*-*-*-*-*-*-*-*-')
            break
        logger.info('开始保存到数据库')
        conn = DB_CONNS['default']()
        pos_col = ['pos_code',
                   'com_code',
                   'work_nature',
                   'pos_name',
                   'address',
                   'salary',
                   'city',
                   'status',
                   'description',
                   'exp_require',
                   'degree',
                   'recruit_num']
        com_col = [
            'code',
            'name',
            'scale_num',
            'sub_industry',
            'company_nature',
            'official_website',
            'com_address',
            'logo',
            'introduce',
        ]
        save_pos(df.loc[:, pos_col], conn, 'xb_company_position_1')
        save_com(df.loc[:, com_col].rename(columns={'com_address': 'address'}), conn, 'xb_company_1')
        del df
        conn.close()
        logger.info('入库完成')


if __name__ == '__main__':
    # 程序入口
    main()
