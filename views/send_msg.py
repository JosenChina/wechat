
from . import send_view
from flask import jsonify, request
from decorators import wx_logined
from global_val import *
import time
import json


@wx_logined
@send_view.route('/')
def send_msg():
    '''
    发送微信信息
    :return:
    '''
    # https://wx2.qq.com/cgi-bin/mmwebwx-bin/webwxsendmsg?
    global wxSession
    global wx_ticket_dict
    url = 'https://wx2.qq.com/cgi-bin/mmwebwx-bin/webwxsendmsg'
    theTime = str(time.time())
    res = wxSession.post(
        url=url,
        params={
            'lang': 'zh_CN',
            'pass_ticket': wx_ticket_dict['pass_ticket']
        },
        data=json.dumps({
            'BaseRequest': {
                'DeviceID': 'e049563162216481',
                'Sid': wx_ticket_dict['wxsid'],
                'Skey': wx_ticket_dict['skey'],
                'Uin': wx_ticket_dict['wxuin']
            },
            'Msg': {
                'ClientMsgId': theTime,
                'Content': request.args.get('message') ,
                'FromUserName': wx_user_info['UserName'],
                'LocalID': theTime,
                'ToUserName': request.args.get('username'),
                'Type': 1
            },
            'Scene': 0
        }, ensure_ascii=False).encode('utf8')
    )
    res_msg = {
        'ToUserNickName': wx_friends.get(request.args.get('username'))
    }
    return jsonify(res_msg)