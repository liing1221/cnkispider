# -*- coding: utf-8 -*-

import sys
import pymysql
import time
from logmanage import LogManager


logger = LogManager(level=0)


class SqlUrlManager:
    """
    文献URL的sql数据库插入、查询、更新数据库状态
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
        创建数据存储表:cnki_urls; cnki_datas
        :return:
        """
        sql = r'''CREATE TABLE IF NOT EXISTS cnki_datas (
                  id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
                  drugid VARCHAR(16) NOT NULL COMMENT '药物编号',
                  title VARCHAR(256) NOT NULL COMMENT '文献标题',
                  authors VARCHAR(256) NOT NULL COMMENT '文献作者',
                  abstract TEXT COMMENT '摘要',
                  periodical VARCHAR(64) COMMENT '期刊名称',
                  issue VARCHAR(24) COMMENT '出版日期',
                  issn  VARCHAR(16) COMMENT 'ISSN号',
                  catalog_keyword VARCHAR(64) COMMENT '分类关键字',
                  catalog_ztcls VARCHAR(24) COMMENT '分类号',
                  url_state TINYINT UNSIGNED DEFAULT 0 COMMENT '爬取状态：0未访问，1未解析，2已解析',
                  title_url VARCHAR(512) NOT NULL COMMENT '文献路径',
                  publication_date VARCHAR(20) NOT NULL COMMENT '发表日期',
                  cited SMALLINT UNSIGNED  COMMENT '引用次数',
                  download SMALLINT UNSIGNED COMMENT '下载次数',
                  INDEX drugid (drugid),
                  INDEX url_state (url_state)
                  )ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;'''
        try:
            self.cursor.execute(sql)
        except Exception as e:
            print('Create table Error: {}'.format(e))

    @logger.log_decoratore
    def save_url(self, data):
        """
        向cnki_urls存储数据,默认url未访问0
        :param data:  文献URL数据
        :return: 返回影响行数
        """
        sql = '''INSERT INTO cnki_datas (drugid, title, authors, periodical, title_url, publication_date, cited,
                 download) VALUES ("{}","{}","{}","{}","{}","{}","{}","{}");'''.format(
            data['drugid'],
            data['title'],
            data['authors'],
            data['periodical'],
            data['title_url'],
            data['publication_date'],
            data['cited'],
            data['download'])
        try:
            self.conn.connect()
            self.cursor.execute(sql)
            row = self.conn.commit()   # 返回影响的行数
            return row
        except Exception as e:
            self.conn.rollback()
            print("Save url Error: {}".format(e))

    @logger.log_decoratore
    def query_url(self):
        """
        查找url_state为0的URL
        :return: data的生成器
        """
        sql = '''SELECT * FROM cnki_datas WHERE url_state=0;'''
        try:
            self.conn.connect()
            self.cursor.execute(sql)
            self.conn.commit()
            while True:
                row = self.cursor.fetchone()         # 每次读取返回数据字典
                if row:
                    yield row
                else:
                    break
        except Exception as e:
            print("Query url Error: {}".format(e))

    def update_url(self, flag, data_id):
        """
        根据id编号更新数据库url_state
        :param flag: url状态标识：初始为0，更新1为已爬取未解析页面，更新2为已解析页面
        :param id: 数据id
        :return:
        """
        sql = '''UPDATE cnki_datas SET url_state="{}" WHERE id="{}";'''.format(
            flag, data_id)
        try:
            self.conn.connect()
            self.cursor.execute(sql)
            row = self.conn.commit()                        # 返回影响的行数
            return row
        except Exception as e:
            self.conn.rollback()
            print(
                "{} -> Update url state Error with -id:{} -flag:{} - error! e : {}".format(
                    __file__,
                    id,
                    flag,
                    e))

    @logger.log_decoratore
    def save_data(self, item):
        """
        页面解析后，保存完整数据, 并更新url_state为2(已存储数据）
        :param item: 解析页面后的数据
        :return:
        """
        flag = 2
        sql = '''UPDATE cnki_datas SET abstract="{}", issue="{}", issn="{}", catalog_keyword="{}", catalog_ztcls="{}",
                 url_state="{}" WHERE id="{}";'''.format(
            item['abstract'],
            item['issue'],
            item['issn'],
            item['catalog_kewword'],
            item['publication_date'],
            flag,
            item['id'])
        try:
            self.conn.connect()
            self.cursor.execute(sql)
            row = self.conn.commit()   # 返回影响的行数
            return row
        except Exception as e:
            self.conn.rollback()
            raise e

    def __del__(self):
        self.cursor.close()
        self.conn.close()


if __name__ == "__main__":
    sqlurlmanager = SqlUrlManager()
    sqlurlmanager.save_url(data='')
