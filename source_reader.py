# -*- coding: utf-8 -*-

import requests
"""
这里定义获取url对应源码的模块
每个模块都必须实现get_page_source方法, 用于获取页面源码
"""

common_headers = {
    'User-Agent':
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:67.0) Gecko/20100101 Firefox/67.0'
}


class HTTPReader:
    """
    直接发起HTTP请求, 直接从Response中读取网页源码
    这个类用于处理一次HTTP请求就返回全部网页源码的情况
    """

    def __init__(self, url):
        self.url = url
        self.__connect()

    def __connect(self):
        self.response = requests.get(self.url, headers=common_headers)

    def get_page_source(self):
        return self.response.text


class SeleniumReader:
    """
    从Selenium读取网页源码,为了应对有的网页内容是从js中加载的问题
    """
    
    def __init__(self, url):
        self.url = url
        pass

    def __connect(self):
        pass

    def get_page_source(self):
        return ""


class FileReader:
    """
    从文件中读取源码, 这个class主要用来测试, 避免每次调试都要访问一次页面
    """
    def __init__(self, url):
        self.filename = "./examples/ldoce.html"
        self.__connect()

    def __connect(self):
        with open(self.filename, 'r', 1, 'utf-8') as f:
           self.source_text = ''.join(f.readlines())

    def get_page_source(self):
        return self.source_text