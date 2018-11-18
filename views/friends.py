
from . import friends_view
from flask import render_template, jsonify
from bs4 import BeautifulSoup
from decorators import wx_logined
from global_val import *
import json


@wx_logined
@friends_view.route('/index')
def index():
    '''
    获取好友页面
    :return:
    '''

    # https://wx2.qq.com/cgi-bin/mmwebwx-bin/webwxgetcontact?
    url = 'https://wx2.qq.com/cgi-bin/mmwebwx-bin/webwxgetcontact?'
    global wxSession
    global wx_ticket_dict
    res = wxSession.get(url=url,
                        params={
                            'lang': 'zh_CN',
                            'pass_ticket': wx_ticket_dict.get('pass_ticket'),
                            'r': '1542373953292',
                            'seq': 0,
                            'skey': wx_ticket_dict.get('skey')
                        })

    res.encoding = 'utf-8'
    print("friend's coding: %s " % res.encoding)
    friends_msg = json.loads(res.text)
    # 保存ｆｒｉｅｎｄｓ列表
    global wx_friends
    wx_friends.update({ friend.get('UserName'): friend.get('NickName') for friend in friends_msg.get('MemberList')})
    return render_template('friends.html', friends_msg=friends_msg)


