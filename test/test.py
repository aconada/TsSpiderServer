#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试专用
"""
import os

import pandas as pd
import tushare as ts

# import pandas_datareader.data as web

DATA_DIR = 'E:/temp/test'
if not os.path.exists(DATA_DIR):
    os.mkdir(DATA_DIR)


def download_tushare(datadir, code, dtype, start):
    print('download: %s' % code)
    path = os.path.join(datadir, code + '_ts.csv')
    df = ts.get_hist_data(code, start=start)
    df.to_csv(path, encoding='gbk')
    return path


if __name__ == '__main__':
    path = download_tushare(DATA_DIR, '600516', 'sz', '2021-01-01')
    df = pd.read_csv(path, encoding='gbk')
    df.tail()
