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
from urllib.parse import urlencode, urljoin
from fake_useragent import UserAgent
from logmanage import LogManager
from proxymanage import ProxyManager
from sqlmanage import SqlUrlManager

logger = LogManager(level=30)


class CnkiSearch:
    """
    通过知网检索入口以及检索关键字，检索获取文献列表:获取文献列表信息以及url
    :知网登陆检索流程：get请求初始化cookie,post请求进行注册检索信息，再get请求查询结果
    """
    def __init__(self,proxies=True):
        """
        初始化搜索url,headers以及cookies
        """
        self.retries = 5
        self.timeout = 20
        self.user_agent = UserAgent().chrome
        self.s = requests.Session()
        self.proxy_manager = ProxyManager(pool=False)
        if proxies:
            ip, port = self.proxy_manager.get_proxy()
            self.proxies = {
                'https': 'http://{}:{}'.format(ip, port),
                'http': 'http://{}:{}'.format(ip, port)
            }
        else:
            self.proxies = None
        self.base_url = "http://kns.cnki.net/kns/brief/default_result.aspx"
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

    def get_param(self, keyword, sortkey=None):
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
                "sorttype": ' ' #HTTP/1.1'
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
        :param url: 登录接口请求
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

    def post_second(self, keyword):
        """
        第二次post请求入口页:post注册提交查询字符串，获取查询结果链接字符串
        :param keyword: 检索关键字
        :return:
        """
        header = {"Accept": "*/*",
                  # "Content-Length": "519",
                  "Content-Type": "application/x-www-form-urlencoded",
                  "Origin": "http://kns.cnki.net",
                  # "Proxy-Connection": "keep-alive"
                  }
        headers = self.headers.update(header)
        params = {
            "action": '',
            "ua": "1.11",
            "isinEn": "1",
            "PageName": "ASP.brief_default_result_aspx",
            "DbPrefix": "SCDB",
            "DbCatalog": "中国学术文献网络出版总库",
            "ConfigFile": "SCDBINDEX.xml",
            "db_opt": "CJFQ, CDFD, CMFD, CPFD, IPFD, CCND, CCJD",
            "txt_1_sel": "SU$%=|",
            "txt_1_value1": keyword,
            "txt_1_special1": "%",
            "his": "0",
            "parentdb": "SCDB",
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
        while retry > 0:
            retry -= 1
            header = {
                "Referer": "http://kns.cnki.net/kns/brief/default_result.aspx"}
            headers = self.headers.update(header)
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
                print('status_code>>', response.status_code)
                if response.status_code == 200 and response:
                    return response
                if response.status_code == 403:
                    print(
                        'Error occur in function : {} whith response.atatus_code == 403;\n{}'.format(
                            self.get_third.__name__, locals()))
                    continue
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
        print(response.text)
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

    def do_search(self, keyword, sortkey=None):
        """
        整体执行类功能：构造查询url,并请求网页
        :param keyword:  检索的关键字
        :param sortkey:  检索结果的排序方式
        :return:
        """
        self.get_first()
        query = self.post_second(keyword=keyword)
        # params = self.get_param(keyword=keyword)
        url = "http://kns.cnki.net/kns/brief/brief.aspx?pagename=" + query
        # url = "http://kns.cnki.net/kns/brief/brief.aspx?pagename=" + params
        response = self.get_third(url)
        response.encoding = 'utf-8'
        for item in self.parse_url(response):
            yield item


if __name__ == "__main__":
    cnkisearch = CnkiSearch()
    sqlmanager = SqlUrlManager()
    for item in cnkisearch.do_search("幽门螺旋杆菌"):
        print(item)
        # sqlmanager.save_url(item)

# http://kns.cnki.net/kns/brief/brief.aspx?curpage=3&RecordsPerPage=20&QueryID=1&ID=&turnpage=1&tpagemode=L&dbPrefix=SCDB&Fields=&DisplayMode=listmode&PageName=ASP.brief_default_result_aspx&isinEn=1 HTTP/1.1
#
# http://kns.cnki.net/kns/brief/brief.aspx?pagename=ASP.brief_default_result_aspx&isinEn=1&dbPrefix=SCDB&dbCatalog=%e4%b8%ad%e5%9b%bd%e5%ad%a6%e6%9c%af%e6%96%87%e7%8c%ae%e7%bd%91%e7%bb%9c%e5%87%ba%e7%89%88%e6%80%bb%e5%ba%93&ConfigFile=SCDBINDEX.xml&research=off&t=1550635280753&keyValue=%E5%B9%BD%E9%97%A8%E8%9E%BA%E6%97%8B%E6%9D%86%E8%8F%8C&S=1&sorttype= HTTP/1.1


