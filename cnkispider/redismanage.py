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
from hashlib import md5
from sqlmanage import SqlUrlManager
from logmanage import LogManager

logger = LogManager(level=10)

class RedisManager:
    """
    创建redis管理对象。从数据库获取url存入redis集合去重，并分发任务给页面爬取进程，分发的url进入已爬队列，url_state为0
    抓取的页面数据存入redis,并根据id号到sql数据库更新url_state为1；第三部页面解析后的数据也存入redis,由redis调度存储
    到数据库
    """
    HOST = 'localhost'
    REDIS_PORT = 6379
    PROJECT = 'cnki'

    @logger.log_decoratore
    def __init__(self):
        """
        初始化redis管理器的数据库链接
        """
        self.timeout = 600
        try:
            self.r = redis.Redis(host=self.HOST, port=self.REDIS_PORT, decode_responses=True)
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

    def get_md5(self, data):
        """
        传入数据，进行MD5摘要算法处理
        :param data: 要进行摘要算法处理的数据
        :return: 数据摘要
        """
        data = data.encode('utf-8')
        m = md5()
        m.update(data)
        md5_digest = m.hexdigest()
        return md5_digest

    @logger.log_decoratore
    def put_url(self, item = None):
        """
        从mysql获取url存入redis:待爬队列 wait_url,url过滤集合 url_filter(md5摘要存储过滤),已爬队列 done_url
        :return:  item
        """
        try:
            wait_queue_key = self.make_key(key='wait_url')
            filter_key = self.make_key(key='url_filter')
            count = 0
            if not item:    # 从sql数据库获取url去重入队
                self.sqlurlmanager = SqlUrlManager()
                for i, item in enumerate(self.sqlurlmanager.query_url()):
                    url = item['title_url']
                    url_digest = self.get_md5(data=url)
                    result = self.r.sadd(filter_key, url_digest)         # redis集合去重
                    if result == 1:
                        count += 1
                        item = json.dumps(item)
                        self.r.rpush(wait_queue_key, item)               # 返回值为插入后的队列长度
                        print('{} -> {} counts: '.format(__file__, wait_queue_key), count)
                    else:
                        continue
            else:           # 直接传入待爬数据导入redis入队
                url = item['title_url']
                url_digest = self.get_md5(data=url)
                result = self.r.sadd(filter_key, url_digest)           # redis集合去重
                if result == 1:
                    count += 1
                    item = json.dumps(item)
                    self.r.rpush(wait_queue_key, item)
                    print('{} -> {} counts: '.format(__file__, wait_queue_key), count)
        except Exception as e:
            print('Put_url url 入队出错：{}'.format(e))

    @logger.log_decoratore
    def get_url(self):
        """
        从redis获取待爬的Url
        :return: 待爬item
        """
        # 从待爬队列获取url返回
        url_key = self.make_key(key='wait_url')                       # 待爬队列获取
        item = self.r.blpop(url_key, timeout=self.timeout)            # 从对列头部获取页面，队列为空则阻塞,超时10分钟
        if isinstance(item, tuple):
            item = json.loads(item[1])
            return item
        if not item:
            return None

    @logger.log_decoratore
    def put_page(self, item=None):
        """
        item: 爬虫并发获取的页面，存入redis队列等待解析
        :return: redis中数据存储的key
        """
        wait_parse_key = self.make_key(key='pages')
        if item:
            item = json.dumps(item)
            self.r.rpush(wait_parse_key, item)                        # 推进redis的待解析队列
        else:
            return wait_parse_key

    @logger.log_decoratore
    def get_page(self):
        """
        从redis获取页面
        :return:  待解析页面
        """
        page_key = self.put_page()
        item = self.r.blpop(page_key, timeout=self.timeout)           # 从对列头部获取页面，队列为空则阻塞,超时10分钟
        if isinstance(item, tuple):
            item = json.loads(item[1])
            return item

    @logger.log_decoratore
    def put_item(self, item=None):
        """
        存储页面解析的数据到redis中。
        :return:  redis中数据存储的key
        """
        item_key = self.make_key(key='items')
        if item:
            item = json.dumps(item)
            self.r.rpush(item_key, item)
        else:
            return item_key

    @logger.log_decoratore
    def get_item(self):
        """
        从redis中获取解析后的数据item
        :return: 待持久化item
        """
        item_key = self.put_item()
        item = self.r.blpop(item_key, timeout=self.timeout)       # 从对列头部获取页面，队列为空则阻塞,超时10分钟
        if isinstance(item, tuple):
            item = json.loads(item[1])
            return item
        if not item:
            return None



if __name__ == "__main__":
    redismanager = RedisManager()
    redismanager.put_url()
