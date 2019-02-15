# -*- coding: utf-8 -*-
"""
    @Project     : malacardspider
    @File        : redismange.py
    @Create_Date : 2019-01-14 16:13
    @Update_Date : 2019-01-14 16:13
    @Author      : liing
    @Email       : liing1221@163.com
    @Software    : PyCharm
    @Description : redis管理类 (disease 的url列表未同步插入redis时，执行本文件，从sql读数据插入redis)
"""
import redis
import json

from sqlmanage import SqlUrlManager
from logmanage import LogManager

logger = LogManager(level=10)

class RedisManager:
    """
    创建redis管理对象。从数据库获取url存入redis集合去重，并分发任务给disease爬取进程，分发的url进入已爬队列，解析flag为0
    disease爬取的疾病数据存入redis,并根据url到已爬队列更新url的flag为1，同时更新数据库url的爬取状态
    """
    HOST = 'localhost'
    REDIS_PORT = 6379
    PROJECT = 'malacards'

    @logger.log_decoratore
    def __init__(self):
        """
        初始化redis管理器的数据库链接
        """
        self.timeout = 600
        try:
            self.r = redis.Redis(host=self.HOST, port=self.REDIS_PORT, decode_responses=True)
            self.sqlurlmanager = SqlUrlManager()
        except Exception as e:
            print('Redis管理器初始化数据库链接出错:{}'.format(e))

    def make_key(self, key):
        """
        格式化返回redis存储的key
        :param key: 字符串
        :return:
        """
        redis_key = '{}:{}'.format(self.PROJECT, key)
        return redis_key

    @logger.log_decoratore
    def put_url(self, item = None):
        """
        从mysql获取url存入redis（疾病的mcid属性唯一）:待爬队列wait_url, 去重集合url_mcid, 已爬队列 done_url
        :return:  item
        """
        # 从sql数据库获取url去重入队
        try:
            url_key = self.make_key(key='wait_url')
            filter_key = self.make_key(key='mcid')
            count = 0
            if not item:
                for i, item in enumerate(self.sqlurlmanager.query_url()):
                    # print('{} -> disease_urls number: '.format(__file__), i)
                    result = self.r.sadd(filter_key, item['mcid'])       # redis集合去重
                    if result == 1:
                        count += 1
                        item = json.dumps(item)
                        self.r.rpush(url_key, item)                      # 返回值为插入后的队列长度
                        print('{} -> {} counts: '.format(__file__, url_key), count)
                    else:
                        continue
            else:
                result = self.r.sadd(filter_key, item['mcid'])           # redis集合去重
                if result == 1:
                    count += 1
                    item = json.dumps(item)
                    self.r.rpush(url_key, item)
                    print('{} -> {} counts: '.format(__file__, url_key), count)
        except Exception as e:
            print('Put_url url 入队出错：{}'.format(e))

    def get_url(self):
        """
        从redis获取待爬的item与Url
        :return: item
        """
        # 从待爬队列获取url返回
        url_key = self.make_key(key='wait_url')                       # 待爬队列获取
        item = self.r.blpop(url_key, timeout=self.timeout)            # 从对列头部获取页面，队列为空则阻塞,超时10分钟
        if isinstance(item, tuple):
            item = json.loads(item[1])
            return item
        if not item:
            return None

    def put_page(self, item=None):
        """
        item 包括疾病数据与页面数据，存储路径信息
        多线程爬虫获取页面，存入redis队列等待解析
        :return:
        """
        page_key = self.make_key(key='pages')
        done_mcid = self.make_key(key='done_url')
        # filter_key = self.make_key(key='mcid')
        if item:
            mcid = item['mcid']
            item = json.dumps(item)
            self.r.rpush(done_mcid, mcid)                     # 获得页面响应后存入已爬队列
            # self.r.srem(filter_key, mcid)                     # 从过滤集合中删除已爬疾病：集合剩余为未爬疾病
            self.r.rpush(page_key, item)
        else:
            return page_key

    def get_page(self):
        """
        从redis获取页面
        :return:
        """
        page_key = self.put_page()
        item = self.r.blpop(page_key, timeout=self.timeout)           # 从对列头部获取页面，队列为空则阻塞,超时10分钟
        if isinstance(item, tuple):
            item = json.loads(item[1])
            return item

    def put_item(self, item=None):
        """
        存储页面解析的数据到redis中。
        :return:
        """
        item_key = self.make_key(key='items')
        if item:
            item = json.dumps(item)
            self.r.rpush(item_key, item)
        else:
            return item_key

    def get_item(self):
        """
        从redis中获取疾病items数据
        :return:
        """
        item_key = self.put_item()
        item = self.r.blpop(item_key, timeout=self.timeout)       # 从对列头部获取页面，队列为空则阻塞,超时10分钟
        if isinstance(item, tuple):
            item = json.loads(item[1])
            return item
        if not item:
            return None

    def get_items(self, max=10):

        """
        从redis中获取多条数据(max条，同事删除redis中相应的数据)，并返回
        :return: items列表
        """

    # def save_item(self, item):
    #     """
    #     从redis获取item存入Mongo数据库
    #     :param item: 解析出来的疾病数据
    #     :return:
    #     """



if __name__ == "__main__":
    redismanager = RedisManager()
    redismanager.put_url()
    # print(dir(redismanager.get_url))

    # s = input('>>>>>>>>>>:')
    # if not s:
    #     item = next(redismanager.get_url())
    #
    #     print(dir(item), '\n', item)
    #
    # else:
    #
    #     return