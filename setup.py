#!/usr/bin/env python
# -*- coding:utf-8 -*-

#############################################
# File Name: setup.py
# Author: lijin
# Mail: lijin@dingtalk.com
# Created Time:  2019-12-06
#############################################

from setuptools import setup, find_packages

setup(
    name="weixinpay",
    version="0.0.1",
    keywords=("pip", "pathtool", "timetool", "magetool", "mage"),
    description="微信支付",
    long_description="微信支付",
    license="MIT Licence",

    url="https://github.com/l616769490/weixinapy",
    author="lijin",
    author_email="lijin@dingtalk.com",

    packages=find_packages(),
    include_package_data=True,
    platforms="any",
    install_requires=[]
)
