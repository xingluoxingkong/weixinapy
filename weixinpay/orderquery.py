import json
import logging
import requests
from .wx_utils import getRandomStr, createSign, decodeXML, encodeXML, post

__all__ = ['Orderquery']

# 接口地址
_URL = 'https://api.mch.weixin.qq.com/pay/orderquery'
_log = logging.getLogger()


class Orderquery(object):

    def __init__(self, appid, mch_id, key):
        ''' 该接口提供所有微信支付订单的查询，商户可以通过查询订单接口主动查询订单状态，完成下一步的业务逻辑。
        --
            @param appid: 微信分配的小程序ID
            @param mch_id: 微信支付分配的商户号
            @param key: key设置路径：微信商户平台(pay.weixin.qq.com)-->账户设置-->API安全-->密钥设置
        '''
        self.values = {}
        self.values['appid'] = appid
        self.values['mch_id'] = mch_id
        self.key = key
        self.sign_type = 'MD5'

    def setSignType(self, sign_type='MD5'):
        ''' 签名类型
        --
            @param sign_type: 签名类型['MD5', 'HMAC-SHA256']
        '''
        if sign_type != 'MD5' or sign_type != 'HMAC-SHA256':
            raise Exception('只能是HMAC-SHA256或MD5')

        self.sign_type = sign_type
        return self

    def query(self, transaction_id=None, out_trade_no=None):
        '''发起查询请求
        --
            以下参数二选一：
                @param transaction_id: 微信的订单号，建议优先使用
                @param out_trade_no: 商户系统内部订单号，要求32个字符内，只能是数字、大小写字母_-|*@ ，且在同一个商户号下唯一
        '''
        if not transaction_id and not out_trade_no:
            raise Exception('transaction_id和out_trade_no必须有一个')

        if transaction_id:
            self.values['transaction_id'] = transaction_id
        else:
            self.values['out_trade_no'] = out_trade_no

        # 随机数
        self.values['nonce_str'] = getRandomStr()
        # 生成签名
        sign = createSign(self.values, self.key, self.sign_type)
        self.values['sign'] = sign
        if self._checkValues():
            xmlStr = decodeXML(self.values)
            res1 = post(_URL, xmlStr)
            res2 = encodeXML(res1)
            if self._checkValues(res2):
                return res2
            else:
                _log.error('用户请求支付失败，返回结果：%s' % res2)
                return '返回参数校验不通过或者请求失败!'
        else:
            return '参数不合法，请检查请求参数！'

    def _checkValues(self, values=None):
        ''' 检查参数是否合法
        --
        :param values:如果为空检查请求参数，否则检查返回参数
        '''
        if values:
            if values['return_code'] == 'SUCCESS':
                v = values.copy()
                sign = v.pop('sign')
                sign2 = createSign(v, self.key, self.sign_type)
                if sign2 == sign:
                    return True
                else:
                    return False
        else:
            if all(k in self.values for k in ('appid', 'mch_id', 'nonce_str', 'sign')):
                if 'transaction_id' in self.values:
                    return True
                elif 'out_trade_no' in self.values:
                    return True

        return False
