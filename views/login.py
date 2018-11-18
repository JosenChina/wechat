
from . import login_view
from global_val import *
from flask import render_template, jsonify
import time
import re
from bs4 import BeautifulSoup
import json


@login_view.route('/')
def login():
    '''
    前端获取二维码
    :return:
    '''
    global wx_appid
    get_uuid_url = 'https://login.wx2.qq.com/jslogin?'
    res1 = wxSession.get(url=get_uuid_url,
                         params={
                             'appid': wx_appid,
                             'redirect_uri': 'https://wx2.qq.com/cgi-bin/mmwebwx-bin/webwxnewloginpage',
                             'fun': 'new',
                             'lang': 'zh_CN',
                             '_': str(time.time())
                         })
    global wx_uuid
    wx_uuid = re.findall('window.QRLogin.uuid = "(.+)";', res1.text)[0]
    return render_template('wx_login_.html', ImgId = wx_uuid)


@login_view.route('/check')
def check():
    '''
    监听前端是否扫码，若无扫码，则返回４０８，若扫码则返回２０１以及头像的ｂａｓｅ６４编码，点击确定则返回２００
    :return:
    '''
    # https://login.wx2.qq.com/cgi-bin/mmwebwx-bin/login?loginicon=true&uuid=oa5F3nFj5A==&tip=1&r=-473111477&_=1542366370442
    global wxSession
    global wx_tip
    global wx_uuid
    url = 'https://login.wx2.qq.com/cgi-bin/mmwebwx-bin/login?loginicon=true&uuid=%s&tip=%s&r=-473111477&_=%s' % (wx_uuid, wx_tip, str(time.time()))
    res = wxSession.get(url=url)
    if 'window.code=408;' in res.text:
        print('未扫码！！！')
        re_msg = {
            'code': 408
        }
        return jsonify(re_msg)
    elif 'window.code=201' in res.text:
        print('已扫码，未确认！！！')
        wx_tip =  0
        res_msg = {
            'code': 201,
            'avatar': re.findall("window.userAvatar = '(.+)'", res.text)[0]
        }
        return jsonify(res_msg)
    elif 'window.code=200' in res.text:
        print(res.text)
        print('已确认！！！')
        '''
            确认登录后需要配置一些参数
        '''
        # https://wx2.qq.com/cgi-bin/mmwebwx-bin/webwxnewloginpage?ticket=Azh7wVG7KAiQ7_3GtMxY3OQ4@qrticket_0&uuid=AbJlWc_hag==&lang=zh_CN&scan=1542367972&fun=new&version=v2&lang=zh_CN
        re_url = re.findall('window.redirect_uri="(.+)"', res.text)[0]
        url2 = re_url + '&fun=new&version=v2&lang=zh_CN'
        res2 = wxSession.get(url2)
        res2.encoding = 'utf-8'
        soup = BeautifulSoup(res2.text, features='lxml')
        for tag in soup.find('error').children:
            wx_ticket_dict[tag.name] = tag.get_text()
        for k, v in wx_ticket_dict.items():
            print(k, v)
        res_msg = {
            'code': 200
        }
        global wx_ISLOGIN
        wx_ISLOGIN = True
        # 用户个人数据
        # https://wx2.qq.com/cgi-bin/mmwebwx-bin/webwxinit
        url3 = 'https://wx2.qq.com/cgi-bin/mmwebwx-bin/webwxinit?r=-488572751&lang=zh_CN&pass_ticket=%s' % wx_ticket_dict['pass_ticket']
        res3 = wxSession.post(
            url=url3,
            json={
                'BaseRequest':{
                    'DeviceID': 'e965365907039494',
                    'Sid': wx_ticket_dict['wxsid'],
                    'Skey': wx_ticket_dict['skey'],
                    'Uin': wx_ticket_dict['wxuin']
                }
            }
        )
        res3.encoding = 'utf-8'
        USER_INFO = json.loads(res3.text)
        wx_user_info.update(USER_INFO.get('User'))
        # 获取SyncKey
        '''
            Count: 4
            List: [{Key: 1, Val: 624835672}, {Key: 2, Val: 624835873}, {Key: 3, Val: 624835827},…]
        '''
        wx_syncKey.update(USER_INFO.get('SyncKey'))
        return jsonify(res_msg)
    else:
        print('the ELSE')
        print(res.text)
        return jsonify(res.text)




