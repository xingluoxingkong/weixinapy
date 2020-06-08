import json
import logging
import requests
from .wx_utils import getRandomStr, createSign, decodeXML, encodeXML

__all__ = ['Refund']

# 接口地址
_URL = 'https://api.mch.weixin.qq.com/secapi/pay/refund'
_log = logging.getLogger()


class Refund(object):

    def __init__(self, appid, mch_id, key):
        ''' 当交易发生之后一段时间内，由于买家或者卖家的原因需要退款时，卖家可以通过退款接口将支付款退还给买家，微信支付将在收到退款请求并且验证成功之后，按照退款规则将支付款按原路退到买家帐号上。
        --
            注意，此接口需要证书
            https://pay.weixin.qq.com/wiki/doc/api/jsapi.php?chapter=4_3
            @param appid: 微信分配的小程序ID
            @param mch_id: 微信支付分配的商户号
            @param key: key设置路径：微信商户平台(pay.weixin.qq.com)-->账户设置-->API安全-->密钥设置
        '''
        self.values = {}
        self.values['appid'] = appid
        self.values['mch_id'] = mch_id
        self.key = key
        self.sign_type = 'MD5'

    def setRefundFeeType(self, refund_fee_type='CNY'):
        ''' 符合ISO 4217标准的三位字母代码，默认人民币：CNY
        --
        '''
        self.values['refund_fee_type'] = refund_fee_type
        return self

    def setSignType(self, sign_type='MD5'):
        ''' 签名类型
        --
            @param sign_type: 签名类型['MD5', 'HMAC-SHA256']
        '''
        if sign_type != 'MD5' or sign_type != 'HMAC-SHA256':
            raise Exception('只能是HMAC-SHA256或MD5')

        self.sign_type = sign_type
        return self

    def setRefundDesc(self, refund_desc=''):
        ''' 若商户传入，会在下发给用户的退款消息中体现退款原因
        --
        '''
        self.values['refund_desc'] = refund_desc
        return self

    def setRefundAccount(self, refund_account=''):
        ''' 仅针对老资金流商户使用
                REFUND_SOURCE_UNSETTLED_FUNDS---未结算资金退款（默认使用未结算资金退款）
                REFUND_SOURCE_RECHARGE_FUNDS---可用余额退款
        --
        '''
        self.values['refund_account'] = refund_account
        return self

    def refund(self, out_refund_no, total_fee, refund_fee, transaction_id=None, out_trade_no=None, refund_desc='', notify_url='', cert = './cert.pem', key = './key.pem'):
        '''发起支付请求
        --
            @param out_refund_no: 商户退款单号
            @param total_fee: 订单金额，单位分
            @param refund_fee: 退款金额，单位分
            @param transaction_id: 微信订单号和out_trade_no二选一
            @param out_trade_no: 商户订单号和transaction_id二选一
            @param refund_desc: 退款原因
            @param notify_url: 退款结果通知url
            @param cert, key: 微信支付证书
        '''
        if not transaction_id and not out_trade_no:
            raise Exception('transaction_id和out_trade_no必须有一个')

        if transaction_id:
            self.values['transaction_id'] = transaction_id
        else:
            self.values['out_trade_no'] = out_trade_no

        self.values['out_refund_no'] = out_refund_no
        self.values['total_fee'] = total_fee
        self.values['refund_fee'] = refund_fee
        self.values['refund_desc'] = refund_desc
        self.values['notify_url'] = notify_url

        # 随机数
        self.values['nonce_str'] = getRandomStr()
        # 生成签名
        sign = createSign(self.values, self.key, self.sign_type)
        self.values['sign'] = sign
        if self._checkValues():
            xmlStr = decodeXML(self.values)
            res1 = self._post(_URL, xmlStr, cert, key)
            res2 = encodeXML(res1)
            if self._checkValues(res2):
                return res2
            else:
                _log.error('用户请求支付失败，返回结果：%s' % res2)
                return '返回参数校验不通过或者请求失败!'
        else:
            return '参数不合法，请检查请求参数！'
    
    def _post(self, url, data, cert, key):
        ''' 发送post请求
        --
        '''
        import requests
        r = requests.post(url, data.encode('utf-8'), cert = (cert, key))
        text = r.text.encode(r.encoding).decode('utf-8')
        
        return text

    def _checkValues(self, values=None):
        ''' 检查参数是否合法
        --
        :param values:如果为空检查请求参数，否则检查返回参数
        '''
        if values:
            if values['return_code'] == 'SUCCESS':
                v = values.copy()
                sign = v['sign']
                v.pop('sign')
                sign2 = createSign(v, self.key, self.sign_type)
                if sign2 == sign:
                    return True
                else:
                    return False
        else:
            if all(k in self.values for k in ('appid', 'mch_id', 'nonce_str', 'out_refund_no', 'total_fee', 'refund_fee', 'refund_desc', 'notify_url', 'sign')):
                if 'transaction_id' in self.values or 'out_trade_no' in self.values:
                    return True
                else:
                    return False

        return False
