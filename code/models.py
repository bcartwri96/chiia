# this file defines the models that govern our database.
from flask import Flask as fl
from flask_sqlalchemy import SQLAlchemy
import os
import datetime

# app = fl(__name__) #instantiate the app
#
#
# def get_env_variable(name):
#     try:
#         return os.environ[name]
#     except KeyError:
#         message = "Expected environment variable '{}' not set.".format(name)
#         raise Exception(message)
#
# # the values of those depend on your setup
# POSTGRES_URL = get_env_variable("POSTGRES_URL")
# POSTGRES_USER = get_env_variable("POSTGRES_USER")
# POSTGRES_PW = get_env_variable("POSTGRES_PW")
# POSTGRES_DB = get_env_variable("POSTGRES_DB")
# DB_URL = 'postgresql+psycopg2://{user}:{pw}@{url}/{db}'.format(user=POSTGRES_USER,pw=POSTGRES_PW,url=POSTGRES_URL,db=POSTGRES_DB)
#
# app.config['SQLALCHEMY_DATABASE_URI'] = DB_URL
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # silence the deprecation warning

# db = SQLAlchemy(app)

#############################################################
# models
#############################################################
from sqlalchemy import Column, Integer, String, DateTime
import code.database as db

class User(db.Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    date = Column(DateTime, default=datetime.datetime.utcnow)

    def __init__(self, id=None, date=None):
            self.id = id
            self.date = date

    def __repr__(self):
        return '<User %r>' % (self.date)
