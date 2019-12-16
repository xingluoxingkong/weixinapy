import base64
import hashlib
from Crypto.Cipher import AES
from .wx_utils import decodeXML

__all__ = ['refundDecode']

class refundDecode(object):
    def __init__(self, key):
        ''' 退款回调解密
        '''
        self.key = key
        
    def decode(self, req_info):
        mima_b = base64.b64decode(req_info)
        key2 = hashlib.md5(self.key.encode('utf-8')).hexdigest()

        aes = AES.new(str.encode(key2), AES.MODE_ECB)
        text = str(aes.decrypt(mima_b).rstrip(b'\0').decode("utf8"))

        return decodeXML(text)