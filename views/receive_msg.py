
from flask import jsonify, request
from . import receive_view
from decorators import wx_logined
from global_val import *
import time
import re
import json


@receive_view.route('/get-msg')
def receive_msg():
    global wxSession
    global wx_DeviceID
    syn_list = []
    for item in wx_syncKey.get('List'):
        temp = '%s_%s' % (item['Key'], item['Val'])
        syn_list.append(temp)
    syncKey = '|'.join(syn_list)
    # 监听是否有新消息
    # https://webpush.wx2.qq.com/cgi-bin/mmwebwx-bin/synccheck?
    url = 'https://webpush.wx2.qq.com/cgi-bin/mmwebwx-bin/synccheck'
    res = wxSession.get(
        url=url,
        params={
            'r': str(time.time()),
            'skey': wx_ticket_dict['skey'],
            'sid': wx_ticket_dict['wxsid'],
            'uin': wx_ticket_dict['wxuin'],
            'deviceid': wx_DeviceID,
            'synckey': syncKey,
            '_': str(time.time())
        }
    )
    res_status = re.findall('selector:"([0-9]+)"', res.text)[0]
    if res_status == '0':
        res_msg = {
            'code': 0
        }
        return jsonify(res_msg)
    else:
        # 有新消息，需要更新synckey
        # https://wx2.qq.com/cgi-bin/mmwebwx-bin/webwxsync?
        url1 = 'https://wx2.qq.com/cgi-bin/mmwebwx-bin/webwxsync'
        res1 = wxSession.post(
            url=url1,
            params={
                'sid': wx_ticket_dict['wxsid'],
                'skey': wx_ticket_dict['skey']
            },
            json={
                'BaseRequest':{
                    'DeviceID': wx_DeviceID,
                    'Sid': wx_ticket_dict['wxsid'],
                    'Skey': wx_ticket_dict['skey'],
                    'Uin': wx_ticket_dict['wxuin']
                },
                'SyncKey': wx_syncKey,
                'rr': -12345
            }
        )
        res1.encoding = 'utf-8'
        res_data = json.loads(res1.text)
        # 更新ｓｙｎｃＫｅｙ
        wx_syncKey.update(res_data.get('SyncKey'))
        # 获取新消息
        global wx_friends
        msgs = [
            {
                'FromUser': msg.get('FromUserName'),
                'FromUserNickName': wx_friends.get(msg.get('FromUserName')),
                'ToUser': msg.get('ToUserName'),
                'ToUserNickName': wx_friends.get(msg.get('ToUserName')),
                'Content': msg.get('Content')
            } for msg in res_data.get('AddMsgList') if msg.get('FromUserName') != wx_user_info.get('UserName')
        ]
        res_msg = {
            'code': 2,
            'msgs': msgs
        }
        return jsonify(res_msg)

