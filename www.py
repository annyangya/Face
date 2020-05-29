from web.controllers.index import route_index
from web.controllers.user.User import route_user
from application import app
from web.controllers.static import route_static
from web.controllers.account.Account import route_account
from web.controllers.member.Member import route_member
from web.controllers.api import route_api
from web.controllers.face.Face import route_face


'''
拦截器
'''
from web.interceptors.AuthInterceptor import *

'''
蓝图
'''
app.register_blueprint(route_index, url_prefix="/")
app.register_blueprint(route_user, url_prefix="/user")
app.register_blueprint(route_static, url_prefix="/static")
app.register_blueprint(route_account, url_prefix="/account")
app.register_blueprint(route_member, url_prefix="/member")
app.register_blueprint(route_face, url_prefix="/face")
