#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
雅迪智行 每日签到  —— 青龙面板脚本
来源: https://github.com/qd-today/templates/blob/master/雅迪智行每日签到.har
cron: 30 7 * * *
new Env('雅迪智行每日签到');
环境变量: YADEA_TOKEN   (Bearer 后面的那串 token，多账号用 & 或换行分隔)
依赖: requests  (+ pycryptodome 或 cryptography)
"""
import os
import re
import json
import time
import base64
import urllib.parse

import requests

try:
    from Crypto.Cipher import AES  # pycryptodome
except ImportError:  # 回退
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

    class AES:  # noqa: N801  —— 兼容垫片
        MODE_ECB = 'ECB'

        @staticmethod
        def new(key, mode, **kw):
            return _CryptographyAES(key)


class _CryptographyAES:
    def __init__(self, key):
        self._key = key

    def encrypt(self, data):
        from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
        c = Cipher(algorithms.AES(self._key), modes.ECB()).encryptor()
        return c.update(data) + c.finalize()

    def decrypt(self, data):
        from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
        c = Cipher(algorithms.AES(self._key), modes.ECB()).decryptor()
        return c.update(data) + c.finalize()


AES_KEY = b'RFC1J02e116b45a0'          # 16 字节 -> AES-128-ECB
GATEWAY_APP_ID = 'cfb00038ddac4c9ebc85821694bbd3fa'
BASE = 'https://tspapph5.yadeaiot.com.cn/prod-wg/api/app/userappruleinfo'
UA = ('Mozilla/5.0 (iPhone; CPU iPhone OS 18_7 like Mac OS X) AppleWebKit/605.1.15 '
      '(KHTML, like Gecko) Mobile/15E148 YadeaApp/8.8.10')


# ---------------- 加密工具 ----------------
def _pkcs7_pad(data: bytes) -> bytes:
    n = 16 - len(data) % 16
    return data + bytes([n]) * n


def _pkcs7_unpad(data: bytes) -> bytes:
    if not data:
        return data
    n = data[-1]
    return data[:-n] if 1 <= n <= 16 else data


def aes_encrypt(text: str) -> str:
    cipher = AES.new(AES_KEY, AES.MODE_ECB)
    return base64.b64encode(cipher.encrypt(_pkcs7_pad(text.encode('utf-8')))).decode()


def aes_decrypt(b64: str) -> str:
    cipher = AES.new(AES_KEY, AES.MODE_ECB)
    raw = base64.b64decode(b64)
    return _pkcs7_unpad(cipher.decrypt(raw)).decode('utf-8', 'ignore')


def decrypt_resp(text: str) -> str:
    """响应体是 urlencode 过的 base64 密文"""
    text = urllib.parse.unquote(text.strip().strip('"'))
    text = text.replace(' ', '+') if '\n' in text else text
    return aes_decrypt(text)


# ---------------- 网络请求 ----------------
def make_headers(token: str) -> dict:
    ts = str(int(time.time() * 1000))          # 13 位毫秒 = 16位微秒戳的前13位
    sign = aes_encrypt('gatewayTimestamp=%s&json={}' % ts)
    return {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'zh-CN,zh-Hans;q=0.9',
        'Authorization': 'Bearer %s' % token,
        'Content-Type': 'x-www-form-urlencoded;charset=utf-8',
        'Origin': 'https://tspapph5.yadeaiot.com.cn',
        'Referer': 'https://tspapph5.yadeaiot.com.cn/',
        'User-Agent': UA,
        'gatewayAppId': GATEWAY_APP_ID,
        'gatewayTimestamp': ts,
        'gatewaySign': sign,
    }


def _pick(data: dict, key):
    """兼容数据在顶层或 data 字段里"""
    if key in data:
        return data.get(key)
    d = data.get('data') or {}
    return d.get(key)


def check_in(token: str, index: int):
    tag = '【账号%d】' % index
    s = requests.Session()

    # 1. 签到
    try:
        r = s.get(BASE + '/addsigninbyuseridNew', headers=make_headers(token), timeout=20)
        sign_msg = ''
        code = ''
        try:
            j = json.loads(decrypt_resp(r.text))
            code = str(_pick(j, 'code') or '')
            sign_msg = str(_pick(j, 'msg') or '')
        except Exception:
            m = re.search(r'msg\\?"?\s*:\s*\\?"?([^"\\]+)', r.text)
            sign_msg = m.group(1) if m else r.text[:80]
        if code and code not in ('000000', '120168'):
            print('%s签到失败: %s (%s)' % (tag, sign_msg or '未知', code))
        else:
            print('%s签到: %s' % (tag, sign_msg or '已提交'))
    except Exception as e:
        print('%s签到请求异常: %s' % (tag, e))

    # 2. 查询积分概况
    try:
        r = s.get(BASE + '/queryuserappruleinfobyuserid', headers=make_headers(token), timeout=20)
        body = decrypt_resp(r.text)
        try:
            j = json.loads(body)
        except Exception:
            j = {}
        integral = _pick(j, 'integral')
        signin_day = _pick(j, 'signinDay')
        is_signin = _pick(j, 'isSignin')
        nick = _pick(j, 'nickName')
        uid = _pick(j, 'userId')
        if integral is None:  # 兜底正则
            g = lambda k: (re.search(k + r'\\?"?\s*:\s*\\?"?([^"\\,}]+)', body) or [None, None])[1]
            integral, signin_day = g('integral'), g('signinDay')
            is_signin, nick, uid = g('isSignin'), g('nickName'), g('userId')
        if integral is None:
            print('%s积分查询失败: %s' % (tag, _pick(j, 'msg') or body[:100]))
            return
        state = '今日已签到' if str(is_signin) == '0' else '今日未签到'
        print('%s用户: %s（ID: %s）｜总积分 %s 分｜连续签到 %s 天｜%s'
              % (tag, nick, uid, integral, signin_day, state))
    except Exception as e:
        print('%s积分查询异常: %s' % (tag, e))


def main():
    raw = (os.getenv('YADEA_TOKEN') or os.getenv('yadea_token') or '').strip()
    if not raw:
        print('未找到环境变量 YADEA_TOKEN，请先添加后再运行')
        return
    tokens = [t.strip() for t in re.split(r'[\n&,;]', raw) if t.strip()]
    print('共 %d 个账号' % len(tokens))
    for i, t in enumerate(tokens, 1):
        check_in(t, i)


if __name__ == '__main__':
    main()
