# -*- coding:utf-8 -*-
import pymysql


create_sql_to_xb_company_position_1 = """
CREATE TABLE `xb_company_position_1` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '主键id',
  `com_code` varchar(64) DEFAULT NULL COMMENT '企业编号',
  `pos_code` varchar(64) DEFAULT NULL COMMENT '职位编号',
  `pos_name` varchar(50) DEFAULT NULL COMMENT '职位名称',
  `status` char(1) DEFAULT '1' COMMENT '职位状态（0=下线，1=上线，2=未发布，3=已删除，7=网络爬取）',
  `salary` varchar(30) DEFAULT NULL COMMENT '工资',
  `min_salary` int(10) DEFAULT '0' COMMENT '薪资下限',
  `max_salary` int(10) DEFAULT '0' COMMENT '薪资上限',
  `degree` char(1) DEFAULT '0' COMMENT '最低学历（0=学历不限，1=专科，2=本科，3=硕士，4=博士）',
  `address` varchar(255) DEFAULT NULL COMMENT '工作地点',
  `city` varchar(100) DEFAULT NULL COMMENT '坐标城市',
  `description` TEXT DEFAULT NULL COMMENT '岗位描述',
  `job_requirements` TEXT DEFAULT NULL COMMENT '任职要求',
  `work_nature` varchar(20) DEFAULT NULL COMMENT '工作性质',
  `recruit_num` smallint(5) DEFAULT NULL COMMENT '招聘人数',
  `exp_require` char(1) DEFAULT NULL COMMENT '经验要求：0=经验不限，1=应届生，2=1年以内，3=1-3年，4=3-5年，6=5-10年，7=10年以上',
  `source` int(1) DEFAULT '0' COMMENT '数据来源(0-系统录入，1-51job)',
  `public_date` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `industry_code` int(4) DEFAULT NULL COMMENT '行业编号(二级编号）',
  `if_school` int(1) NOT NULL DEFAULT '0' COMMENT '是否校招职位（0-非校招；1-校招）',
  `hotpos` int(1) DEFAULT '0' COMMENT '是否热招岗位：0=否；1=是',
  `update_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `create_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `pos_code_index` (`pos_code`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=117053 DEFAULT CHARSET=utf8 COMMENT='企业职位信息';
"""

create_sql_to_xb_company_1 = """
CREATE TABLE `xb_company_1` (
  `code` varchar(64) NOT NULL COMMENT '企业编码',
  `name` varchar(32) DEFAULT NULL COMMENT '企业名称',
  `short_name` varchar(30) DEFAULT NULL COMMENT '公司简称',
  `scale_num` varchar(11) DEFAULT NULL COMMENT '规模人数',
  `sub_industry` varchar(25) DEFAULT NULL COMMENT '所属行业（存放行业编号一级编号）',
  `company_nature` varchar(25) DEFAULT NULL COMMENT '公司性质',
  `official_website` varchar(100) DEFAULT NULL COMMENT '企业官网',
  `status` char(1) DEFAULT '1' COMMENT '企业状态(0=禁用，1=启用)',
  `phone` varchar(20) DEFAULT NULL COMMENT '联系电话（座机）',
  `mobile_phone` varchar(20) DEFAULT NULL COMMENT '手机号码',
  `logo` varchar(800) DEFAULT 'http://xiaobaijob.com/res/img/7974354903424c85aec99526f57a3dd4.png' COMMENT '企业LOGO',
  `email` varchar(50) DEFAULT NULL COMMENT '企业邮箱',
  `address` varchar(50) DEFAULT NULL COMMENT '企业地址',
  `introduce` varchar(5000) DEFAULT NULL COMMENT '企业介绍',
  `business_license` varchar(100) DEFAULT NULL COMMENT '营业执照',
  `register_status` char(1) DEFAULT '1' COMMENT '注册状态（1=邮箱注册；2=邮箱验证；3=完善资料1；4=完善资料2；5=完善资料3；6=等待审核；7=审核通过；8=审核不通过）',
  `npass_reason` varchar(50) DEFAULT NULL COMMENT '审核不通过的原因',
  `activation_code` varchar(64) DEFAULT NULL COMMENT '邮箱激活码',
  `activation_time` timestamp NULL DEFAULT NULL COMMENT '激活码获取时间',
  `city` varchar(10) DEFAULT NULL COMMENT '所在城市',
  `hr_website` varchar(1024) DEFAULT NULL COMMENT '招聘官网(网申)',
  `school_recruit_website` varchar(1024) DEFAULT NULL COMMENT '校招官网',
  `hr_email` varchar(50) DEFAULT NULL COMMENT 'HR邮箱',
  `source` char(50) DEFAULT '0' COMMENT '0-为系统添加、1-为51job爬取',
  `financing_phase` int(1) DEFAULT '1' COMMENT '融资阶段（1=未融资；2=天使轮；3=A轮；4=B轮；5=C轮；6=D轮；7=上市公司；8=不需要融资）',
  `light_word` varchar(60) DEFAULT NULL COMMENT '一句话点亮',
  `company_label` varchar(100) DEFAULT NULL COMMENT '公司标签',
  `famouscom` int(1) DEFAULT '0' COMMENT '是否H5微信活动页面名企（0=否；1=是）',
  `slogen` varchar(64) DEFAULT NULL COMMENT '一句话介绍公司',
  `if_start_mnms` tinyint(1) DEFAULT '0' COMMENT '是否开启模拟面试：0=否，1=是',
  `create_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `new_email` varchar(50) DEFAULT NULL COMMENT '新登陆邮箱',
  `new_email_code` varchar(64) DEFAULT NULL COMMENT '修改登陆邮箱验证码',
  `new_email_time` timestamp NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT '修改登录邮箱提交验证时间',
  PRIMARY KEY (`code`),
  UNIQUE KEY `index_activation_code` (`activation_code`) USING BTREE,
  KEY `index_sub_industry` (`sub_industry`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='企业信息';
"""

TABLE_CONFIG = {
    'xb_company_position_1': create_sql_to_xb_company_position_1,
    'xb_company_1': create_sql_to_xb_company_1,
}

ZHILIAN_API_URL = 'https://fe-api.zhaopin.com/c/i/sou'


DB_CONNS = {
    'default': lambda: pymysql.connect(host="localhost", port=3306, user="root",
                                       password="training", db="crawler_db", charset='utf8mb4'),
}

ZHILIAN_CONFIG = {
    'start': 0,
    'page_size': 5,
    'url': """
https://fe-api.zhaopin.com/c/i/sou?pageSize=60&cityId=530&industry=10100&workExperience=-1&education=5&companyType=-1&employmentType=-1&jobWelfareTag=-1&kw=python&kt=3&_v=0.83086867&x-zp-page-request-id=52e34b70ae424e8ab0251d1af51441db-1544065836286-73332    """,
    'keyword': 'python'
}
