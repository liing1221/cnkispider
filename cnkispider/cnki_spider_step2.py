# -*- coding: utf-8 -*-
"""
    @Project     : cnkispider
    @File        : cnki_spider_step2.py
    @Create_Date : 2019-02-19 11:31
    @Update_Date : 2019-02-19 11:31
    @Author      : liing
    @Email       : liing1221@163.com
    @Software    : PyCharm
"""
import requests
from fake_useragent import UserAgent
from logmanage import LogManager
from redismanage import RedisManager
from proxymanage import ProxyManager
from sqlmanage import SqlUrlManager

logger = LogManager(level=30)

class CnkiSpider:
    """
    根据给定URL，抓取页面，并更新数据库cnki_urls的url_state，存入redis待解析
    """
    def __init__(self):
        """
        初始化CNKI抓取对象
        """
        self.retries = 5
        self.timeout = 20
        self.redismanager = RedisManager()
        self.sqlmanager = SqlUrlManager()
        self.user_agent = UserAgent().chrome
        self.proxy_manager = ProxyManager(pool=False)
        self.headers = {
            "Host": "kns.cnki.net",
            "Connection": "keep-alive",
            "Cache-Control": "max-age=0",
            "Upgrade-Insecure-Requests": "1",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Accept-Encoding": "gzip,deflate",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Referer": "http://kns.cnki.net/kns/brief/default_result.aspx",
            "User-Agent": self.user_agent
        }
        # self.cookies = {"Ecp_ClientId": "6190218174501425684",
        #                "Ecp_IpLoginFail": "190218124.202.241.162",
        #                "ASP.NET_SessionId": "oedpnlpza3h2dx5o4i5m5xhs",
        #                "SID_kns": "123121",
        #                # "RsPerPage": "20",      # 可省
        #                # "cnkiUserKey": "05a9e126-4d9f-5f86-eadd-95116a35129b",  # 可省
        #                # "SID_klogin": "125144",
        #                # "SID_crrs": "125132",
        #                # "SID_krsnew": "125132", # 可省
        #                # "KNS_SortType": '',
        #                # "_pk_ses": "*"          # 可省
        # }

    def get_item(self):
        """
        获取要抓取页面的URL数据
        :return: 数据item
        """
        item = self.redismanager.get_url()
        return item

    def make_proxy(self):
        """
        构建proxies代理
        :return:
        """
        ip, port = self.proxy_manager.get_proxy()
        proxies = {
            'https': 'http://{}:{}'.format(ip, port),
            'http': 'http://{}:{}'.format(ip, port)
        }
        return proxies

    @logger.log_decoratore
    def get_page(self, item):
        """
        抓取item指定URL的页面
        :param item: 待爬URL的item
        :return: 包含页面page数据的待解析item
        """
        retries = self.retries
        url = item['title_url']
        while True:
            retries -= 1
            proxies = self.make_proxy()
            s = requests.Session()
            response = s.get(url, headers=self.headers, proxies=proxies, timeout=self.timeout)    # cookies = self.cookies
            response.encoding = 'utf-8'
            if response.status_code == 200:
                item['page'] = response.text
                item['url_state'] = 1
                return item

    @logger.log_decoratore
    def put_item(self, item):
        """
        存储item到redis的待解析队列，同时更新数据库cnki_urls的url_state为1
        :param item: 完成页面抓取的item
        :return:
        """
        id = item['id']
        self.redismanager.put_page(item=item)   # item存入redis的带解析队列
        self.sqlmanager.update_url(flag=1, id=id)

    def to_run(self):
        """
        执行页面抓取处理任务
        :return:
        """
        while True:
            url_item = self.get_item()
            if url_item:
                item = self.get_page(url_item)
                self.put_item(item)
            else:
                break


if __name__ == "__main__":
    cnkispider = CnkiSpider()
    cnkispider.to_run()