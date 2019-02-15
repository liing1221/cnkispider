# -*- coding: utf-8 -*-
"""
    @Project     : cnkispider
    @File        : test.py
    @Create_Date : 2019-02-15 12:03
    @Update_Date : 2019-02-15 12:03
    @Author      : liing
    @Email       : liing1221@163.com
    @Software    : PyCharm
"""
from urllib.parse import urlparse, urlunparse, unquote, parse_qs

#时间
url1 = 'http://kns.cnki.net/kns/brief/brief.aspx?pagename=ASP.brief_default_result_aspx&isinEn=1&dbPrefix=SCDB&dbCatalog=%e4%b8%ad%e5%9b%bd%e5%ad%a6%e6%9c%af%e6%96%87%e7%8c%ae%e7%bd%91%e7%bb%9c%e5%87%ba%e7%89%88%e6%80%bb%e5%ba%93&ConfigFile=SCDBINDEX.xml&research=off&t=1550203089683&keyValue=%E5%B9%BD%E9%97%A8%E8%9E%BA%E6%97%8B%E6%9D%86%E8%8F%8C&S=1&sorttype= HTTP/1.1'
# 引用
url2 = 'http://kns.cnki.net/kns/brief/brief.aspx?pagename=ASP.brief_default_result_aspx&isinEn=1&dbPrefix=SCDB&dbCatalog=%e4%b8%ad%e5%9b%bd%e5%ad%a6%e6%9c%af%e6%96%87%e7%8c%ae%e7%bd%91%e7%bb%9c%e5%87%ba%e7%89%88%e6%80%bb%e5%ba%93&ConfigFile=SCDBINDEX.xml&research=off&t=1550203089683&keyValue=%E5%B9%BD%E9%97%A8%E8%9E%BA%E6%97%8B%E6%9D%86%E8%8F%8C&S=1&sorttype=(%e8%a2%ab%e5%bc%95%e9%a2%91%e6%ac%a1%2c%27INTEGER%27)+desc&queryid=4 HTTP/1.1'
# 相关
url3 = 'http://kns.cnki.net/kns/brief/brief.aspx?pagename=ASP.brief_default_result_aspx&isinEn=1&dbPrefix=SCDB&dbCatalog=%e4%b8%ad%e5%9b%bd%e5%ad%a6%e6%9c%af%e6%96%87%e7%8c%ae%e7%bd%91%e7%bb%9c%e5%87%ba%e7%89%88%e6%80%bb%e5%ba%93&ConfigFile=SCDBINDEX.xml&research=off&t=1550208222407&keyValue=%E5%B9%BD%E9%97%A8%E8%9E%BA%E6%97%8B%E6%9D%86%E8%8F%8C&S=1&sorttype=(FFD%2c%27RANK%27)+desc&queryid=1 HTTP/1.1'
# 下载
url4 = 'http://kns.cnki.net/kns/brief/brief.aspx?pagename=ASP.brief_default_result_aspx&isinEn=1&dbPrefix=SCDB&dbCatalog=%e4%b8%ad%e5%9b%bd%e5%ad%a6%e6%9c%af%e6%96%87%e7%8c%ae%e7%bd%91%e7%bb%9c%e5%87%ba%e7%89%88%e6%80%bb%e5%ba%93&ConfigFile=SCDBINDEX.xml&research=off&t=1550208222407&keyValue=%E5%B9%BD%E9%97%A8%E8%9E%BA%E6%97%8B%E6%9D%86%E8%8F%8C&S=1&sorttype=(%e4%b8%8b%e8%bd%bd%e9%a2%91%e6%ac%a1%2c%27INTEGER%27)+desc&queryid=3 HTTP/1.1'

par1 = urlparse(url1)
quo1 = unquote(url1)
print('par1>>', par1)
query = par1.query
print('query>>', query)
print(parse_qs(query))
# print('par1>>', urlunparse(url1))
print('quo1>>', quo1)
