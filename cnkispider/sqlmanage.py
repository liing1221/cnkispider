# -*- coding: utf-8 -*-

import sys
import pymysql
import time
from logmanage import LogManager


logger = LogManager(level=0)


class SqlUrlManager:
    """
    疾病URL的sql数据库插入、查询、更新数据库状态
    """
    if 'win' in sys.platform:
        HOST = 'localhost'
        PORT = 3306
        USER = 'root'
        PASSWORD = '123456'
        DB = 'test'
    elif 'linux' in sys.platform:
        HOST = 'localhost'
        PORT = 3306
        USER = 'spider'
        PASSWORD = 'spider@#$8900'
        DB = 'spider'
    @logger.log_decoratore
    def __init__(self):
        """
        初始化数据库连接
        """
        try:
            self.conn = pymysql.Connect(
                host=self.HOST,
                port=self.PORT,
                user=self.USER,
                passwd=self.PASSWORD,
                db=self.DB,
                charset='utf8mb4')
            self.cursor = self.conn.cursor(cursor=pymysql.cursors.DictCursor)
            self.create_table()
        except ConnectionError as e:
            print("SqlUrlManager ConnectionError: {}".format(e))

    @logger.log_decoratore
    def create_table(self):
        """
        创建数据存储表
        :return:
        """
        sql = '''CREATE TABLE IF NOT EXISTS disease_urls (
                 id INT AUTO_INCREMENT PRIMARY KEY,
                 anatomical_category VARCHAR(128) NOT NULL COMMENT '疾病分类',
                 category_include VARCHAR(512) NOT NULL COMMENT '类别包含的子类',
                 disease_count SMALLINT UNSIGNED NOT NULL COMMENT '该类别的疾病数目',
                 name VARCHAR(256) NOT NULL COMMENT '疾病名称',
                 family VARCHAR(20) COMMENT '疾病族（按首字母分）',
                 mcid VARCHAR(20) NOT NULL COMMENT '疾病编号',
                 mifits TINYINT UNSIGNED NOT NULL COMMENT '评分',
                 disease_url VARCHAR(512) NOT NULL COMMENT '疾病的页面URL',
                 url_identify TINYINT UNSIGNED DEFAULT 0 COMMENT '页面爬取状态，0未访问，1已访问并解析'
                 )ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;'''
        try:
            self.cursor.execute(sql)
        except Exception as e:
            print('Create table Error: {}'.format(e))

    @logger.log_decoratore
    def save_url(self, data):
        """
        向disease_urls存储数据,默认url未访问0
        :param data:  疾病URL数据
        :return: 返回影响行数
        """
        print('save_url save_url save_url save_url')
        # sql = '''INSERT INTO disease_urls (anatomical_category, category_include, disease_count,name,family,mcid,
        #          mifits,disease_url) VALUES ("{}","{}","{}","{}","{}","{}","{}","{}");'''.format(
        #     data['anatomical_category'],
        #     data['category_include'],
        #     data['disease_count'],
        #     data['name'],
        #     data['family'],
        #     data['mcid'],
        #     data['mifits'],
        #     data['disease_url'])
        # try:
        #     self.conn.connect()
        #     self.cursor.execute(sql)
        #     row = self.conn.commit()   # 返回影响的行数
        #     return row
        # except Exception as e:
        #     self.conn.rollback()
        #     print("Save url Error: {}".format(e))

    @logger.log_decoratore
    def query_url(self):
        """
        查找url_identify为0的URL
        :return: data的生成器
        """
        sql = '''SELECT * FROM disease_urls WHERE url_identify=0;'''
        try:
            self.conn.connect()
            self.cursor.execute(sql)
            self.conn.commit()
            while True:
                row = self.cursor.fetchone()    # 每次读取返回数据字典
                if row:
                    yield row
                else:
                    break
        except Exception as e:
            print("Query url Error: {}".format(e))

    def update_url(self, flag, mcid):
        """
        根据药物编号更新数据库url_identify
        :param flag: url状态标识：初始为0，更新1为已爬取页面，更新2为已解析页面
        :param mcid: 药物编号
        :return:
        """
        sql = '''UPDATE disease_urls SET url_identify="{}" WHERE mcid="{}";'''.format(
            flag, mcid)
        try:
            self.conn.connect()
            self.cursor.execute(sql)
            row = self.conn.commit()   # 返回影响的行数
            print(
                '{} -> Update url identify with - {} - {} - successfully! counts : {}'.format(__file__, mcid, flag, row))
            return row
        except Exception as e:
            self.conn.rollback()
            print(
                "{} -> Update url Error with mcid - {} - {} - : {}".format(__file__, mcid, flag, e))

    def __del__(self):
        self.cursor.close()
        self.conn.close()


if __name__ == "__main__":
    sqlurlmanager = SqlUrlManager()
    sqlurlmanager.save_url(data='')
