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
import requests
import traceback
from urllib.parse import urlencode, urljoin
from fake_useragent import UserAgent
from logmanage import LogManager
from proxymanage import ProxyManager

logger = LogManager(level=30)

class CnkiSearch:
    """
    通过知网检索入口以及检索关键字，检索获取文献列表:获取文献列表信息以及url
    """
    def __init__(self):
        """
        初始化搜索url,headers以及cookies
        """
        self.cookie = {"Ecp_ClientId": "6190215172201124902",
                       "Ecp_IpLoginFail": "190215124.202.241.162",
                       "ASP.NET_SessionId": "mdotc5f4ww5zygtbyaf035lh",
                       "SID_kns": "123124",
                       # "RsPerPage": "20",      # 可省
                       # "cnkiUserKey": "05a9e126-4d9f-5f86-eadd-95116a35129b",  # 可省
                       # "SID_klogin": "125144",
                       # "SID_crrs": "125132",
                       # "SID_krsnew": "125132", # 可省
                       # "KNS_SortType": '',
                       # "_pk_ses": "*"          # 可省
        }
        self.timeout = 20
        self.retries = 5
        self.search_url = 'http://kns.cnki.net/kns/brief/brief.aspx?'
        self.header = {
            "Host": "kns.cnki.net",
            "Connection": "keep-alive",
            "Cache-Control": "max-age=0",
            "Upgrade-Insecure-Requests": "1",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Accept-Encoding": "gzip,deflate",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "User-Agent": UserAgent().random
        }
        self.proxy_manager = ProxyManager(pool=False)
        self.s = requests.Session()

    def get_param(self, keyword, sortkey=None):
        """
        初始化请求参数:检索关键字keyword，以及结果列表的排列方式sortkey,sortkey取值:引用排序——"(被引频次,'INTEGER') desc",
        相关性排序——"(FFD,'RANK') desc",下载排序——"(下载频次,'INTEGER') desc", 默认排序——' HTTP/1.1'无queryid参数
        :param keyword:
        :return:
        """
        if not sortkey:
            params = {
                "pagename": "ASP.brief_default_result_aspx",
                "isinEn": "1",
                "dbPrefix": "SCDB",
                "dbCatalog": "中国学术文献网络出版总库",
                "ConfigFile": "SCDBINDEX.xml",
                "research": "off",
                "t": "1550209057868",
                "keyValue": keyword,
                "S": "1",
                "sorttype": ' HTTP/1.1'
            }
        else:
            params = {
                "pagename": "ASP.brief_default_result_aspx",
                "isinEn": "1",
                "dbPrefix": "SCDB",
                "dbCatalog": "中国学术文献网络出版总库",
                "ConfigFile": "SCDBINDEX.xml",
                "research": "off",
                "t": "1550209057868",
                "keyValue": keyword,
                "S": "1",
                "sorttype": sortkey,
                "queryid": '4 HTTP/1.1'
            }
        params = urlencode(params)
        return params

    def make_proxy(self):
        """
        构建相互独立的proxies代理
        :return:
        """
        ip, port = self.proxy_manager.get_proxy()
        proxies = {
            'https': 'http://{}:{}'.format(ip, port),
            'http': 'http://{}:{}'.format(ip, port)
        }
        return proxies

    @logger.log_decoratore
    def get_page(self, url):
        """
        根据检索url,请求获取页面
        :param url: 根据查询参数构造的url
        :return: html页面
        """
        retry = self.retries
        while retry > 0:
            retry -= 1
            headers = self.header
            cookie = self.cookie
            # proxies = self.make_proxy()
            try:
                response = self.s.get(
                    url=url,
                    headers=headers,
                    # proxies=proxies,
                    cookies = cookie,
                    timeout=self.timeout,
                )
                print('status_code>>', response.status_code)
                if response.status_code == 200 and response:
                    return response
                if response.status_code == 403:
                    print(
                        'Error occur in function : {} whith response.atatus_code == 403;\n{}'.format(
                            self.get_page.__name__, locals()))
                    continue
            except Exception as e:
                print('*'* 100)
                traceback.print_exc()
                print(
                    'Error occur in function : {} \n{}'.format(
                        self.get_page.__name__,
                        locals()))
                continue

    def do_search(self, keyword, sortkey=None):
        """
        整体执行类功能：构造查询url,并请求网页
        :param keyword:
        :param sortkey:
        :return:
        """
        params = self.get_param(keyword, sortkey= sortkey)
        self.url = self.search_url + params
        print('self.url>>', self.url)
        response = self.get_page(url=self.url)
        print(response.status_code)
        print(response.text)


if __name__ == "__main__":
    cnkisearch = CnkiSearch()
    # params = cnkisearch.get_param("幽门螺旋杆菌")
    # print(params)
    cnkisearch.do_search("幽门螺旋杆菌")