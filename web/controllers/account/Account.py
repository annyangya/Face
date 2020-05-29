from flask import Blueprint, request, redirect, jsonify
from common.lib.Helper import ops_render,iPagination, getCurrentDate
from common.models.User import User
from application import app,db
from common.lib.UrlManager import UrlManager
from common.lib.user.UserService import UserService

route_account = Blueprint("account_page", __name__)

@route_account.route("/index")
def index():
    resp_data = {}
    req = request.values
    page= int(req['page']) if ('page' in req and req['page']) else 1
    query = User.query
    query.count()
    page_params = {
        'total':query.count(),
        'page_size':app.config['PAGE_SIZE'],
        'page':page,
        'display':app.config['PAGE_DISPLAY'],
        'url': '/account/index'
    }
    pages = iPagination(page_params)
    offset = (page-1)*app.config['PAGE_SIZE']
    limit = app.config['PAGE_SIZE']*page

    list = query.order_by(User.uid.desc()).all()[offset:limit]
    resp_data['list'] = list
    resp_data['pages'] = pages
    return ops_render("account/index.html",resp_data)

@route_account.route("/info")
def info():
    resp_data ={}
    req = request.args
    uid = int(req.get('id',0))
    reback_url = UrlManager.buildUrl("/account/index")
    if uid < 1:
        return redirect(reback_url)
    info = User.query.filter_by(uid=uid).first()
    if not info :
        return redirect(reback_url)
    resp_data['info'] = info
    return ops_render("account/info.html",resp_data)

@route_account.route("/set",methods = ['POST','GET'])
def set():
    default_pwd = "******"
    if request.method == 'GET':
        resp_data = {}
        req = request.args
        uid = int(req.get('id',0))
        user_info = None
        if uid:
            user_info = User.query.filter_by(uid=uid).first()
        resp_data['user_info'] = user_info
        return ops_render("account/set.html", resp_data)

    resp ={'code':200,'msg':"操作成功",'data':{}}
    req = request.values
    id = req['id'] if 'id'in req else 0
    nickname= req['nickname'] if 'nickname' in req else ""
    mobile = req['mobile'] if 'mobile' in req else ""
    email = req['email'] if 'email' in req else ""
    login_name = req['login_name'] if 'login_name' in req else ""
    login_pwd = req['login_pwd'] if 'login_pwd' in req else ""
    if nickname is None or len(nickname)<2:
        resp['code'] = -1
        resp['msg'] = '请输入符合规范的姓名'
        return jsonify(resp)
    if mobile is None or len(mobile)<2:
        resp['code'] = -1
        resp['msg'] = '请输入符合规范的mobile'
        return jsonify(resp)
    if email is None or len(email)<2:
        resp['code'] = -1
        resp['msg'] = '请输入符合规范的email'
        return jsonify(resp)
    if login_name is None or len(login_name)<2:
        resp['code'] = -1
        resp['msg'] = '请输入符合规范login_name'
        return jsonify(resp)
    if login_pwd is None or len(login_pwd)<6:
        resp['code'] = -1
        resp['msg'] = '请输入符合规范的密码'
        return jsonify(resp)

    has_in = User.query.filter(User.login_name == login_name, User.uid!=id).first()
    if has_in:
        resp['code'] = -1
        resp['msg'] = '登录用户名已存在！'
        return jsonify(resp)
    user_info = User.query.filter_by(uid=id).first()
    if user_info:
        #编辑
        model_user = user_info
    else:
        #新增
        model_user = User()
        model_user.created_time = getCurrentDate()
        model_user.login_salt = UserService.geneSalt()

    model_user.nickname = nickname
    model_user.mobile = mobile
    model_user.email = email
    model_user.login_name = login_name
    if login_pwd != default_pwd:
        model_user.login_pwd = UserService.genePwd(login_pwd,model_user.login_salt)
    model_user.updated_time = getCurrentDate()


    db.session.add(model_user)
    db.session.commit()
    return jsonify(resp)