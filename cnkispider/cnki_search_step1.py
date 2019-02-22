# -*- coding: utf-8 -*-
"""
    @Project     : cnkispider
    @File        : cnki_search_step1.py
    @Create_Date : 2019-02-15 13:03
    @Update_Date : 2019-02-15 13:03
    @Author      : liing
    @Email       : liing1221@163.com
    @Software    : PyCharm
"""
import time
import requests
from lxml import etree
from urllib.parse import urlencode
from fake_useragent import UserAgent
from logmanage import LogManager
from csvmanage import CsvReader
from proxymanage import ProxyManager
from sqlmanage import SqlUrlManager

logger = LogManager(level=30)


class CnkiSearch:
    """
    通过知网检索入口以及检索关键字，检索获取文献列表:获取文献列表信息以及url
    :知网登陆检索流程：get请求初始化cookie,post请求进行注册检索信息，再get请求查询结果
    """

    def __init__(self, proxies=False):
        """
        初始化搜索url,headers以及cookies
        """
        self.retries = 5
        self.timeout = 20
        self.user_agent = UserAgent().chrome
        self.s = requests.Session()
        if proxies:
            self.proxy_manager = ProxyManager(pool=False)
            ip, port = self.proxy_manager.get_proxy()
            self.proxies = {
                'https': 'http://{}:{}'.format(ip, port),
                'http': 'http://{}:{}'.format(ip, port)
            }
        else:
            self.proxies = None
        # self.base_url = "http://kns.cnki.net/kns/brief/default_result.aspx"
        self.base_url = "http://kns.cnki.net/kns/brief/result.aspx?dbprefix=scdb"
        self.post_url = 'http://kns.cnki.net/kns/request/SearchHandler.ashx'
        # self.search_url = 'http://kns.cnki.net/kns/brief/brief.aspx?'
        self.headers = {
            "Host": "kns.cnki.net",
            "Connection": "keep-alive",
            "Cache-Control": "max-age=0",
            "Upgrade-Insecure-Requests": "1",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Accept-Encoding": "gzip,deflate",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "User-Agent": self.user_agent}

    @staticmethod
    def get_param(keyword, sortkey=None):     # 类方法
        """
        初始化请求参数:检索关键字keyword，以及结果列表的排列方式sortkey,sortkey取值:引用排序——"(被引频次,'INTEGER') desc",
        相关性排序——"(FFD,'RANK') desc",下载排序——"(下载频次,'INTEGER') desc", 默认排序——' HTTP/1.1'无queryid参数
        :param keyword:  检索关键字
        :param sortkey:  检索结果的排序方式
        :return: url编码的查询字符串
        """
        if not sortkey:
            params = {
                "pagename": "ASP.brief_default_result_aspx",
                "isinEn": "1",
                "dbPrefix": "SCDB",
                "dbCatalog": "中国学术文献网络出版总库",
                "ConfigFile": "SCDBINDEX.xml",
                "research": "off",
                "t": int(time.time() * 1000),
                "keyValue": keyword,
                "S": "1",
                "sorttype": ' '  # HTTP/1.1'
            }
        else:
            params = {
                "pagename": "ASP.brief_default_result_aspx",
                "isinEn": "1",
                "dbPrefix": "SCDB",
                "dbCatalog": "中国学术文献网络出版总库",
                "ConfigFile": "SCDBINDEX.xml",
                "research": "off",
                "t": int(time.time() * 1000),
                "keyValue": keyword,
                "S": "1",
                "sorttype": sortkey,
                "queryid": '4 HTTP/1.1'
            }
        params = urlencode(params)
        return params

    @logger.log_decoratore
    def get_first(self):
        """
        第一次请求：构建请求会话，初始化cookies
        :return:
        """
        url = self.base_url
        if self.proxies:
            self.s.get(
                url=url,
                headers=self.headers,
                proxies=self.proxies,
                timeout=self.timeout)
        else:
            self.s.get(
                url=url,
                headers=self.headers,
                timeout=self.timeout)

    @logger.log_decoratore
    def post_second(self, keyword):
        """
        第二次post请求入口页:post注册提交查询字符串，获取查询结果链接字符串
        :param keyword: 检索关键字
        :return:
        """
        header = {"Accept": "*/*",
                  "Content-Type": "application/x-www-form-urlencoded",
                  "Origin": "http://kns.cnki.net",
                  # "Proxy-Connection": "keep-alive",
                  "Referer": "http://kns.cnki.net/kns/brief/result.aspx?dbprefix=scdb"
                  }
        headers = self.headers.update(header)
        params = {
            "action": '',
            "NaviCode": '*',
            "ua": "1.21",
            "isinEn": "1",
            "PageName": "ASP.brief_result_aspx",
            "DbPrefix": "SCDB",
            "DbCatalog": "中国学术文献网络出版总库",
            "ConfigFile": "SCDB.xml",
            "db_opt": "CJFQ, CDFD, CMFD, CPFD, IPFD, CCND, CCJD",
            "expertvalue": keyword,
            "his": "0",
            "__": time.strftime('%a %b %d %Y %H:%M:%S') + ' GMT+0800 (中国标准时间)'
        }
        if self.proxies:
            response = self.s.post(
                url=self.post_url,
                data=params,
                headers=headers,
                proxies=self.proxies,
                timeout=self.timeout)
        else:
            response = self.s.post(
                url=self.post_url,
                data=params,
                headers=headers,
                timeout=self.timeout)
        response.encoding = 'utf-8'
        if response.status_code == 200:
            return response.text

    @logger.log_decoratore
    def get_third(self, url):
        """
        根据检索url,请求获取检索结果的页面数量与页面链接
        :param url: 根据查询参数构造的url
        :return: html页面
        """
        retry = self.retries
        header = {
            "Referer": "http://kns.cnki.net/kns/brief/result.aspx?dbprefix=scdb"}
        self.headers.update(header)
        while retry > 0:
            retry -= 1
            try:
                if self.proxies:
                    response = self.s.get(
                        url=url,
                        headers=self.headers,
                        proxies=self.proxies,
                        timeout=self.timeout)
                else:
                    response = self.s.get(
                        url=url,
                        headers=self.headers,
                        timeout=self.timeout)
                response.encoding = 'utf-8'
                if response.status_code == 200 and response:
                    html = etree.HTML(response.text)
                    page_href = html.xpath(r'//*[@id="Page_next"]/@href')
                    if page_href:
                        page_href = page_href[0]
                        page_count = html.xpath(
                            r'//*[@id="Page_next"]/../preceding-sibling::span/text()')
                        page_count = int(page_count[0].split('/')[1])
                        print(page_count, '------', page_href)
                        return page_count, page_href
                    else:
                        return response
            except Exception as e:
                print(
                    'Error occur in function : {} \n{}'.format(
                        self.get_third.__name__,
                        locals()))
                continue

    @logger.log_decoratore
    def get_page(self, url):
        """
        由get_third中获取检索结果的页面数量以及页面href,爬取检索结果列表
        :return:
        """
        retry = self.retries
        header = {
            "Referer": "http://kns.cnki.net/kns/brief/result.aspx?dbprefix=scdb"}
        headers = self.headers.update(header)
        print("self.s.cookies >> ", self.s.cookies.get_dict())
        while retry > 0:
            retry -= 1
            try:
                if self.proxies:
                    response = self.s.get(
                        url=url,
                        headers=headers,
                        proxies=self.proxies,
                        timeout=self.timeout)
                else:
                    response = self.s.get(
                        url=url,
                        headers=headers,
                        timeout=self.timeout)
                response.encoding = 'utf-8'
                if response.status_code == 200 and response:
                    return response
            except Exception as e:
                print(
                    'Error occur in function : {} \n{}'.format(
                        self.get_third.__name__,
                        locals()))
                continue

    @logger.log_decoratore
    def parse_url(self, response):
        """
        根据 response 解析检索结果条目，以及条目url,并存入数据库, 记录url抓取状态flag:0待获取页面；1已获取页面；2已解析页面并存抽数据
        :param response:  页面请求响应
        :return: item
        """
        if not response:
            return
        else:
            html = etree.HTML(response.text)
            trs = html.xpath(
                r'//*[@id="ctl00"]//table[@class="GridTableContent"]/tr[not(@class)]')  # 所有的文献标题
            for tr in trs:
                item = {}
                item['title'] = str(
                    tr.xpath(r'string(./td[2])')).strip()          # 文献标题
                # 文献URL
                title_url = tr.xpath(r'./td[2]/a/@href')[0]
                item['title_url'] = 'http://kns.cnki.net/KCMS/' + title_url[5:]
                item['authors'] = ','.join(
                    tr.xpath(r'./td[3]/a/text()'))          # 文献作者
                item['periodical'] = str(
                    tr.xpath(r'./td[4]/a/text()')[0])         # 发表期刊
                item['publication_date'] = tr.xpath(
                    r'./td[5]/text()')[0].strip()          # 发表日期
                # 引用次数,可为空
                cited = tr.xpath(r'string(./td[7])')[0].strip()
                if cited:
                    item['cited'] = cited
                else:
                    item['cited'] = 0
                # 下载次数,可为空
                download = tr.xpath(r'string(./td[8])')[0].strip()
                if download:
                    item['download'] = download
                else:
                    item['download'] = 0
                yield item

    def do_search(self, keyword):
        """
        整体执行类功能：构造查询url,并请求网页
        :param keyword:  检索的关键字
        :param sortkey:  检索结果的排序方式
        :return:
        """
        self.get_first()
        query = self.post_second(keyword=keyword)
        url = "http://kns.cnki.net/kns/brief/brief.aspx?pagename=" + query
        result = self.get_third(url)
        if isinstance(result, tuple):
            page_count = result[0]
            page_href = result[1]
            for i in range(1, page_count + 1):
                href_datas = page_href.split('&')
                href_datas[0] = href_datas[0].split('=')[0] + '=' + str(i)
                href = '&'.join(href_datas)
                page_url = 'http://kns.cnki.net/kns/brief/brief.aspx' + href
                print("page_url >> ", page_url)
                response = self.get_page(url=page_url)
                for item in self.parse_url(response):
                    yield item
        else:
            for item in self.parse_url(result):
                yield item

            # print(response.status_code)


def run_step1():
    """
    执行step1,检索并存储文献url
    :return:
    """
    csvreader = CsvReader()
    cnkisearch = CnkiSearch()
    sqlmanager = SqlUrlManager()
    for item in csvreader.csv_read():
        # item['drugid'] = csvreader.csv_read()['drugid']
        # item['search'] = csvreader.csv_read()['search']
        for data in cnkisearch.do_search(keyword=item['search']):
            item['title'] = data['title']
            item['title_url'] = data['title_url']
            item['authors'] = data['authors']
            item['periodical'] = data['periodical']
            item['publication_date'] = data['publication_date']
            item['cited'] = data['cited']
            item['download'] = data['download']
            sqlmanager.save_url(item)


if __name__ == "__main__":
    run_step1()
