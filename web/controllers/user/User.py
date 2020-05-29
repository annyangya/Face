
from common.lib.user.UserService import UserService

from flask import Blueprint ,request, jsonify, make_response, redirect, g
from common.models.User import User
from common.lib.Helper import ops_render
import json
from application import app, db
from common.lib.UrlManager import UrlManager

route_user = Blueprint("user_page", __name__)

@route_user.route("/login",methods=['POST','GET'])
def index():
    if request.method == 'GET':
        return ops_render("user/login.html")

    resp = {'code':'200', 'msg':'登录成功','data':{}}
    req = request.values
    login_name = req['login_name'] if 'login_name' in req else ''
    login_pwd = req['login_pwd'] if 'login_pwd' in req else ''

    #输入有效性前端js可以不判断，但是后端一定要判断，js只是给用户更好的体验
    if login_name is None or len(login_name) < 1:
        resp['code'] = -1
        resp['msg'] = '登录失败'
        return jsonify(resp)

    if login_pwd is None or len(login_pwd) < 1:
        resp['code'] = -1
        resp['msg'] = '请输入正确的密码'
        return jsonify(resp)

    user_info = User.query.filter_by(login_name = login_name).first()
    if not user_info :
        resp['code'] = -1
        resp['msg'] = "请输入正确的用户名和密码！"
        return jsonify(resp)

    if user_info.login_pwd != UserService.genePwd(login_pwd,user_info.login_salt):
        resp['code'] = -1
        resp['msg'] = "请输入正确的用户名和密码！"
        return jsonify(resp)

    #cookie的使用
    responce = make_response(json.dumps(resp))
    responce.set_cookie(app.config['AUTH_COOKIE_NAME'],'%s#%s'%(UserService.geneAuthCode(user_info),user_info.uid))

    return responce

@route_user.route("/edit", methods=['GET','POST'])
def edit():
    if request.method == 'GET':
        return ops_render("user/edit.html",{'current':'edit'})

    resp = {'code':200,'msg':'操作成功','data':{}}
    req = request.values
    nickname = req['nickname'] if 'nickname' in req else ''
    email = req['email'] if 'email' in req else ''
    if nickname is None or len(nickname) < 1:
        resp['code'] = -1
        resp['msg'] = '请输入正确的姓名！'
        return jsonify(resp)
    if email is None or len(email) < 1:
        resp['code'] = -1
        resp['msg'] = '请输入正确的邮箱！'
        return jsonify(resp)

    user_info = g.current_user
    user_info.nickname = nickname
    user_info.email = email

    db.session.add(user_info)
    db.session.commit()
    return jsonify(resp)



@route_user.route("/reset-pwd",methods = ['GET','POST'])
def resetPwd():
    if request.method == 'GET':
        return ops_render("user/reset_pwd.html",{'current':'reset-pwd'})
    resp = {'code': 200, 'msg': '操作成功', 'data': {}}
    req = request.values
    old_password = req['old_password'] if 'old_password' in req else ''
    new_password = req['new_password'] if 'new_password' in req else ''
    if old_password is None or len(old_password) < 6:
        resp['code'] = -1
        resp['msg'] = '请输入符合规范的原密码！'
        return jsonify(resp)
    if new_password is None or len(new_password) < 6:
        resp['code'] = -1
        resp['msg'] = '请输入符合规范的新密码！'
        return jsonify(resp)

    if old_password == new_password :
        resp['code'] = -1
        resp['msg'] = '新旧密码不能相同！'
        return jsonify(resp)
    user_info = g.current_user
    user_info.login_pwd = UserService.genePwd(new_password, user_info.login_salt)

    db.session.add(user_info)
    db.session.commit()

    responce = make_response(json.dumps(resp))
    responce.set_cookie(app.config['AUTH_COOKIE_NAME'], '%s#%s' % (UserService.geneAuthCode(user_info), user_info.uid))
    return responce


@route_user.route("/logout")
def logout():
    response = make_response(redirect(UrlManager.buildUrl("/user/login")))
    response.delete_cookie(app.config['AUTH_COOKIE_NAME'])
    return response