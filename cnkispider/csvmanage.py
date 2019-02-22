# -*- coding: utf-8 -*-
"""
    @Project     : drugspider
    @File        : csv_read.py
    @Create_Date : 2018-12-26 14:11
    @Update_Date : 2018-12-26 14:11
    @Author      : liing
    @Email       : liing1221@163.com
    @Site        :
    @Software    : PyCharm
"""
import csv


class CsvReader:
    def __init__(self):
        self.csv_file = './drug_cost_search.csv'

    def csv_read(self):
        """
        utf-8与utf-8-sig两种编码格式的区别:UTF-8以字节为编码单元，它的字节顺序在所有系统中都是一様的，
        没有字节序的问题，也因此它实际上并不需要BOM(“ByteOrder Mark”)。但是UTF-8 with BOM即
        utf-8-sig需要提供BOM.
        \ufeff(字节顺序标记):(英语:byte-order mark，BOM）是位于码点U+FEFF的统一码字符的名称。当以
        UTF-16或UTF-32来将UCS/统一码字符所组成的字符串编码时，这个字符被用来标示其字节序。它常被用来当
        做标示文件是以UTF-8、UTF-16或UTF-32编码的记号。
        :return:
        """
        with open(self.csv_file, 'r', encoding='UTF-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:        # row为collections.OrderedDict()对象，有序字典
                yield row


if __name__ == '__main__':
    csvreader = CsvReader()
    for i in csvreader.csv_read():
        print(i['drugid'], i['search'])