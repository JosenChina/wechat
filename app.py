# python3.6
# 模拟登录微信

from flask import Flask
from config import Config
import os
from views import *


def create_app(configName):
    app = Flask(__name__)
    app.config.from_object(Config.get(configName))
    app.register_blueprint(login_view, url_prefix='/login')
    app.register_blueprint(friends_view, url_prefix='/friends')
    app.register_blueprint(send_view, url_prefix="/send-msg")
    app.register_blueprint(receive_view, url_prefix='/receive-msg')
    return app


if __name__ == '__main__':
    app = create_app('default')
    app.run()