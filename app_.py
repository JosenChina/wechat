# python3.6
# 模拟登录微信

from flask import Flask, render_template, request
from flask import jsonify
import re
import time
import requests
from bs4 import BeautifulSoup
import json

app = Flask(__name__)

WTIME = None
WIMG_ID = None
Tip = 1
ticket_dict = {}
USER_INFO = {}
USER_FRIENDS = {}
USER_CONTRACT = []
USER_UNREAD_CONTRACT = []
wx_session = None

@app.route('/wx-login')
def hello_world():
    global WTIME
    WTIME = time.time()
    global wx_session
    wx_session = requests.Session()
    resp = wx_session.get('https://login.wx.qq.com/jslogin?appid=wx782c26e4c19acffb&fun=new&lang=zh_CN&_=%s' % WTIME)
    print (resp.text)
    ImgId = re.findall(r'uuid = "(.+)";', resp.text)
    global WIMG_ID
    WIMG_ID = ImgId[0]

    return render_template('wx_login_.html', ImgId = WIMG_ID)


@app.route('/check-login')
def checkLogin():
    global WTIME
    global WIMG_ID
    global Tip
    global wx_session
    ret_json = {
        'code': 408,
        'data': None
    }
    response = wx_session.get('https://login.wx.qq.com/cgi-bin/mmwebwx-bin/login?loginicon=true&uuid=%s&tip=%s&r=419186684&_=%s'\
                            % (WIMG_ID, Tip, WTIME))
    if 'window.code=408' in response.text:
        print('无人扫码')
        return jsonify(ret_json)
    elif 'window.code=201' in response.text:
        ret_json['code'] = 201
        Tip = 0
        avatar = re.findall(r"window.userAvatar = '(.+)';", response.text)[0]
        ret_json['data'] = avatar
        return jsonify(ret_json)
    elif 'window.code=200' in response.text:
        # 用户点击确认登录
        redirect_uri = re.findall(r'window.redirect_uri="(.+)"', response.text)[0]
        redirect_uri = redirect_uri + '&fun=new&version=v2&lang=zh_CN'
        print(response.text)
        #　获取凭证
        response2 = wx_session.get(redirect_uri)
        print(response2.text)
        soup = BeautifulSoup(response2.text, 'lxml')
        for tag in soup.find('error').children:
            ticket_dict[tag.name] = tag.get_text()
        print(ticket_dict)

        # 获取用户信息
        # https://wx2.qq.com/cgi-bin/mmwebwx-bin/webwxinit?r=210623940&lang=zh_CN&pass_ticket=2itOUKahV2mvVBtmwnlpBHIGGNczoWH92hDnuiKBZHflfPdBTDmdmo4JPALFkwOp
        req_data = {
            'BaseRequest': {
                'DeviceID': "e234283477123796",
                'Sid': ticket_dict['wxsid'],
                'Skey': ticket_dict['skey'],
                'Uin': ticket_dict['wxuin']
            }
        }
        response3 = wx_session.post(url='https://wx2.qq.com/cgi-bin/mmwebwx-bin/webwxinit?r=%s&lang=zh_CN&pass_ticket=%s' \
                                  % (time.time(), ticket_dict['pass_ticket']),
                                  json=req_data
                                  )
        response3.encoding = response3.apparent_encoding
        res_json = json.loads(response3.text)
        USER_INFO.update(res_json['User'])
        global USER_CONTRACT
        USER_CONTRACT = res_json['ContactList']
        USER_UNREAD_CONTRACT = res_json['MPSubscribeMsgList']
        # 获取好友列表
        # https://wx2.qq.com/cgi-bin/mmwebwx-bin/webwxgetcontact?r=1541737804790&seq=0&skey=@crypt_763802bb_56cfdf97fd943a4d7347668f20f29378
        response4 = wx_session.get('https://wx2.qq.com/cgi-bin/mmwebwx-bin/webwxgetcontact?r=%s&seq=0&skey=%s' % \
                                 (time.time(), ticket_dict['skey']), json=req_data)
        response4.encoding = 'utf8'
        cont_json = json.loads(response4.text)
        USER_FRIENDS = cont_json['MemberList']
        return render_template('user_.html', user_info=USER_INFO, user_contract=USER_CONTRACT,
                               user_unread_contract=USER_UNREAD_CONTRACT, user_friends=USER_FRIENDS)
    return response.text


if __name__ == '__main__':
    app.run()
