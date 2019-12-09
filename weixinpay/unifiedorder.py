import json
import time
import logging
import requests
from .wx_utils import getRandomStr, createSign, decodeXML, encodeXML, post

__all__ = ['Unifiedorder']

# 接口地址
_URL = 'https://api.mch.weixin.qq.com/pay/unifiedorder'
_log = logging.getLogger()


class Unifiedorder(object):

    def __init__(self, appid, mch_id, key):
        ''' 商户在小程序中先调用该接口在微信支付服务后台生成预支付交易单，返回正确的预支付交易后调起支付。
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

    def setDeviceInfo(self, device_info):
        ''' 自定义参数，可以为终端设备号(门店号或收银设备ID)，PC网页或公众号内支付可以传"WEB"
        --
        '''
        self.values['device_info'] = device_info
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

    def setBody(self, body=''):
        ''' 商品简单描述，该字段请按照规范传递
        --
        '''
        self.values['body'] = body
        return self

    def setDetail(self, detail=''):
        ''' 商品详细描述，对于使用单品优惠的商户，该字段必须按照规范上传
        --
        '''
        self.values['detail'] = detail
        return self

    def setAttach(self, attach=''):
        ''' 附加数据，在查询API和支付通知中原样返回，可作为自定义参数使用
        --
        '''
        self.values['attach'] = attach
        return self

    def setFeeType(self, fee_type='CNY'):
        ''' 符合ISO 4217标准的三位字母代码，默认人民币：CNY
        --
        '''
        self.values['fee_type'] = fee_type
        return self

    def setGoodsTag(self, goods_tag=''):
        ''' 订单优惠标记，使用代金券或立减优惠功能时需要的参数
        --
        '''
        self.values['goods_tag'] = goods_tag
        return self

    def noCredit(self):
        ''' 不允许使用信用卡。默认允许使用
        --
        '''
        self.values['limit_pay'] = 'no_credit'
        return self

    def useCredit(self):
        ''' 允许使用信用卡，默认值
        --
        '''
        self.values['limit_pay'] = ''
        return self

    def receipt(self):
        ''' 支付成功消息和支付详情页将出现开票入口。需要在微信支付商户平台或微信公众平台开通电子发票功能，才可生效。默认不开启
        --
        '''
        self.values['receipt'] = 'Y'
        return self

    def noReceipt(self):
        ''' 不提供开票入口，默认值
        --
        '''
        self.values['receipt'] = ''
        return self

    def pay(self, total_fee, out_trade_no, body, spbill_create_ip, notify_url, trade_type='JSAPI', openid='', product_id='', time_start='', time_expire='', scene_info=''):
        '''发起支付请求
        --
            @param total_fee: 支付金额,单位分
            @param out_trade_no: 商户订单号
            @param body: 商品描述
            @param spbill_create_ip: 终端ip
            @param notify_url: 回调地址
            @param trade_type: 交易类型，默认小程序
            @param openid: trade_type=JSAPI，此参数必传
            @param product_id: trade_type=NATIVE时，此参数必传。此参数为二维码中包含的商品ID，商户自行定义
            @param time_start: 交易开始时间，非必填
            @param time_expire: 交易结束时间，非必填
            @param scene_info： 该字段常用于线下活动时的场景信息上报，支持上报实际门店信息，商户也可以按需求自己上报相关信息。该字段为JSON对象数据，对象格式为{"store_info":{"id": "门店ID","name": "名称","area_code": "编码","address": "地址" }}
        '''
        if trade_type == 'JSAPI' and openid == '':
            raise Exception('trade_type=JSAPI，openid必传')
        if trade_type == 'NATIVE' and product_id == '':
            raise Exception(' trade_type=NATIVE时，product_id必传')

        self.values['total_fee'] = total_fee
        self.values['out_trade_no'] = out_trade_no
        self.values['body'] = body
        self.values['spbill_create_ip'] = spbill_create_ip
        self.values['notify_url'] = notify_url
        self.values['trade_type'] = trade_type
        self.values['openid'] = openid
        self.values['product_id'] = product_id
        self.values['time_start'] = time_start
        self.values['time_expire'] = time_expire
        self.values['scene_info'] = scene_info

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
                return _reSign(res2)
            else:
                _log.error('用户请求支付失败，返回结果：%s' % res2)
                return '返回参数校验不通过或者请求失败!'
        else:
            return '参数不合法，请检查请求参数！'

    def _reSign(self, res):
        ''' 二次签名
        --
        '''
        re = {}
        re['appId'] = res['appid']
        re['timeStamp'] = int(time.time())
        re['package'] = 'prepay_id=' + res['prepay_id']
        re['signType'] = self.sign_type
        re['nonceStr'] = getRandomStr()
        sign = createSign(re, self.key, self.sign_type)
        re['paySign'] = sign
        return re

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
            if all(k in self.values for k in ('appid', 'mch_id', 'nonce_str', 'body', 'out_trade_no', 'total_fee', 'spbill_create_ip', 'notify_url', 'trade_type', 'sign')):
                if self.values['trade_type'] == 'NATIVE':
                    if 'product_id' in self.values:
                        return True
                    else:
                        return False
                if self.values['trade_type'] == 'JSAPI':
                    if 'openid' in self.values:
                        return True
                    else:
                        return False

        return False
