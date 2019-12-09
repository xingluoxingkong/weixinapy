from .dict2xml import Dict2XML
from .xml2dict import XML2Dict
from random import Random
import requests
import hashlib
import base64
import hmac
import json

__all__ = ['getRandomStr', 'createSign',
           'decodeXML', 'encodeXML', 'post', 'getIp']

_chars = 'AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz0123456789'


def getRandomStr(length=16):
    ''' 获取随机字符串
    --
    '''
    salt = ''
    len_chars = len(_chars) - 1
    random = Random()
    for i in range(length):
        # 每次从chars中随机取一位
        salt += _chars[random.randint(0, len_chars)]
    return salt


def createSign(values, key, sign_type='MD5'):
    ''' 生成签名
    --
        @param values：签名数据
        @param key：签名key
        @param sign_type：签名算法MD5或HMAC-SHA256
    '''
    # 字典序
    sortArr = sorted(values.items(), key=lambda item: item[0])
    signStr = ''
    # 拼接
    for i in sortArr:
        if i[1] != '':
            signStr += str(i[0]) + '=' + str(i[1]) + '&'

    # 最后再拼上key
    signStr += 'key=' + key

    if sign_type == 'MD5':
        # MD5签名
        m2 = hashlib.md5()
        m2.update(signStr.encode('utf-8'))
        return m2.hexdigest().upper()
    elif sign_type == 'HMAC-SHA256':
        appsecret = key.encode('utf-8')  # 秘钥

        data = signStr.encode('utf-8')  # 加密数据
        signature = base64.b64encode(
            hmac.new(appsecret, data, digestmod=hashlib.sha256).digest())
        return signature.upper()


def decodeXML(data, rootName='xml'):
    ''' 字典解析成XML
    --
        @param data
        @param rootName:跟节点名字
    '''
    values = {rootName: {}}
    for k, v in data.items():
        if v:
            if not isinstance(v, str):
                if isinstance(v, list) or isinstance(v, dict) or isinstance(v, tuple):
                    v = json.dumps(v)
                else:
                    v = str(v)
            values[rootName][k] = v
    x = Dict2XML()
    return x.parse(values)


def encodeXML(xmlStr, rootName='xml'):
    ''' XML解析成字典
    -- 
        @param data
        @param rootName:跟节点名字
    '''
    x = XML2Dict()
    res = x.parse(xmlStr)[rootName]
    for k, v in res.items():
        if isinstance(v, bytes):
            res[k] = v.decode('UTF-8')
    return res


def post(url, data):
    ''' 发送post请求
    --
    '''
    r = requests.post(url, data.encode('utf-8'))
    text = r.text.encode(r.encoding).decode('utf-8')
    return text


def getIp(env):
    ''' 从环境中获取ip
    --
    '''
    return env['REMOTE_ADDR']
