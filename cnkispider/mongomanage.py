# -*- coding: utf-8 -*-
"""
    @Project     : malacardspider
    @File        : mongoManage.py
    @Create_Date : 2019-01-14 13:20
    @Update_Date : 2019-01-14 13:20
    @Author      : liing
    @Email       : liing1221@163.com
    @Software    : PyCharm
"""
import json
import pymongo
from logmanage import LogManager


logger = LogManager(level=0)


class MongoManager:
    """
    疾病URL的sql数据库插入、查询、更新数据库状态
    """
    HOST = 'localhost'
    PORT = 27017
    DB = 'malacards'

    @logger.log_decoratore
    def __init__(self):
        """
        初始化数据库连接
        """
        try:
            self.mongoclient = pymongo.MongoClient(
                'mongodb://{}:{}/'.format(self.HOST, self.PORT))
            # self.mongoclient = pymongo.MongoClient(host=self.HOST, port=self.PORT)
            self.db = self.mongoclient[self.DB]   # 初始化数据库链接
            collist = self.db.list_collection_names()
            if 'mala_diseases' in collist:
                print('Mongo数据库mala_diseases集合已存在 ...')
            self.col = self.db['mala_diseases']   # 连接到集合
            self.col.create_index('id')
        except Exception as e:
            print('Mongo数据库链接出错:{}'.format(e))

    @logger.log_decoratore
    def save_disease(self, item):
        """
        向mala_diseases集合存储数据,一次多条
        :param data:  疾病数据
        :return:
        """
        try:
            l = self.query_item(item)
            if l:
                return
            else:
                row = self.col.insert_one(item)
        except Exception as e:
            print(
                'Mongo save disease item Error with mcid:{} name:{} url:{}\nError e and item: {}\n{}'.format(
                    item['mcid'], item['name'], item['disease_url'], e, item))

    @logger.log_decoratore
    def query_item(self, item):
        """
        查找dic指定的疾病数据
        :param dic: 查找字段的字典
        :return: 返回疾病数据的字典列表
        """
        l = []
        [l.append(i) for i in self.col.find({'mcid': item['mcid']})]
        return l

    def __del__(self):
        self.mongoclient.close()


if __name__ == "__main__":
    mongomanager = MongoManager()
