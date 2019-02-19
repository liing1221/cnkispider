# -*- coding: utf-8 -*-
"""
    @Project     : malacardspider
    @File        : cookiemanage.py
    @Create_Date : 2019-01-09 18:30
    @Update_Date : 2019-01-09 18:30
    @Author      : liing
    @Email       : liing1221@163.com
    @Software    : PyCharm
"""
import time
import random
import redis
import requests
import threading
import threadpool
from requests.models import Response
from requests.cookies import RequestsCookieJar
from fake_useragent import UserAgent
from logmanage import LogManager
from proxymanage import ProxyManager


logger = LogManager(level=10)


class CookieManager:
    URL = "http://kns.cnki.net/kns/brief/default_result.aspx"
    INTERVAL = 900  # 15分钟
    POOL = []                             # cookies池

    def __init__(self, url=None, pool=True):
        """
        初始化过期时间
        :param pool:
        """
        if url:
            self.URL = url     # 初始化cookie请求的url
        self.cookies = RequestsCookieJar()
        self.user_agent = UserAgent().random
        self.header = {
            "Host": "kns.cnki.net",
            "Connection": "keep-alive",
            "Cache-Control": "max-age=0",
            "Upgrade-Insecure-Requests": "1",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Accept-Encoding": "gzip,deflate",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "User-Agent": self.user_agent}
        self.proxymanager = ProxyManager(pool=False)
        self.timeout = 10
        self.pool = pool                # 是否使用cookie池：True or False
        if self.pool:
            self.get_pool()
        else:
            self.set_cookie()

    @logger.log_decoratore
    def set_cookie(self):
        """
        cookie获取，记录cookies以及获取时间
        :return:
        """
        retry_time = 5  # 重复请求次数
        # IP, PORT = self.proxymanager.get_proxy()
        # self.proxy = {
        #     'https': 'http://{}:{}'.format(IP, PORT)
        # }
        while True:
            try:
                print(1111111)
                print(self.URL)
                resp = requests.get(
                    self.URL,
                    headers=self.header,
                    # proxies=self.proxy,
                    cookies=self.cookies,
                    timeout=self.timeout)
                print(resp.status_code)
                if resp.status_code == 200:
                    self.EXPIRES_TIME = int(time.time())    # 过期时间
                    self.cookies.update(resp.cookies)
                    print('resp.cookies>>', resp.cookies)
                    print('self.cookies', self.cookies)
                return self.cookies, self.header, self.EXPIRES_TIME
            except Exception as e:
                retry_time -= 1
                if retry_time <= 0:
                    print('self.cookies>> {}...!'.format(self.cookies))
                    print(e)
                    return self.cookies, 0
                time.sleep(0.1)

    @logger.log_decoratore
    def get_cookie(self):
        """
        若__init__的pool参数为True，则从POOL随机获取一个cookie；否则自动获取一个cookie；
        并都对cookie进行了过期维护
        :return: 返回获取cookie
        """
        now_time = int(time.time())
        if not self.pool:                                                     # 没用使用cookie池时
            cookie_expires = self.EXPIRES_TIME                                # 过期时间
            if cookie_expires + self.INTERVAL < now_time:                     # 过期从新获取
                self.set_cookie()
            return self.cookies
        else:                                                                 # 使用cookie池时
            while True:
                try:
                    cookies = random.choice(
                        self.POOL)                        # 过期维护
                    # 过期时间
                    cookie_expires = cookies[1]
                    if cookie_expires + self.INTERVAL < now_time:             # 移除过期cookie
                        self.cookie_remove(cookies)
                    else:
                        return cookies[0]
                except IndexError as e:
                    self.get_pool()

    def _add_cookie(self, i):
        """
        使用cookie池时，添加cookie到POOL
        :return:
        """
        self.set_cookie()
        item = (self.cookies, self.EXPIRES_TIME)
        self.POOL.append(item)

    def get_pool(self):
        """
        获取一个数量为200的cookie池POOL
        :return:
        """
        pool = threadpool.ThreadPool(32)
        req = threadpool.makeRequests(self._add_cookie, range(200))
        [pool.putRequest(i) for i in req]
        pool.wait()

    def cookie_remove(self, cookie):
        """
        从POOL中移除一个cookie，并再添加一个
        :param cookie: cookie
        :return:
        """
        self.POOL.remove(cookie)
        self._add_cookie()


class RedisCookieManager:
    """
    创建redis的cookie管理类：为请求添加cookie,并进行过期维护
    """
    URL = "http://kns.cnki.net/kns/brief/default_result.aspx"
    INTERVAL = 1500  # 25分钟

    def __init__(self, url=None, num=10):
        """
        初始化过期时间
        :param pool:
        """
        self.URL = url                                # 初始化cookie请求的url
        self.cookies = RequestsCookieJar()
        self.user_agent = UserAgent().chrome
        self.headers = {
            "Host": "kns.cnki.net",
            "Connection": "keep-alive",
            "Cache-Control": "max-age=0",
            "Upgrade-Insecure-Requests": "1",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Accept-Encoding": "gzip,deflate",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "User-Agent": self.user_agent}
        self.proxymanager = ProxyManager(pool=False)
        self.timeout = 20
        self.redis_host = 'localhost'
        self.redis_port = 6379
        self.num = num                               # redis中存储的cookie数量， 默认10个

    @logger.log_decoratore
    def set_cookie(self):
        """
        cookie获取，记录cookies以及获取时间
        :return:
        """
        retry_time = 5  # 重复请求次数
        # IP, PORT = self.proxymanager.get_proxy()
        # self.proxy = {
        #     'https': 'http://{}:{}'.format(IP, PORT)
        # }
        while True:
            try:
                resp = requests.get(
                    self.URL,
                    headers=self.headers,
                    # proxies=self.proxy,
                    cookies=self.cookies,
                    timeout=self.timeout)
                if resp.status_code == 200:
                    self.cookies.update(resp.cookies)
                    self.EXPIRES_TIME = int(time.time())      # 过期时间
                    print('resp.cookies>>', resp.cookies)
                    print('self.cookies', self.cookies)
                return self.cookies, self.EXPIRES_TIME
            except Exception as e:
                retry_time -= 1
                if retry_time <= 0:
                    resp = Response()
                    cookie = resp.cookies
                    print('cookie>> {}...!'.format(cookie))
                    return cookie
                time.sleep(0.1)

    @logger.log_decoratore
    def get_cookie(self):
        """
        从Redis的mala_cookies列表中最左侧获取一个cookie判断过期时间，没过期返回
        并都对cookie进行了过期维护
        :return: 返回获取cookie
        """
        try:
            while True:
                r = redis.Redis(host=self.redis_host, port=self.redis_port)
                res = r.blpop('cnki:cookies')
                if not res:
                    self.create_redis()
                    continue
                cookie_expires = res[1]
                now_time = int(time.time())
                if cookie_expires + self.INTERVAL < now_time:   # 过期从新获取
                    continue
                else:
                    r.rpush('cnki:cookies', res)
                    return res[0]
        except Exception as e:   # redis为空时，添加cookie
            raise e

    def create_redis(self):
        """
        往redis插入cookie
        :return:
        """
        pool = threadpool.ThreadPool(32)
        req = threadpool.makeRequests(self._add_cookie, list(range(self.num)))
        [pool.putRequest(i) for i in req]
        pool.wait()

    @logger.log_decoratore
    def _add_cookie(self, i):
        """
        把cookie存到redis
        :return:
        """
        try:
            r = redis.Redis(host=self.redis_host, port=self.redis_port, db=0)
            res = self.set_cookie()
            if res:
                print(type(res), res.get_dict())
                r.rpush('mala_cookies', res.get_dict())
        except Exception as e:
            pass


if __name__ == "__main__":

    # class CookieManager
    start = time.time()
    print('Start time : {}'.format(time.ctime(start)))
    cookie1 = CookieManager(pool=False)
    # cookie2 = CookieManager(pool=False)
    # print(id(cookie1), id(cookie2))                #验证单列模式
    # for i in zip(cookie1.POOL, cookie2.POOL):
    #     print(i[0]['expire'], i[1]['expire'], i[0]['expire'] == i[1]['expire'])
    # print(cookie1.get_cookie(), cookie2.get_cookie())
    print(cookie1.get_cookie())
    end = time.time()
    print('End time : {}'.format(time.ctime(end)))
    print(end - start)

    # class RedisCookieManager
    # manager = RedisCookieManager()
    # cookie = manager.get_cookie()
    # print(cookie)
