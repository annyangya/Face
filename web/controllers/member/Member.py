# -*- coding: utf-8 -*-
from flask import Blueprint
from common.lib.Helper import ops_render
from common.models.Student import Student
from application import db
import MySQLdb

route_member = Blueprint( 'member_page',__name__ )

@route_member.route( "/index" )
def index():
    student_data = {}
    # query = db.session.query(Student)
    # query.count()
    # list = query.filter_by(Student.status).all()
    list = Student.query.filter(Student.no).all()
    student_data['list']=list
    return ops_render( "member/index.html",student_data)

@route_member.route( "/info" )
def info():
    return ops_render( "member/info.html" )

@route_member.route(("/index2"))
def index2():
    student_data = {}
    list = Student.query.order_by(Student.no).all()
    student_data['list'] = list
    return ops_render("member/index2.html",student_data)



