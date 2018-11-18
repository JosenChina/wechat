from functools import wraps
from global_val import wx_ISLOGIN
from flask import abort

def wx_logined(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not wx_ISLOGIN:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function
