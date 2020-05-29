# coding: utf-8
from sqlalchemy import Column, DateTime, Integer, String, Text
from sqlalchemy.schema import FetchedValue
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()



class Student(db.Model):
    __tablename__ = 'student'

    no = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(10), nullable=False, server_default=db.FetchedValue())
    updated_time = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue())
    face_id = db.Column(db.Text)
    status = db.Column(db.Integer)
    address = db.Column(db.String(100))
