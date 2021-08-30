#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
__title__ = '初始化数据库(每次配置新环境时运行)'
__author__ = 'aconda'
__mtime__ = '2021/8/29'
"""
import json
import time
from time import sleep

import requests

from config import mod_config
from logs.logs_manager import add_error_logs
from mongo_db.mongodb_manager import DBManager


def check_code_in_300(code):
    if code.startswith("30"):
        if mod_config.get_custom_config("custom", "300_switch") == "on":
            return True
        else:
            return False
    else:
        return True


def check_code_in_688(code):
    if code.startswith("68"):
        if mod_config.get_custom_config("custom", "688_switch") == "on":
            return True
        else:
            return False
    else:
        return True


def check_code(code):
    return check_code_in_300(code) and check_code_in_688(code)


def init_stock_info_list():
    """
    初始化股票信息列表，数据来源东方财富
    :return:股票列表，包含股票名称和股票编码
    """
    stock_infos = []
    stock_codes = []
    for stock_info_item in get_stock_info_list_by_hushen():
        stock_infos.append(stock_info_item)
        stock_codes.append(stock_info_item.get("code"))

    for stock_info_item in get_stock_info_list_by_shangzheng():
        if stock_info_item.get("code") not in stock_codes:
            stock_infos.append(stock_info_item)

    for stock_info_item in get_stock_info_list_by_new():
        if stock_info_item.get("code") not in stock_codes:
            stock_infos.append(stock_info_item)

    for stock_info_item in get_stock_info_list_by_chuangye():
        if stock_info_item.get("code") not in stock_codes:
            stock_infos.append(stock_info_item)

    for stock_info_item in get_stock_info_list_by_kechuang():
        if stock_info_item.get("code") not in stock_codes:
            stock_infos.append(stock_info_item)
    return stock_infos


def get_stock_info_list_by_hushen():
    """
    获取沪深A股股票列表
    :return:股票列表，包含股票名称和股票编码
    """
    url = "f3&fs=m:0+t:6,m:0+t:80,m:1+t:2,m:1+t:23"
    return get_request_result(url)


def get_stock_info_list_by_shangzheng():
    """
    获取上证A股股票列表
    :return:股票列表，包含股票名称和股票编码
    """
    url = "f3&fs=m:1+t:2,m:1+t:23"
    return get_request_result(url)


def get_stock_info_list_by_shenzheng():
    """
    获取深证A股股票列表
    :return:股票列表，包含股票名称和股票编码
    """
    url = "f3&fs=m:0+t:6,m:0+t:80"
    return get_request_result(url)


def get_stock_info_list_by_new():
    """
    获取新股股票列表
    :return:股票列表，包含股票名称和股票编码
    """
    url = "f26&fs=m:0+f:8,m:1+f:8"
    return get_request_result(url)


def get_stock_info_list_by_chuangye():
    """
    获取创业板股票列表
    :return:股票列表，包含股票名称和股票编码
    """
    url = "f3&fs=m:0+t:80"
    return get_request_result(url)


def get_stock_info_list_by_kechuang():
    """
    获取科创板股票列表
    :return:股票列表，包含股票名称和股票编码
    """
    url = "f3&fs=m:1+t:23"
    return get_request_result(url)


def get_request_result(url):
    """
    请求接口地址，默认重试8次
    :param url:请求地址
    :return:接口返回内容
    """
    times = str(round(time.time() * 1000))
    jquery = "jQuery112404956352472222245_1630205940247"
    base_url = "http://54.push2.eastmoney.com/api/qt/clist/get?cb={jquery}&pn=1&pz" \
               "=100000&po=1&np=1&ut=bd1d9ddb04089700cf9c27f6f7426281&fltt=2&invt=2&fid={url}&fields=f1,f2,f3,f4,f5," \
               "f6,f7,f8,f9,f10,f11,f12,f13,f14,f15,f16,f17,f18,f20,f21,f22,f23,f24,f25,f26,f62,f128,f136,f115," \
               "f152&_={times}".format(jquery=jquery, url=url, times=times)
    max_try = 8
    for tries in range(max_try):
        try:
            content = requests.get(base_url)
            return parse_pager(content.content, jquery)
        except Exception:
            if tries < (max_try - 1):
                sleep(2)
                continue
            else:
                add_error_logs("get_request_result error", "501", "key")


def parse_pager(content, jquery):
    stock_infos = []
    start_index = len(jquery) + 1
    end_index = len(content) - 2
    content_result = content[start_index: end_index]
    content_json = json.loads(content_result)
    content_data = content_json.get("data")
    for item in content_data.get("diff"):
        code, name = item.get("f12"), item.get("f14")
        if name.find("ST") < 0 and check_code(code):
            stock_infos.append({"code": code, "name": name, "price_list": []})
    return stock_infos


def get_stock_code(item):
    return item.get("code")


if __name__ == '__main__':
    dm = DBManager("tk_details")
    dm.drop()
    stock_info_list = init_stock_info_list()
    stock_info_list.sort(key=get_stock_code)
    for stock_info in stock_info_list:
        dm.add_one(stock_info)
