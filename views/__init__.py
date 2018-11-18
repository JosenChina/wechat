
from flask import Blueprint
login_view = Blueprint('login', __name__)
friends_view = Blueprint('friends', __name__)
send_view = Blueprint('send_MSG', __name__)
receive_view = Blueprint('receive_MSG', __name__)

from .login import *
from .friends import *
from .send_msg import *
from .receive_msg import *
