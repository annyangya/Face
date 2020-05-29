
from flask import Blueprint,render_template,g, jsonify
from common.lib.Helper import ops_render
from common.models.Student import Student
from sqlalchemy import func
route_index = Blueprint('index_page', __name__)

@route_index.route("/")
def index():
    data = {
        "count":0,
        "in":0,
        "out":0
    }
    sum_in = 0
    sum_out = 0
    list = Student.query.order_by(Student.no).all()
    if list:
        data["count"]=len(list)
        for item in list:
            if item.status == 0:
                sum_out += 1
            elif item.status == 1:
                sum_in += 1
        data['in'] = sum_in
        data['out'] = sum_out
    return ops_render("index/index.html",data)

@route_index.route("/board")
def board():
    data = {
    }
    sum_in = 0
    sum_out = 0
    list = Student.query.order_by(Student.no).all()
    if list:
        for item in list:
            if item.status == 0:
                sum_out += 1
            elif item.status == 1:
                sum_in += 1

    resp = {'code':200,'msg':'success','data':{}}
    data = {
        'series': [{
            'type': 'pie',
            'name': 'Browser share',
            data: [
                ['签到', sum_in],
                ['未签到', sum_out]
            ]
        }]
    }
    resp['data'] = data
    return jsonify(resp)